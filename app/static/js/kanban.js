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
    const select = document.getElementById('addCardColumnSelect');
    if (select) {
        select.value = columnId;
    }
    const form = document.getElementById('addCardForm');
    form.action = "/add_card/" + columnId;
    document.getElementById('modalAddCardTitle').value = '';
    document.getElementById('modalAddCardValor').value = '';
    document.getElementById('modalAddCardConversa').value = '';
    document.getElementById('modalAddCardConversationId').value = '';
    document.getElementById('modalAddCardVendedor').value = currentUserId;
    document.querySelectorAll('#addCardModal [name^="custom_"]').forEach(input => {
        if (input.type === 'checkbox') {
            input.checked = false;
        } else {
            input.value = '';
        }
    });
    new bootstrap.Modal(document.getElementById('addCardModal')).show();
}

function openEditModal(cardDiv) {
    const cardId = cardDiv.getAttribute('data-card-id');
    const title = cardDiv.getAttribute('data-title');
    const valor = cardDiv.getAttribute('data-valor') || '';
    const conversa = cardDiv.getAttribute('data-conversa') || '';
    const conversationId = cardDiv.getAttribute('data-conversation-id') || '';
    const vendedor = cardDiv.getAttribute('data-vendedor-id') || '';
    const customRaw = cardDiv.getAttribute('data-custom') || '{}';
    let customData = {};
    try {
        customData = JSON.parse(customRaw);
    } catch (e) {
        customData = {};
    }

    document.getElementById('modalCardId').value = cardId;
    document.getElementById('modalCardTitle').value = title;
    document.getElementById('modalCardValor').value = valor;
    document.getElementById('modalCardConversa').value = conversa;
    document.getElementById('modalCardConversationId').value = conversationId;
    document.getElementById('modalCardVendedor').value = vendedor;
    document.getElementById('editCardForm').action = "/edit_card/" + cardId;

    // Pre-fill custom field inputs
    document.querySelectorAll('#editCardModal [name^="custom_"]').forEach(input => {
        const key = input.name.replace('custom_', '');
        const val = customData[key];
        if (input.type === 'checkbox') {
            input.checked = Boolean(val);
        } else {
            input.value = val !== undefined && val !== null ? val : '';
        }
    });

    // Handler delete button
    document.getElementById('deleteCardBtn').onclick = function() {
        fetch("/delete_card/" + cardId, {method: "POST"})
        .then(() => location.reload());
    }

    new bootstrap.Modal(document.getElementById('editCardModal')).show();
}

// Drag and Drop com SortableJS
function formatBRL(value) {
    return (value || 0).toLocaleString('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    });
}

function updateColumnStats(columnEl) {
    const cards = columnEl.querySelectorAll('.kanban-card');
    let total = 0;
    cards.forEach(card => {
        total += parseFloat(card.getAttribute('data-valor')) || 0;
    });
    const badge = columnEl.querySelector('.kanban-header .badge');
    if (badge) {
        badge.textContent = `${cards.length} • ${formatBRL(total)}`;
    }
}

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

    const addCardColumnSelect = document.getElementById('addCardColumnSelect');
    const addCardForm = document.getElementById('addCardForm');
    if (addCardColumnSelect && addCardForm) {
        addCardColumnSelect.addEventListener('change', () => {
            addCardForm.action = "/add_card/" + addCardColumnSelect.value;
        });
    }

    const columns = document.querySelectorAll('.kanban-cards');
    columns.forEach(column => {
        new Sortable(column, {
            group: 'kanban',
            animation: 150,
            onAdd: function (evt) {
                // Card foi movido entre colunas
                const cardId = evt.item.getAttribute('data-card-id');
                const newColumn = evt.to.closest('.kanban-column');
                const oldColumn = evt.from.closest('.kanban-column');
                const newColumnId = newColumn.getAttribute('data-column-id');

                fetch("/api/move_card", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({card_id: cardId, column_id: newColumnId})
                }).then(response => {
                    if (!response.ok) {
                        alert("Erro ao mover card!");
                        location.reload();
                    }
                });

                updateColumnStats(newColumn);
                if (oldColumn && oldColumn !== newColumn) {
                    updateColumnStats(oldColumn);
                }
            }
        });
    });
});
