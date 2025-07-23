const currentUserId = document.body.dataset.userId;
function openEditColumnModal(columnId, columnName) {
    document.getElementById('modalColumnId').value = columnId;
    document.getElementById('modalColumnName').value = columnName;
    document.getElementById('editColumnForm').action = "/edit_column/" + columnId;

    document.getElementById('deleteColumnBtn').onclick = function() {
        fetch("/delete_column/" + columnId, {method: "POST"})
        .then(() => location.reload());
    };

    new bootstrap.Modal(document.getElementById('editColumnModal')).show();
}

function openAddCardModal(columnId) {
    document.getElementById('modalAddCardColumnId').value = columnId;
    document.getElementById('addCardForm').action = "/add_card/" + columnId;
    document.getElementById('modalAddCardTitle').value = '';
    document.getElementById('modalAddCardValor').value = '';
    document.getElementById('modalAddCardVendedor').value = currentUserId;
    new bootstrap.Modal(document.getElementById('addCardModal')).show();
}

function openEditModal(cardDiv) {
    const cardId = cardDiv.getAttribute('data-card-id');
    const title = cardDiv.getAttribute('data-title');
    const valor = cardDiv.getAttribute('data-valor') || '';
    const vendedor = cardDiv.getAttribute('data-vendedor-id') || '';

    document.getElementById('modalCardId').value = cardId;
    document.getElementById('modalCardTitle').value = title;
    document.getElementById('modalCardValor').value = valor;
    document.getElementById('modalCardVendedor').value = vendedor;
    document.getElementById('editCardForm').action = "/edit_card/" + cardId;

    // Handler delete button
    document.getElementById('deleteCardBtn').onclick = function() {
        fetch("/delete_card/" + cardId, {method: "POST"})
        .then(() => location.reload());
    }

    new bootstrap.Modal(document.getElementById('editCardModal')).show();
}

// Drag and Drop com SortableJS
document.addEventListener('DOMContentLoaded', () => {
    const toggleForm = document.getElementById('toggleThemeForm');
    if (toggleForm) {
        toggleForm.addEventListener('submit', (e) => {
            e.preventDefault();
            fetch(toggleForm.action, {method: 'POST'})
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        document.body.classList.toggle('dark-mode', data.dark_mode);
                        const icon = toggleForm.querySelector('i');
                        if (icon) {
                            icon.classList.toggle('fa-sun', data.dark_mode);
                            icon.classList.toggle('fa-moon', !data.dark_mode);
                        }
                    } else {
                        location.reload();
                    }
                })
                .catch(() => location.reload());
        });
    }

    const columns = document.querySelectorAll('.kanban-cards');
    columns.forEach(column => {
        new Sortable(column, {
            group: 'kanban',
            animation: 150,
            onAdd: function (evt) {
                // Card foi movido
                const cardId = evt.item.getAttribute('data-card-id');
                const newColumnId = evt.to.closest('.kanban-column').getAttribute('data-column-id');
                fetch("/api/move_card", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({card_id: cardId, column_id: newColumnId})
                }).then(response => {
                    if (!response.ok) alert("Erro ao mover card!");
                });
            }
        });
    });
});
