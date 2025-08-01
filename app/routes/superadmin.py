import os
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    abort,
    g,
)
import json
from ..models import db, Empresa, Usuario, Column, Panel


class CustomFieldError(ValueError):
    """Raised when custom field definitions are invalid."""


def parse_custom_fields(raw):
    """Validate and normalize custom field definitions.

    Parameters
    ----------
    raw: str
        JSON string describing the custom fields.

    Returns
    -------
    list[dict]
        Normalized list of custom field definitions.

    Raises
    ------
    CustomFieldError
        If the JSON is invalid or any field definition is incorrect.
    """
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise CustomFieldError("Invalid JSON for custom fields") from exc

    if not isinstance(data, list):
        raise CustomFieldError("Custom fields must be a list")

    if len(data) > 8:
        raise CustomFieldError("At most 8 custom fields are allowed")

    allowed = {"text", "number", "boolean", "select"}
    result = []
    for idx, item in enumerate(data, start=1):
        if not isinstance(item, dict):
            raise CustomFieldError(f"Field #{idx} must be an object")
        name = item.get("name")
        ftype = item.get("type")
        if not name or not ftype:
            raise CustomFieldError(f"Field #{idx} must contain 'name' and 'type'")
        if ftype not in allowed:
            raise CustomFieldError(f"Invalid type '{ftype}' for field '{name}'")

        entry = {"name": name, "type": ftype}
        if ftype == "select":
            opts = item.get("options")
            if not isinstance(opts, list) or len(opts) == 0:
                raise CustomFieldError(
                    f"Select field '{name}' requires a non-empty 'options' list"
                )
            if not all(isinstance(o, str) for o in opts):
                raise CustomFieldError(f"All options for '{name}' must be strings")
            entry["options"] = opts
        result.append(entry)

    return result


superadmin_bp = Blueprint("superadmin", __name__, url_prefix="/superadmin")


def _require_token():
    required = os.environ.get("SUPERADMIN_TOKEN")
    token = request.args.get("token") or session.get("superadmin_token")
    if not required or token != required:
        abort(403)
    session["superadmin_token"] = token


@superadmin_bp.before_request
def check_superadmin_token():
    # Allow super-admin role to access without token
    if g.get("user") and g.user.role == "superadmin":
        return
    _require_token()


def redirect_next(default_endpoint):
    """Redirect to ``next`` parameter if present else to default endpoint."""
    next_url = request.form.get("next") or request.args.get("next")
    if next_url:
        return redirect(next_url)
    return redirect(url_for(default_endpoint, token=session.get("superadmin_token")))


def add_user_to_panels(usuario):
    """Attach usuario to panels based on role and company."""
    if usuario.role == "superadmin":
        panels = Panel.query.all()
    elif usuario.role == "gestor":
        panels = Panel.query.filter_by(empresa_id=usuario.empresa_id).all()
    else:
        panels = []
    for p in panels:
        if usuario not in p.usuarios:
            p.usuarios.append(usuario)
    db.session.commit()


@superadmin_bp.route("/")
def dashboard():
    empresas = Empresa.query.all()
    return render_template("superadmin/dashboard.html", empresas=empresas)


@superadmin_bp.route("/empresa/<int:empresa_id>")
def empresa_detail(empresa_id):
    empresa = Empresa.query.get_or_404(empresa_id)
    vendedores = Usuario.query.filter_by(empresa_id=empresa_id).all()
    columns = Column.query.join(Panel).filter(Panel.empresa_id == empresa_id).all()
    panels = Panel.query.filter_by(empresa_id=empresa_id).all()
    return render_template(
        "superadmin/empresa_detail.html",
        empresa=empresa,
        vendedores=vendedores,
        columns=columns,
        panels=panels,
    )


@superadmin_bp.route("/create_empresa", methods=["GET", "POST"])
def create_empresa():
    if request.method == "POST":
        nome = request.form["nome"]
        account_id = request.form["account_id"]
        dark_mode = bool(request.form.get("dark_mode"))
        # Campos customizáveis em JSON (até 8 definições)
        raw = request.form.get("custom_fields", "[]")
        try:
            cf = parse_custom_fields(raw)
        except CustomFieldError as e:
            return str(e), 400
        empresa = Empresa(
            nome=nome,
            account_id=account_id,
            custom_fields=cf,
            dark_mode=dark_mode,
        )
        db.session.add(empresa)
        db.session.commit()
        return redirect_next("superadmin.dashboard")
    return render_template("superadmin/create_empresa.html")


@superadmin_bp.route("/edit_empresa/<int:empresa_id>", methods=["GET", "POST"])
def edit_empresa(empresa_id):
    empresa = Empresa.query.get_or_404(empresa_id)
    if request.method == "POST":
        empresa.nome = request.form["nome"]
        empresa.account_id = request.form["account_id"]
        empresa.dark_mode = bool(request.form.get("dark_mode"))
        # Atualiza campos customizáveis JSON
        raw = request.form.get("custom_fields", "[]")
        try:
            empresa.custom_fields = parse_custom_fields(raw)
        except CustomFieldError as e:
            return str(e), 400
        db.session.commit()
        return redirect_next("superadmin.dashboard")
    return render_template("superadmin/edit_empresa.html", empresa=empresa)


@superadmin_bp.route("/delete_empresa/<int:empresa_id>", methods=["POST"])
def delete_empresa(empresa_id):
    empresa = Empresa.query.get_or_404(empresa_id)
    db.session.delete(empresa)
    db.session.commit()
    return redirect_next("superadmin.dashboard")


@superadmin_bp.route("/create_vendedor", methods=["GET", "POST"])
def create_vendedor():
    empresas = Empresa.query.all()
    if request.method == "POST":
        usuario = Usuario(
            user_id=request.form["user_id"],
            user_email=request.form["user_email"],
            user_name=request.form["user_name"],
            role=request.form["role"],
            empresa_id=int(request.form["empresa_id"]),
        )
        db.session.add(usuario)
        db.session.commit()

        panel_ids = [int(pid) for pid in request.form.getlist("panel_ids")]
        if panel_ids:
            panels = Panel.query.filter(Panel.id.in_(panel_ids)).all()
            for p in panels:
                if usuario not in p.usuarios:
                    p.usuarios.append(usuario)

        add_user_to_panels(usuario)
        db.session.commit()
        return redirect_next("superadmin.dashboard")

    empresa_id = request.args.get("empresa_id", type=int)
    if not empresa_id and empresas:
        empresa_id = empresas[0].id

    panels = []
    if empresa_id:
        panels = Panel.query.filter_by(empresa_id=empresa_id).all()

    return render_template(
        "superadmin/create_vendedor.html",
        empresas=empresas,
        panels=panels,
    )


@superadmin_bp.route("/edit_vendedor/<int:vendedor_id>", methods=["GET", "POST"])
def edit_vendedor(vendedor_id):
    usuario = Usuario.query.get_or_404(vendedor_id)
    empresas = Empresa.query.all()
    if request.method == "POST":
        usuario.user_id = request.form["user_id"]
        usuario.user_email = request.form["user_email"]
        usuario.user_name = request.form["user_name"]
        usuario.role = request.form["role"]
        usuario.empresa_id = int(request.form["empresa_id"])
        db.session.commit()
        add_user_to_panels(usuario)
        db.session.commit()
        return redirect_next("superadmin.dashboard")
    return render_template(
        "superadmin/edit_vendedor.html", usuario=usuario, empresas=empresas
    )


@superadmin_bp.route("/delete_vendedor/<int:vendedor_id>", methods=["POST"])
def delete_vendedor(vendedor_id):
    usuario = Usuario.query.get_or_404(vendedor_id)
    db.session.delete(usuario)
    db.session.commit()
    return redirect_next("superadmin.dashboard")
