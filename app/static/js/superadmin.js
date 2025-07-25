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
            const empresaId = button.getAttribute('data-empresa');
            const form = editColumnModal.querySelector('form');
            form.action = `/superadmin/edit_column/${id}`;
            form.querySelector('input[name="name"]').value = name;
            fillSelectOptions(form.querySelector('select[name="empresa_id"]'), null, empresaId);
        });
    }

    const createColumnModal = document.getElementById('createColumnModal');
    if (createColumnModal) {
        createColumnModal.addEventListener('show.bs.modal', event => {
            const button = event.relatedTarget;
            const empresaId = button.getAttribute('data-empresa');
            fillSelectOptions(createColumnModal.querySelector('select[name="empresa_id"]'), null, empresaId);
        });
    }
});
