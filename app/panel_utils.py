from .models import Usuario, Panel


def add_default_panel_users(panel: Panel) -> None:
    """Add superadmins and gestores of the panel's empresa to the panel."""
    if panel is None:
        return
    # Superadmins
    superadmins = Usuario.query.filter_by(role="superadmin").all()
    gestores = Usuario.query.filter_by(role="gestor", empresa_id=panel.empresa_id).all()
    for user in [*superadmins, *gestores]:
        if user not in panel.usuarios:
            panel.usuarios.append(user)

