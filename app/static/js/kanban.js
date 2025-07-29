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

function openAddColumnModal() {
    const panelSelect = document.getElementById('panelSelect');
    const panelId = panelSelect ? panelSelect.value : '';
    const form = document.getElementById('addColumnForm');
    if (form) {
        form.querySelector('input[name="panel_id"]').value = panelId;
        form.querySelector('input[name="name"]').value = '';
    }
    new bootstrap.Modal(document.getElementById('addColumnModal')).show();
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

    const panelSelect = document.getElementById('panelSelect');
    const addColumnForm = document.getElementById('addColumnForm');
    if (panelSelect && addColumnForm) {
        panelSelect.addEventListener('change', () => {
            addColumnForm.querySelector('input[name="panel_id"]').value = panelSelect.value;
        });
    }

    const boardWrapper = document.querySelector('.kanban-board-wrapper');
    const topScroll = document.getElementById('kanbanTopScroll');
    if (boardWrapper && topScroll) {
        const inner = topScroll.firstElementChild;
        const syncWidth = () => {
            inner.style.width = boardWrapper.scrollWidth + 'px';
        };
        syncWidth();
        topScroll.addEventListener('scroll', () => {
            boardWrapper.scrollLeft = topScroll.scrollLeft;
        });
        boardWrapper.addEventListener('scroll', () => {
            topScroll.scrollLeft = boardWrapper.scrollLeft;
        });
        new ResizeObserver(syncWidth).observe(boardWrapper);
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

    function createCardEl(card) {
        const div = document.createElement('div');
        div.className = 'kanban-card';
        div.setAttribute('draggable', 'true');
        div.dataset.cardId = card.id;
        div.dataset.title = card.title;
        div.dataset.valor = card.valor_negociado || '';
        div.dataset.conversa = card.conversa || '';
        div.dataset.conversationId = card.conversation_id || '';
        div.dataset.vendedorId = card.vendedor_id || '';
        div.dataset.columnId = card.column_id;
        div.dataset.custom = JSON.stringify(card.custom_data || {});
        div.onclick = () => openEditModal(div);
        const titleDiv = document.createElement('div');
        titleDiv.className = 'card-title';
        titleDiv.textContent = card.title;
        div.appendChild(titleDiv);
        const descDiv = document.createElement('div');
        descDiv.className = 'card-desc';
        descDiv.textContent = `${formatBRL(card.valor_negociado)} - ${card.vendedor_name || ''}`;
        if (card.conversa) {
            const link = document.createElement('a');
            link.href = card.conversa;
            link.target = '_blank';
            link.className = 'text-decoration-none eye-link';
            link.innerHTML = '<i class="fa-solid fa-eye text-primary"></i>';
            descDiv.appendChild(link);
        }
        div.appendChild(descDiv);
        return div;
    }

    function addCard(card) {
        const columnDiv = document.querySelector(`#column-${card.column_id}`);
        if (!columnDiv) return;
        const cardEl = createCardEl(card);
        columnDiv.appendChild(cardEl);
        updateColumnStats(columnDiv.closest('.kanban-column'));
    }

    function updateCard(card) {
        const existing = document.querySelector(`.kanban-card[data-card-id='${card.id}']`);
        if (!existing) {
            addCard(card);
            return;
        }
        const oldColumn = existing.dataset.columnId;
        existing.dataset.title = card.title;
        existing.dataset.valor = card.valor_negociado || '';
        existing.dataset.conversa = card.conversa || '';
        existing.dataset.conversationId = card.conversation_id || '';
        existing.dataset.vendedorId = card.vendedor_id || '';
        existing.dataset.columnId = card.column_id;
        existing.dataset.custom = JSON.stringify(card.custom_data || {});
        existing.querySelector('.card-title').textContent = card.title;
        existing.querySelector('.card-desc').textContent = `${formatBRL(card.valor_negociado)} - ${card.vendedor_name || ''}`;
        if (card.conversa) {
            const link = document.createElement('a');
            link.href = card.conversa;
            link.target = '_blank';
            link.className = 'text-decoration-none eye-link';
            link.innerHTML = '<i class="fa-solid fa-eye text-primary"></i>';
            existing.querySelector('.card-desc').appendChild(link);
        }
        if (oldColumn != card.column_id) {
            const columnDiv = document.querySelector(`#column-${card.column_id}`);
            if (columnDiv) columnDiv.appendChild(existing);
            updateColumnStats(document.querySelector(`.kanban-column[data-column-id='${oldColumn}']`));
        }
        updateColumnStats(document.querySelector(`.kanban-column[data-column-id='${card.column_id}']`));
    }

    function removeCard(cardId) {
        const el = document.querySelector(`.kanban-card[data-card-id='${cardId}']`);
        if (el) {
            const column = el.closest('.kanban-column');
            el.remove();
            updateColumnStats(column);
        }
    }

    function handleEvent(evt) {
        switch (evt.type) {
            case 'card_created':
                addCard(evt.card);
                break;
            case 'card_updated':
            case 'card_moved':
                updateCard(evt.card);
                break;
            case 'card_deleted':
                removeCard(evt.card_id);
                break;
            case 'column_created':
            case 'column_updated':
            case 'column_deleted':
            case 'panel_created':
            case 'panel_updated':
            case 'panel_deleted':
                location.reload();
                break;
        }
    }

    const evtSource = new EventSource('/events');
    evtSource.onmessage = (e) => {
        try {
            const data = JSON.parse(e.data);
            handleEvent(data);
        } catch (_) {}
    };
});
