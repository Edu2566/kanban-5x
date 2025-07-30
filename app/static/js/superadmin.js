// Superadmin panel modal logic

function fillSelectOptions(select, options, selected) {
    if (!select) return;
    select.querySelectorAll('option').forEach(o => {
        if (o.value == selected) {
            o.selected = true;
        } else {
            o.selected = false;
        }
    });
}

document.addEventListener('DOMContentLoaded', () => {
    const editEmpresaModal = document.getElementById('editEmpresaModal');
    if (editEmpresaModal) {
        editEmpresaModal.addEventListener('show.bs.modal', event => {
            const button = event.relatedTarget;
            const id = button.getAttribute('data-id');
            const nome = button.getAttribute('data-nome');
            const account = button.getAttribute('data-account');
            const dark = button.getAttribute('data-dark') === '1';
            const custom = button.getAttribute('data-custom') || '[]';
            const form = editEmpresaModal.querySelector('form');
            form.action = `/superadmin/edit_empresa/${id}`;
            form.querySelector('input[name="nome"]').value = nome;
            form.querySelector('input[name="account_id"]').value = account;
            form.querySelector('input[name="dark_mode"]').checked = dark;
            form.querySelector('textarea[name="custom_fields"]').value = custom;
        });
    }

    const editVendedorModal = document.getElementById('editVendedorModal');
    if (editVendedorModal) {
        editVendedorModal.addEventListener('show.bs.modal', event => {
            const button = event.relatedTarget;
            const id = button.getAttribute('data-id');
            const userId = button.getAttribute('data-user');
            const email = button.getAttribute('data-email');
            const name = button.getAttribute('data-name');
            const empresaId = button.getAttribute('data-empresa');
            const role = button.getAttribute('data-role');
            const form = editVendedorModal.querySelector('form');
            form.action = `/superadmin/edit_vendedor/${id}`;
            form.querySelector('input[name="user_id"]').value = userId;
            form.querySelector('input[name="user_email"]').value = email;
            form.querySelector('input[name="user_name"]').value = name;
            fillSelectOptions(form.querySelector('select[name="empresa_id"]'), null, empresaId);
            fillSelectOptions(form.querySelector('select[name="role"]'), null, role);
        });
    }

    const createVendedorModal = document.getElementById('createVendedorModal');
    if (createVendedorModal) {
        createVendedorModal.addEventListener('show.bs.modal', event => {
            const button = event.relatedTarget;
            const empresaId = button.getAttribute('data-empresa');
            fillSelectOptions(createVendedorModal.querySelector('select[name="empresa_id"]'), null, empresaId);
        });
    }

    const editColumnModal = document.getElementById('editColumnModalSuper');
    if (editColumnModal) {
        editColumnModal.addEventListener('show.bs.modal', event => {
            const button = event.relatedTarget;
            const id = button.getAttribute('data-id');
            const name = button.getAttribute('data-name');
            const color = button.getAttribute('data-color') || '#000000';
            const form = editColumnModal.querySelector('form');
            form.action = `/superadmin/edit_column/${id}`;
            form.querySelector('input[name="name"]').value = name;
            const colorInput = form.querySelector('input[name="color"]');
            if (colorInput) colorInput.value = color;
        });
    }

    const createColumnModal = document.getElementById('createColumnModal');
    if (createColumnModal) {
        const form = createColumnModal.querySelector('form');
        const select = createColumnModal.querySelector('select[name="panel_id"]');
        const token = form ? form.dataset.token : '';
        const match = form ? form.action.match(/[?&]next=([^&]+)/) : null;
        const nextParam = match ? decodeURIComponent(match[1]) : '';

        function updateCreateColumnAction() {
            if (!form || !select) return;
            const panelId = select.value;
            const params = new URLSearchParams();
            if (token) params.set('token', token);
            if (nextParam) params.set('next', nextParam);
            form.action = `/superadmin/create_column/${panelId}?${params.toString()}`;
        }

        createColumnModal.addEventListener('show.bs.modal', () => {
            const colorInput = createColumnModal.querySelector('input[name="color"]');
            if (colorInput) colorInput.value = '#000000';
            updateCreateColumnAction();
        });

        if (select) {
            select.addEventListener('change', updateCreateColumnAction);
        }
    }

    const createColumnBtn = document.getElementById('createColumnBtn');
    if (createColumnBtn) {
        createColumnBtn.addEventListener('click', function(event) {
            if (this.dataset.hasPanels === '0') {
                event.preventDefault();
                event.stopImmediatePropagation();
                const modalEl = document.getElementById('noPanelModal');
                if (modalEl) {
                    const m = new bootstrap.Modal(modalEl);
                    m.show();
                }
            }
        });
    }
});
