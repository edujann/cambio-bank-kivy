(function () {
    // ── Estilos ──────────────────────────────────────────────────────────────
    const css = `
#cs-backdrop {
    display: none;
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,0.6);
    z-index: 99998;
    backdrop-filter: blur(2px);
}
#cs-panel {
    position: fixed;
    top: 18%;
    left: 50%;
    transform: translateX(-50%);
    width: min(520px, 92vw);
    background: #1e2533;
    border: 1px solid #1a5fb4;
    border-radius: 10px;
    box-shadow: 0 8px 40px rgba(0,0,0,0.6);
    z-index: 99999;
    overflow: hidden;
    font-family: inherit;
}
#cs-header {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 14px 18px 10px;
    border-bottom: 1px solid rgba(255,255,255,0.07);
    color: #aaa;
    font-size: 12px;
    letter-spacing: 0.5px;
}
#cs-header i { color: #1a5fb4; font-size: 15px; }
#cs-input-wrap {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 14px 18px;
    border-bottom: 1px solid rgba(255,255,255,0.07);
}
#cs-input {
    flex: 1;
    background: transparent;
    border: none;
    outline: none;
    color: #eee;
    font-size: 18px;
    font-family: monospace;
    caret-color: #1a5fb4;
}
#cs-input::placeholder { color: #555; }
#cs-btn {
    background: #1a5fb4;
    color: #fff;
    border: none;
    border-radius: 6px;
    padding: 7px 16px;
    font-size: 13px;
    cursor: pointer;
    white-space: nowrap;
}
#cs-btn:hover { background: #1c71d8; }
#cs-result {
    min-height: 60px;
    max-height: 320px;
    overflow-y: auto;
    padding: 14px 18px;
}
.cs-card {
    background: rgba(26,95,180,0.08);
    border: 1px solid rgba(26,95,180,0.25);
    border-radius: 8px;
    padding: 14px 16px;
    margin-bottom: 10px;
}
.cs-card:last-child { margin-bottom: 0; }
.cs-origem {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 10px;
    padding: 3px 8px;
    border-radius: 20px;
    display: inline-block;
}
.cs-origem.cliente { background: rgba(46,194,126,0.15); color: #2ec27e; }
.cs-origem.empresa { background: rgba(249,197,26,0.15); color: #f9c51a; }
.cs-row {
    display: flex;
    gap: 8px;
    font-size: 13px;
    margin-bottom: 6px;
    align-items: baseline;
}
.cs-row:last-child { margin-bottom: 0; }
.cs-label {
    min-width: 130px;
    color: #888;
    font-weight: 600;
    flex-shrink: 0;
}
.cs-val { color: #eee; word-break: break-all; }
.cs-val strong { color: #fff; font-size: 15px; }
.cs-val.mono { font-family: monospace; font-size: 12px; color: #aaa; }
.cs-ativa-sim { color: #2ec27e; }
.cs-ativa-nao { color: #e01b24; }
#cs-msg {
    text-align: center;
    color: #aaa;
    font-size: 14px;
    padding: 10px 0;
}
#cs-msg.erro { color: #e74c3c; }
#cs-footer {
    padding: 8px 18px;
    border-top: 1px solid rgba(255,255,255,0.05);
    display: flex;
    gap: 16px;
    font-size: 11px;
    color: #555;
}
#cs-footer kbd {
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 3px;
    padding: 1px 5px;
    font-size: 11px;
    color: #aaa;
}
`;

    const styleEl = document.createElement('style');
    styleEl.textContent = css;
    document.head.appendChild(styleEl);

    // ── HTML ─────────────────────────────────────────────────────────────────
    const backdropEl = document.createElement('div');
    backdropEl.id = 'cs-backdrop';

    const panelEl = document.createElement('div');
    panelEl.id = 'cs-panel';
    panelEl.innerHTML = `
        <div id="cs-header"><i class="fas fa-search"></i> BUSCAR CONTA</div>
        <div id="cs-input-wrap">
            <input id="cs-input" type="text" placeholder="Digite o ID da conta..." autocomplete="off" spellcheck="false">
            <button id="cs-btn">Buscar</button>
        </div>
        <div id="cs-result"><div id="cs-msg">Digite o ID e pressione Enter ou clique em Buscar.</div></div>
        <div id="cs-footer">
            <span><kbd>Enter</kbd> buscar</span>
            <span><kbd>Esc</kbd> fechar</span>
            <span><kbd>Ctrl+K</kbd> abrir/fechar</span>
        </div>
    `;

    document.body.appendChild(backdropEl);
    document.body.appendChild(panelEl);

    // ── Lógica ────────────────────────────────────────────────────────────────
    const input  = document.getElementById('cs-input');
    const result = document.getElementById('cs-result');
    const msg    = document.getElementById('cs-msg');

    function open() {
        backdropEl.style.display = 'block';
        panelEl.style.display    = 'block';
        input.focus();
        input.select();
    }

    function close() {
        backdropEl.style.display = 'none';
        panelEl.style.display    = 'none';
    }

    function fmtSaldo(v, moeda) {
        if (v == null) return 'N/A';
        return parseFloat(v).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + ' ' + (moeda || '');
    }

    async function buscar() {
        const id = input.value.trim();
        if (!id) return;

        result.innerHTML = '<div id="cs-msg"><i class="fas fa-spinner fa-spin"></i> Buscando...</div>';

        try {
            const res  = await fetch('/api/admin/conta/lookup', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id })
            });
            const data = await res.json();

            if (!data.success) {
                result.innerHTML = `<div id="cs-msg erro" style="color:#e74c3c;text-align:center;padding:10px 0;">${data.message}</div>`;
                return;
            }

            result.innerHTML = data.resultados.map(r => {
                if (r.origem === 'cliente') {
                    const ativaHtml = r.ativa === false
                        ? '<span class="cs-ativa-nao">Inativa</span>'
                        : '<span class="cs-ativa-sim">Ativa</span>';
                    return `
                        <div class="cs-card">
                            <span class="cs-origem cliente">Conta Cliente</span>
                            <div class="cs-row"><span class="cs-label">ID da Conta:</span><span class="cs-val mono">${r.id}</span></div>
                            <div class="cs-row"><span class="cs-label">Cliente:</span><span class="cs-val"><strong>${r.cliente_nome || 'N/A'}</strong></span></div>
                            <div class="cs-row"><span class="cs-label">Username:</span><span class="cs-val">${r.cliente_username || 'N/A'}</span></div>
                            <div class="cs-row"><span class="cs-label">Moeda:</span><span class="cs-val">${r.moeda || 'N/A'}</span></div>
                            <div class="cs-row"><span class="cs-label">Saldo:</span><span class="cs-val">${fmtSaldo(r.saldo, r.moeda)}</span></div>
                            <div class="cs-row"><span class="cs-label">Status:</span><span class="cs-val">${ativaHtml}</span></div>
                        </div>`;
                } else {
                    return `
                        <div class="cs-card">
                            <span class="cs-origem empresa">Conta Empresa</span>
                            <div class="cs-row"><span class="cs-label">Número:</span><span class="cs-val mono">${r.id}</span></div>
                            <div class="cs-row"><span class="cs-label">Nome:</span><span class="cs-val"><strong>${r.nome || 'N/A'}</strong></span></div>
                            <div class="cs-row"><span class="cs-label">Moeda:</span><span class="cs-val">${r.moeda || 'N/A'}</span></div>
                            <div class="cs-row"><span class="cs-label">Saldo:</span><span class="cs-val">${fmtSaldo(r.saldo, r.moeda)}</span></div>
                        </div>`;
                }
            }).join('');

        } catch (err) {
            result.innerHTML = `<div id="cs-msg" style="color:#e74c3c;text-align:center;padding:10px 0;">Erro: ${err.message}</div>`;
        }
    }

    // ── Eventos ───────────────────────────────────────────────────────────────
    document.getElementById('cs-btn').addEventListener('click', buscar);
    input.addEventListener('keydown', e => { if (e.key === 'Enter') buscar(); });
    backdropEl.addEventListener('click', close);

    document.addEventListener('keydown', e => {
        if (e.ctrlKey && e.key === 'k') {
            e.preventDefault();
            panelEl.style.display === 'none' ? open() : close();
        }
        if (e.key === 'Escape') close();
    });
})();
