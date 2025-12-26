
// ===========================================
// FUNCIONALIDADES DA TELA DE TRANSFERÊNCIA
// ===========================================

let selectedFile = null;
let userContas = [];

// GARANTIR que userContas seja global
window.userContas = window.userContas || [];

// ============================================
// FUNÇÃO: POPUP DE SUCESSO VERDE FINANCEIRO
// Substitua a função atual "garantirPopupSucesso"
// ============================================

function garantirPopupSucesso(transferenciaId, valor, moeda) {
    console.log('🎉🎉🎉 GARANTIRPOPUPSUCESSO CHAMADA! 🎉🎉🎉');
    console.log('Transferencia ID:', transferenciaId);
    console.log('Valor:', valor);
    console.log('Moeda:', moeda);
    console.log('🎉 TRANSFERÊNCIA BEM-SUCEDIDA:', transferenciaId);
    
    // Remover qualquer popup anterior
    const popupAntigo = document.getElementById('elegantSuccessPopup');
    if (popupAntigo) popupAntigo.remove();
    document.querySelectorAll('.popup-overlay').forEach(el => el.remove());
    
    // Criar overlay escuro
    const overlay = document.createElement('div');
    overlay.className = 'popup-overlay';
    overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.7);
        z-index: 99998;
        animation: fadeInOverlay 0.3s ease;
    `;
    
    // Criar popup elegante VERDE
    const popup = document.createElement('div');
    popup.id = 'elegantSuccessPopup';
    popup.style.cssText = `
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: linear-gradient(135deg, #059669 0%, #047857 100%);
        color: white;
        padding: 40px;
        border-radius: 20px;
        box-shadow: 0 25px 80px rgba(5, 150, 105, 0.4);
        z-index: 99999;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        width: 90%;
        max-width: 500px;
        text-align: center;
        animation: popupSlideIn 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
        border: 1px solid rgba(255, 255, 255, 0.3);
    `;
    
    popup.innerHTML = `
        <div style="
            font-size: 70px;
            margin-bottom: 20px;
            animation: iconBounce 1s infinite alternate;
            filter: drop-shadow(0 5px 10px rgba(0,0,0,0.2));
        ">✅</div>
        
        <h2 style="
            margin: 0 0 15px 0;
            font-size: 32px;
            font-weight: 700;
            letter-spacing: -0.5px;
            text-shadow: 0 2px 4px rgba(0,0,0,0.2);
        ">Transferência Concluída!</h2>
        
        <p style="
            margin: 0 0 30px 0;
            font-size: 17px;
            opacity: 0.95;
            line-height: 1.5;
            font-weight: 400;
        ">Sua transferência internacional foi<br>solicitada com sucesso e está em processamento.</p>
        
        <div style="
            background: rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 25px;
            margin: 25px 0;
            text-align: left;
            border: 1px solid rgba(255, 255, 255, 0.2);
        ">
            <div style="display: flex; justify-content: space-between; margin-bottom: 15px; align-items: center;">
                <span style="opacity: 0.9; font-size: 15px;">ID da Transferência:</span>
                <strong style="font-size: 20px; letter-spacing: 1px;">${transferenciaId}</strong>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="opacity: 0.9; font-size: 15px;">Valor Transferido:</span>
                <strong style="font-size: 28px; color: #a7f3d0; font-weight: 800;">
                    ${parseFloat(valor).toFixed(2)} ${moeda}
                </strong>
            </div>
        </div>
        
        <div style="
            display: flex;
            gap: 15px;
            margin-top: 30px;
            justify-content: center;
        ">
            <button id="fecharPopupBtn" style="
                background: rgba(255, 255, 255, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.3);
                color: white;
                padding: 15px 35px;
                border-radius: 50px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s;
                flex: 1;
                min-width: 140px;
            ">Fechar</button>
            
            <button id="verTransferenciaBtn" style="
                background: white;
                color: #059669;
                border: none;
                padding: 15px 35px;
                border-radius: 50px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s;
                flex: 1;
                min-width: 140px;
                box-shadow: 0 5px 15px rgba(255, 255, 255, 0.1);
            ">Ver Detalhes</button>
        </div>
        
        <div style="
            margin-top: 25px;
            font-size: 14px;
            opacity: 0.8;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        ">
            <span style="display: inline-block; width: 10px; height: 10px; background: #a7f3d0; border-radius: 50%; animation: pulse 2s infinite;"></span>
            Status: <strong>Em processamento</strong>
        </div>
    `;
    
    // Adicionar estilos de animação
    const style = document.createElement('style');
    style.textContent = `
        @keyframes popupSlideIn {
            0% {
                opacity: 0;
                transform: translate(-50%, -50%) scale(0.8) translateY(30px);
            }
            100% {
                opacity: 1;
                transform: translate(-50%, -50%) scale(1);
            }
        }
        
        @keyframes fadeInOverlay {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        @keyframes iconBounce {
            from { transform: translateY(0); }
            to { transform: translateY(-10px); }
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        #fecharPopupBtn:hover {
            background: rgba(255, 255, 255, 0.3) !important;
            transform: translateY(-3px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }
        
        #verTransferenciaBtn:hover {
            background: #f0fdf4 !important;
            transform: translateY(-3px);
            box-shadow: 0 8px 20px rgba(255, 255, 255, 0.2);
        }
    `;
    document.head.appendChild(style);
    
    // Adicionar ao body
    document.body.appendChild(overlay);
    document.body.appendChild(popup);
    
    // Event listeners para os botões
    document.getElementById('fecharPopupBtn').onclick = function() {
        fecharPopupElegante();
    };
    
    document.getElementById('verTransferenciaBtn').onclick = function() {
        fecharPopupElegante();
        // Redirecionar para minhas transferências
        setTimeout(() => {
            window.location.href = '/minhas-transferencias';
        }, 300);
    };
    
    // Fechar ao clicar no overlay
    overlay.onclick = fecharPopupElegante;
    
    // Fechar automaticamente após 8 segundos
    setTimeout(fecharPopupElegante, 8000);
}

// ============================================
// FUNÇÃO AUXILIAR: FECHAR POPUP ELEGANTE
// ============================================

function fecharPopupElegante() {
    const popup = document.getElementById('elegantSuccessPopup');
    const overlay = document.querySelector('.popup-overlay');
    const style = document.querySelector('style');
    
    if (popup) {
        popup.style.animation = 'popupSlideIn 0.3s reverse';
        setTimeout(() => popup.remove(), 300);
    }
    
    if (overlay) {
        overlay.style.animation = 'fadeInOverlay 0.3s reverse';
        setTimeout(() => overlay.remove(), 300);
    }
    
    if (style && style.textContent.includes('popupSlideIn')) {
        setTimeout(() => style.remove(), 500);
    }
}

// CARREGAR DADOS DO USUÁRIO
async function loadUserData() {
    try {
        const response = await fetch('/api/user');
        if (response.ok) {
            const data = await response.json();
            if (data.success) {
                document.getElementById('username').textContent = data.user.nome;
                return data.user;
            }
        }
    } catch (error) {
        console.error('Erro ao carregar dados do usuário:', error);
    }
    return null;
}

// VERIFICAÇÃO DE CHAMADA
console.log('🔍 configurarSelectGarantido definida?', typeof configurarSelectGarantido);

// Forçar chamada após loadContas
const oldLoadContas = loadContas;
loadContas = async function() {
    console.log('🔍 loadContas CHAMADA!');
    const result = await oldLoadContas.apply(this, arguments);
    console.log('🔍 loadContas finalizou, resultado:', result);
    return result;
};

// Função auxiliar para atualizar display
function atualizarSaldoDisplay(optionElement) {
    console.log('💸 atualizarSaldoDisplay chamada para:', optionElement.text);
    
    // Tentar várias formas de obter os dados
    let moeda = 'USD';
    let saldo = 0;
    
    // Método 1: dataset
    if (optionElement.dataset.moeda) {
        moeda = optionElement.dataset.moeda;
        saldo = parseFloat(optionElement.dataset.saldo || 0);
        console.log('📊 Via dataset:', { moeda, saldo });
    }
    // Método 2: Extrair do texto
    else if (optionElement.text) {
        const match = optionElement.text.match(/([A-Z]{3})\s*-\s*Saldo:\s*([\d.,]+)/);
        if (match) {
            moeda = match[1];
            saldo = parseFloat(match[2].replace(',', ''));
            console.log('📊 Via regex do texto:', { moeda, saldo });
        }
    }
    // Método 3: Buscar na array userContas
    else {
        const conta = userContas.find(c => c.id === optionElement.value);
        if (conta) {
            moeda = conta.moeda || 'USD';
            saldo = parseFloat(conta.saldo || 0);
            console.log('📊 Via userContas array:', { moeda, saldo });
        }
    }
    
    console.log(`💰 Resultado final: ${saldo} ${moeda}`);
    
    // Atualizar UI
    const saldoSpan = document.getElementById('saldo_valor');
    const moedaLabel = document.getElementById('moeda_label');
    
    if (saldoSpan) {
        saldoSpan.textContent = `${saldo.toFixed(2)} ${moeda}`;
        saldoSpan.style.color = '#27ae60';
        saldoSpan.style.fontWeight = 'bold';
    }
    
    if (moedaLabel) {
        moedaLabel.textContent = moeda;
    }
    
    return { moeda, saldo };
}

// CARREGAR CONTAS DO USUÁRIO
async function loadContas() {
    console.log('🎯 loadContas SIMPLES INICIADA');
    
    try {
        const response = await fetch('/api/user/contas');
        
        if (response.ok) {
            const data = await response.json();
            
            if (data.success && data.contas) {
                // 1. Atualizar userContas GLOBAL
                userContas = data.contas;
                window.userContas = data.contas; // ⬅️ GARANTIR que seja global
                
                console.log(`✅ ${userContas.length} contas carregadas`);
                console.log('📊 Contas:', userContas);
                
                // 2. Atualizar select de forma SUPER SIMPLES
                atualizarSelectSimples();
                
                return true;
            }
        }
    } catch (error) {
        console.error('❌ Erro em loadContas:', error);
    }
    
    return false;
}

function atualizarSelectSimples() {
    console.log('🎯 atualizarSelectSimples INICIADA');
    
    const select = document.getElementById('conta_origem');
    if (!select) {
        console.error('❌ Select não encontrado');
        return;
    }
    
    // 1. Salvar seleção atual
    const valorAtual = select.value;
    
    // 2. Limpar
    select.innerHTML = '<option value="">Selecione sua conta...</option>';
    
    // 3. Adicionar opções (FORMA QUE FUNCIONA)
    userContas.forEach(conta => {
        const option = document.createElement('option');
        option.value = conta.id;
        option.textContent = `${conta.moeda} - Saldo: ${parseFloat(conta.saldo || 0).toFixed(2)}`;
        
        // ⚠️ FORMA CORRETA que FUNCIONA
        option.setAttribute('data-moeda', conta.moeda || 'USD');
        option.setAttribute('data-saldo', parseFloat(conta.saldo || 0));
        
        select.appendChild(option);
    });
    
    console.log(`✅ ${userContas.length} opções adicionadas ao select`);
    
    // 4. Restaurar seleção
    if (valorAtual) {
        select.value = valorAtual;
    }
    
    // 5. 🔥 CONFIGURAR EVENTO QUE FUNCIONA
    configurarEventoQueFunciona();
}

function configurarEventoQueFunciona() {
    console.log('🎯 configurarEventoQueFunciona INICIADA');
    
    const select = document.getElementById('conta_origem');
    if (!select) return;
    
    // ⚠️ FORMA QUE SEMPRE FUNCIONA: onchange direto
    select.onchange = function() {
        console.log('🎉🎉🎉 ONCHANGE DISPARADO! 🎉🎉🎉');
        
        const option = this.options[this.selectedIndex];
        console.log('Opção selecionada:', option?.text);
        
        if (option && option.value) {
            // Obter dados DE QUALQUER JEITO
            let moeda = 'USD';
            let saldo = 0;
            
            // Tentar getAttribute primeiro
            moeda = option.getAttribute('data-moeda') || 'USD';
            saldo = parseFloat(option.getAttribute('data-saldo') || 0);
            
            // Se não funcionou, tentar extrair do texto
            if (!moeda || moeda === 'USD') {
                const partes = option.text.split(' - ');
                if (partes[0]) moeda = partes[0].trim();
                
                const saldoMatch = option.text.match(/Saldo:\s*([\d.]+)/);
                if (saldoMatch) saldo = parseFloat(saldoMatch[1]);
            }
            
            console.log(`💰 Encontrado: ${saldo.toFixed(2)} ${moeda}`);
            
            // ATUALIZAR UI
            const saldoSpan = document.getElementById('saldo_valor');
            const moedaLabel = document.getElementById('moeda_label');
            
            if (saldoSpan) {
                saldoSpan.textContent = `${saldo.toFixed(2)} ${moeda}`;
                saldoSpan.style.color = '#27ae60';
                saldoSpan.style.fontWeight = 'bold';
            }
            
            if (moedaLabel) {
                moedaLabel.textContent = moeda;
            }
        }
    };
    
    console.log('✅ Evento onchange configurado!');
    
    // Testar automaticamente
    if (select.options.length > 1) {
        setTimeout(() => {
            console.log('🧪 Teste automático...');
            select.selectedIndex = 1;
            select.onchange();
        }, 500);
    }
}

// SOLUÇÃO SUPER SIMPLES QUE FUNCIONA
function solucaoDefinitiva() {
    console.log('🎯 SOLUÇÃO DEFINITIVA INICIADA');
    
    const select = document.getElementById('conta_origem');
    if (!select) {
        console.error('❌ Select não encontrado');
        return;
    }
    
    // 1. Configurar evento change de forma ULTRA SIMPLES
    select.onchange = function() {
        console.log('🎉 EVENTO ONCHANGE DISPARADO!');
        
        const option = this.options[this.selectedIndex];
        if (!option || !option.value) {
            document.getElementById('saldo_valor').textContent = '--';
            return;
        }
        
        // Obter dados
        const moeda = option.getAttribute('data-moeda') || 'USD';
        const saldo = parseFloat(option.getAttribute('data-saldo') || 0);
        
        console.log(`💰 ${saldo.toFixed(2)} ${moeda}`);
        
        // Atualizar UI
        document.getElementById('saldo_valor').textContent = `${saldo.toFixed(2)} ${moeda}`;
        document.getElementById('moeda_label').textContent = moeda;
    };
    
    // 2. Configurar também addEventListener (backup)
    select.addEventListener('change', select.onchange);
    
    // 3. Verificar
    console.log('✅ Evento configurado?', select.onchange ? 'SIM!' : 'NÃO');
    
    // 4. Testar automaticamente
    if (select.options.length > 1) {
        setTimeout(() => {
            select.selectedIndex = 1;
            select.onchange();
        }, 1000);
    }
}

// Chamar após loadContas
window.solucaoDefinitiva = solucaoDefinitiva;

// ATUALIZAR SELECT DE CONTAS
function updateContasSelect() {
    console.log('🎯 updateContasSelect CHAMADA!');
    
    const select = document.getElementById('conta_origem');
    if (!select) {
        console.error('❌ Select não encontrado');
        return;
    }
    
    // 1. SALVAR o valor atual (se tiver selecionado)
    const valorAtual = select.value;
    
    // 2. LIMPAR completamente
    select.innerHTML = '<option value="">Selecione sua conta...</option>';
    
    // 3. ADICIONAR opções
    userContas.forEach(conta => {
        const option = document.createElement('option');
        
        const contaId = conta.id;
        const moeda = conta.moeda || 'USD';
        const saldo = parseFloat(conta.saldo || 0);
        
        option.value = contaId;
        option.textContent = `${moeda} - Saldo: ${saldo.toFixed(2)}`;
        
        // Dataset
        option.dataset.moeda = moeda;
        option.dataset.saldo = saldo;
        
        select.appendChild(option);
    });
    
    console.log(`✅ ${userContas.length} opções adicionadas`);
    
    // 4. RESTAURAR seleção anterior (se existia)
    if (valorAtual) {
        select.value = valorAtual;
    }
    
    // 5. 🔥🔥🔥 CONFIGURAR EVENTO ONCHANGE DE FORMA GARANTIDA
    console.log('🎯 Configurando evento onchange...');
    
    // Remover evento anterior
    select.onchange = null;
    
    // Adicionar novo evento (forma mais direta possível)
    select.addEventListener('change', function(event) {
        console.log('🎉🎉🎉 EVENTO CHANGE DISPARADO! 🎉🎉🎉');
        console.log('Evento:', event);
        console.log('Target:', event.target);
        
        const selectedOption = this.options[this.selectedIndex];
        console.log('Opção selecionada:', selectedOption);
        
        if (selectedOption && selectedOption.value) {
            const moeda = selectedOption.dataset.moeda || 'USD';
            const saldo = parseFloat(selectedOption.dataset.saldo || 0);
            
            console.log(`💰 Moeda: ${moeda}, Saldo: ${saldo}`);
            
            // Atualizar UI
            const saldoSpan = document.getElementById('saldo_valor');
            const moedaLabel = document.getElementById('moeda_label');
            
            if (saldoSpan && moedaLabel) {
                saldoSpan.textContent = `${saldo.toFixed(2)} ${moeda}`;
                moedaLabel.textContent = moeda;
                console.log(`✅ UI atualizada: ${saldo.toFixed(2)} ${moeda}`);
                
                // Forçar redesenho
                saldoSpan.style.display = 'none';
                saldoSpan.offsetHeight; // Trigger reflow
                saldoSpan.style.display = '';
            }
        } else {
            console.log('ℹ️ Nenhuma conta selecionada');
            document.getElementById('saldo_valor').textContent = '--';
        }
    }, true); // true = usar capture phase (mais confiável)
    
    // 6. VERIFICAR se o evento foi configurado
    console.log('🔍 Evento configurado?', select.onchange ? 'SIM (onchange)' : 
                                        select._eventListeners ? 'SIM (addEventListener)' : 'NÃO');
    
    // 7. TESTAR IMEDIATAMENTE
    if (valorAtual) {
        setTimeout(() => {
            console.log('🧪 Testando evento com seleção atual...');
            select.dispatchEvent(new Event('change'));
        }, 100);
    }
    
    console.log('✅ updateContasSelect FINALIZADA');
}

function configurarEventoEmergencia() {
    const select = document.getElementById('conta_origem');
    
    // Forma ULTRA simples
    select.onchange = function() {
        console.log('🚨 EVENTO DE EMERGÊNCIA DISPARADO!');
        
        const option = this.options[this.selectedIndex];
        if (option && option.value) {
            const moeda = option.getAttribute('data-moeda') || option.dataset.moeda || 'USD';
            const saldo = parseFloat(option.getAttribute('data-saldo') || option.dataset.saldo || 0);
            
            console.log(`💰 EMERGÊNCIA: ${saldo} ${moeda}`);
            
            // Atualizar de qualquer jeito
            const saldoElement = document.getElementById('saldo_valor');
            const moedaElement = document.getElementById('moeda_label');
            
            if (saldoElement) saldoElement.textContent = `${saldo} ${moeda}`;
            if (moedaElement) moedaElement.textContent = moeda;
        }
    };
    
    console.log('✅ Evento de emergência configurado!');
}

// Executar verificação
setTimeout(verificarEventosSelect, 2000);

// TESTE MANUAL DE SELEÇÃO
function testarSelecaoConta() {
    console.log('🧪 TESTANDO SELEÇÃO DE CONTA...');
    
    const select = document.getElementById('conta_origem');
    if (!select) {
        console.error('❌ Select não encontrado!');
        return;
    }
    
    console.log('📊 Status do select:');
    console.log('  - Total de opções:', select.options.length);
    console.log('  - Event listeners:', select._eventListeners || 'Nenhum');
    
    // Verificar se há evento change
    const temEventoChange = select.onchange || 
                           (select._eventListeners && select._eventListeners.change);
    console.log('  - Tem evento change?', temEventoChange ? 'SIM' : 'NÃO');
    
    // Tentar selecionar a primeira conta
    if (select.options.length > 1) {
        console.log('🔄 Selecionando primeira conta automaticamente...');
        select.selectedIndex = 1;
        
        // Disparar evento manualmente
        const event = new Event('change', { bubbles: true });
        select.dispatchEvent(event);
        
        console.log('✅ Evento change disparado!');
    }
}

// Executar teste após 2 segundos
setTimeout(testarSelecaoConta, 2000);

// Função especial para debug do dataset
function debugDataset() {
    const select = document.getElementById('conta_origem');
    if (!select) {
        console.error('❌ Select não encontrado para debug');
        return;
    }
    
    console.log('🔍 DEBUG DATASET - Todas as opções:');
    console.log('Total de opções:', select.options.length);
    
    for (let i = 0; i < select.options.length; i++) {
        const option = select.options[i];
        console.log(`Opção ${i}:`, {
            texto: option.text,
            valor: option.value,
            dataset: option.dataset,
            moeda: option.dataset.moeda,
            saldo: option.dataset.saldo,
            // Verificar atributos diretamente
            getAttribute_moeda: option.getAttribute('data-moeda'),
            getAttribute_saldo: option.getAttribute('data-saldo')
        });
    }
}

// ATUALIZAR INFO DE SALDO
/*
document.getElementById('conta_origem').addEventListener('change', function() {
    const selectedOption = this.options[this.selectedIndex];
    
    // DEBUG: verificar tudo
    console.log('🔍 Opção selecionada:', selectedOption);
    console.log('📊 Dataset completo:', selectedOption.dataset);
    console.log('📊 dataset.moeda:', selectedOption.dataset.moeda);
    console.log('📊 dataset.saldo:', selectedOption.dataset.saldo);
    
    // ⚠️ CORREÇÃO: Usar dataset em vez de getAttribute
    const moeda = selectedOption.dataset.moeda || 'USD';
    const saldo = parseFloat(selectedOption.dataset.saldo || 0);
    
    // Atualizar exibição do saldo
    const saldoSpan = document.getElementById('saldo_valor');
    const moedaLabel = document.getElementById('moeda_label');
    
    if (saldoSpan && moedaLabel) {
        saldoSpan.textContent = `${saldo.toFixed(2)} ${moeda}`;
        moedaLabel.textContent = moeda;
        console.log(`✅ Saldo atualizado: ${saldo.toFixed(2)} ${moeda}`);
    } else {
        console.error('❌ Elementos de saldo não encontrados!');
    }
});
*/
// Função para forçar atualização do saldo
function forcarAtualizacaoSaldo() {
    console.log('🔄 Forçando atualização de saldo...');
    const select = document.getElementById('conta_origem');
    if (select && select.value) {
        // Disparar evento change manualmente
        select.dispatchEvent(new Event('change'));
    } else {
        console.log('ℹ️ Nenhuma conta selecionada');
    }
}

// Testar após 3 segundos
setTimeout(() => {
    console.log('🧪 Testando atualização automática de saldo...');
    forcarAtualizacaoSaldo();
}, 3000);

// CARREGAR BENEFICIÁRIOS SALVOS
async function loadBeneficiarios() {
    try {
        const response = await fetch('/api/beneficiarios');
        if (response.ok) {
            const data = await response.json();
            if (data.success && data.beneficiarios) {
                updateBeneficiariosSelect(data.beneficiarios);
                return true;
            }
        }
    } catch (error) {
        console.error('Erro ao carregar beneficiários:', error);
    }
    return false;
}

// ATUALIZAR SELECT DE BENEFICIÁRIOS
function updateBeneficiariosSelect(beneficiarios) {
    const select = document.getElementById('beneficiarios_salvos');
    const options = ['<option value="">Selecione um beneficiário salvo...</option>'];
    
    beneficiarios.forEach(benef => {
        options.push(`<option value="${benef.id}">${benef.nome} | ${benef.banco} | ${benef.pais}</option>`);
    });
    
    select.innerHTML = options.join('');
}

// PREENCHER DADOS DO BENEFICIÁRIO SELECIONADO
document.getElementById('beneficiarios_salvos').addEventListener('change', async function() {
    if (!this.value) return;
    
    try {
        console.log(`🔄 Buscando beneficiário ID: ${this.value}`);
        const response = await fetch(`/api/beneficiarios/${this.value}`);
        
        if (response.ok) {
            const data = await response.json();
            console.log('📦 Resposta API:', data);
            
            if (data.success && data.beneficiario) {
                const benef = data.beneficiario;
                console.log(`✅ Preenchendo dados de: ${benef.nome}`);
                
                // PREENCHER CAMPOS COM DADOS REAIS DO SUPABASE
                document.getElementById('beneficiario').value = benef.nome || '';
                document.getElementById('endereco').value = benef.endereco || '';
                document.getElementById('cidade').value = benef.cidade || '';
                document.getElementById('pais').value = benef.pais || '';
                document.getElementById('banco').value = benef.banco || '';
                document.getElementById('endereco_banco').value = benef.endereco_banco || '';
                document.getElementById('cidade_banco').value = benef.cidade_banco || '';
                document.getElementById('pais_banco').value = benef.pais_banco || '';
                document.getElementById('swift').value = benef.swift || '';
                document.getElementById('iban').value = benef.iban || '';
                document.getElementById('aba').value = benef.aba || '';
                
                // FEEDBACK VISUAL
                showAlert(`Beneficiário "${benef.nome}" selecionado!`, 'success');
            } else {
                console.error('❌ API retornou erro:', data.message);
                showAlert(`Erro ao carregar beneficiário: ${data.message || 'Não encontrado'}`, 'error');
            }
        } else {
            console.error('❌ Erro HTTP:', response.status);
            showAlert('Erro ao conectar com o servidor', 'error');
        }
    } catch (error) {
        console.error('❌ Erro ao carregar beneficiário:', error);
        showAlert('Erro de conexão. Tente novamente.', 'error');
    }
});

// UPLOAD DE ARQUIVO
document.getElementById('selectFileBtn').addEventListener('click', () => {
    document.getElementById('invoiceFile').click();
});

document.getElementById('invoiceFile').addEventListener('change', function(e) {
    if (this.files.length > 0) {
        handleFileSelect(this.files[0]);
    }
});

// DRAG AND DROP
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('invoiceFile');

uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('dragover');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    
    if (e.dataTransfer.files.length > 0) {
        handleFileSelect(e.dataTransfer.files[0]);
    }
});

// MANIPULAR SELEÇÃO DE ARQUIVO
function handleFileSelect(file) {
    // Validar tamanho (5MB)
    if (file.size > 5 * 1024 * 1024) {
        showAlert('Arquivo muito grande! O tamanho máximo é 5MB.', 'error');
        return;
    }
    
    // Validar tipo
    const validTypes = ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png'];
    if (!validTypes.includes(file.type)) {
        showAlert('Tipo de arquivo não suportado. Use PDF, JPG ou PNG.', 'error');
        return;
    }
    
    selectedFile = file;
    
    // Mostrar preview
    const preview = document.getElementById('filePreview');
    const fileName = document.getElementById('fileName');
    
    fileName.textContent = file.name;
    preview.classList.remove('hidden');
    
    // Mudar ícone baseado no tipo
    const icon = preview.querySelector('i');
    if (file.type === 'application/pdf') {
        icon.className = 'fas fa-file-pdf';
        icon.style.color = '#27ae60';  // ← VERDE ESCURO
    } else {
        icon.className = 'fas fa-file-image';
        icon.style.color = '#27ae60';  // ← VERDE ESCURO
    }
}

// REMOVER ARQUIVO
document.getElementById('removeFileBtn').addEventListener('click', () => {
    selectedFile = null;
    document.getElementById('filePreview').classList.add('hidden');
    document.getElementById('invoiceFile').value = '';
});


// FECHAR MODAL
document.getElementById('closeModalBtn').addEventListener('click', () => {
    const modal = document.getElementById('successModal');
    modal.classList.remove('show');
    setTimeout(() => modal.classList.add('hidden'), 300);
});

// IR PARA DASHBOARD
document.getElementById('goToDashboardBtn').addEventListener('click', () => {
    window.location.href = '/dashboard';
});

// MOSTRAR ALERTA
function showAlert(message, type = 'info') {
    const alertDiv = document.getElementById('alert');
    alertDiv.textContent = message;
    alertDiv.className = `alert ${type}`;
    alertDiv.classList.remove('hidden');
    
    setTimeout(() => {
        alertDiv.classList.add('hidden');
    }, 5000);
}

// CONFIGURAR EVENT LISTENERS
function setupEventListeners() {
    // Validar valor em tempo real
    document.getElementById('valor').addEventListener('input', function() {
        const valor = parseFloat(this.value) || 0;
        const contaSelect = document.getElementById('conta_origem');
        const saldo = parseFloat(contaSelect.options[contaSelect.selectedIndex]?.dataset.saldo || 0);
        
        if (valor > saldo) {
            this.style.borderColor = '#e74c3c';
            showAlert(`Valor excede saldo disponível (${saldo.toFixed(2)})`, 'warning');
        } else {
            this.style.borderColor = '';
        }
    });
}

// INICIALIZAR
document.addEventListener('DOMContentLoaded', async function() {
    console.log('🚀 Iniciando sistema de transferência...');
    
    try {
        // 1. Carregar dados do usuário (não bloqueante)
        loadUserData().catch(error => {
            console.warn('⚠️ Erro em loadUserData:', error);
        });
        
        // 2. Carregar contas (CRÍTICO - fazer primeiro e separado)
        console.log('🔄 Carregando contas (prioridade)...');
        await loadContas().catch(error => {
            console.error('❌ Erro crítico em loadContas:', error); 
        });
        
        // 3. Carregar beneficiários (não bloqueante)
        setTimeout(() => {
            loadBeneficiarios().catch(error => {
                console.warn('⚠️ Erro em loadBeneficiarios:', error);
            });
        }, 500);
        
        // 4. Configurar eventos
        setupEventListeners();
        
        console.log('✅ Sistema inicializado com sucesso!');
        
    } catch (error) {
        console.error('❌ Erro fatal na inicialização:', error);
    }
});

// TESTE DE EMERGÊNCIA: Forçar updateContasSelect se não funcionar
setTimeout(() => {
    console.log('🚨 TESTE DE EMERGÊNCIA: Verificando se select foi atualizado...');
    
    const select = document.getElementById('conta_origem');
    if (select && select.options.length === 1) {
        // Só tem a opção padrão, então updateContasSelect não foi chamado
        console.log('⚠️ Select não foi atualizado! Forçando agora...');
        
        if (userContas && userContas.length > 0) {
            updateContasSelect();
            console.log('✅ updateContasSelect forçado!');
        } else {
            console.log('❌ Não há contas para atualizar');
        }
    } else if (select && select.options.length > 1) {
        console.log('✅ Select já foi atualizado!');
        
        // Verificar evento
        console.log('🔍 Verificando evento onchange:', select.onchange ? 'SIM' : 'NÃO');
    }
}, 3000);    

// ============================================
// FUNÇÃO PARA MENU DO USUÁRIO
// ============================================

// Função que está sendo chamada pelo onclick mas não existe
function toggleUserMenu() {
    console.log('Menu do usuário clicado');
    
    // Verificar se dropdown existe
    let dropdown = document.getElementById('userDropdown');
    
    // Se não existir, criar
    if (!dropdown) {
        createUserDropdown();
        dropdown = document.getElementById('userDropdown');
    }
    
    // Alternar visibilidade
    dropdown.classList.toggle('show');
    
    // Posicionar corretamente
    if (dropdown.classList.contains('show')) {
        positionDropdown(dropdown);
    }
}

// Criar dropdown do usuário
function createUserDropdown() {
    const dropdownHTML = `
        <div class="dropdown-menu-user" id="userDropdown">
            <div class="dropdown-header">
                <div class="dropdown-username" id="dropdownUserName">${USER?.username || 'Usuário'}</div>
                <div class="dropdown-email" id="dropdownUserEmail">${USER?.email || ''}</div>
            </div>
            
            <a href="/perfil" class="dropdown-item">
                <i class="fas fa-user"></i> Meu Perfil
            </a>
            
            <a href="/configuracoes" class="dropdown-item">
                <i class="fas fa-cog"></i> Configurações
            </a>
            
            <div class="dropdown-divider"></div>
            
            <a href="/logout" class="dropdown-item logout-item">
                <i class="fas fa-sign-out-alt"></i> Sair
            </a>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', dropdownHTML);
}

// Posicionar dropdown corretamente
function positionDropdown(dropdown) {
    const userMenu = document.querySelector('.user-menu');
    if (!userMenu || !dropdown) return;
    
    const rect = userMenu.getBoundingClientRect();
    dropdown.style.top = (rect.bottom + window.scrollY + 10) + 'px';
    dropdown.style.right = (window.innerWidth - rect.right) + 'px';
}

// ============================================
// FUNÇÃO ENVIARTRANSFERENCIA - VERSÃO 2025 CORRIGIDA
// POPUP GARANTIDO + BENEFICIÁRIO EM SEGUNDO PLANO
// ============================================

window.enviarTransferencia = async function(e) {
    if (e) e.preventDefault();
    
    console.log('🚀 enviarTransferencia() - VERSÃO CORRIGIDA');
    
    // 1. COLETAR DADOS (COM NOMES EXATOS DA TABELA)
    const dados = {
        // === DADOS DA CONTA ===
        conta_origem: document.getElementById('conta_origem').value,
        valor: parseFloat(document.getElementById('valor').value) || 0,
        moeda: document.getElementById('conta_origem').options[
            document.getElementById('conta_origem').selectedIndex
        ]?.dataset.moeda || 'USD',
        
        // === DADOS DO BENEFICIÁRIO ===
        beneficiario: document.getElementById('beneficiario').value.trim(),
        endereco_beneficiario: document.getElementById('endereco').value.trim(),
        cidade: document.getElementById('cidade').value.trim(),
        pais: document.getElementById('pais').value.trim(),
        
        // === DADOS DO BANCO ===
        nome_banco: document.getElementById('banco').value.trim(),
        endereco_banco: document.getElementById('endereco_banco').value.trim(),
        cidade_banco: document.getElementById('cidade_banco').value.trim(),
        pais_banco: document.getElementById('pais_banco').value.trim(),
        
        // === DADOS BANCÁRIOS ===
        codigo_swift: document.getElementById('swift').value.trim(),
        iban_account: document.getElementById('iban').value.trim(),
        aba_routing: document.getElementById('aba').value.trim() || '',
        
        // === INFORMAÇÕES ===
        finalidade: document.getElementById('finalidade').value || 'Pagamento de Serviços',
        descricao: document.getElementById('descricao').value || '',
        
        // === DADOS DO USUÁRIO (DA SESSÃO) ===
        cliente: window.USER?.username || 'pantanal',
        usuario: window.USER?.username || 'pantanal',
        solicitado_por: window.USER?.username || 'pantanal',
        
        // === TIPO FIXO ===
        tipo: 'transferencia_internacional',
        status: 'solicitada'
    };
    
    console.log('📦 DADOS (estrutura correta):', dados);
    
    // 2. VALIDAR CAMPOS OBRIGATÓRIOS (APENAS UM LOOP - SEM DUPLICATA!)
    const obrigatorios = [
        { id: 'conta_origem', nome: 'Conta de origem' },
        { id: 'valor', nome: 'Valor' },
        { id: 'beneficiario', nome: 'Beneficiário' },
        { id: 'endereco', nome: 'Endereço do beneficiário' },
        { id: 'cidade', nome: 'Cidade' },
        { id: 'pais', nome: 'País' },
        { id: 'banco', nome: 'Banco' },
        { id: 'endereco_banco', nome: 'Endereço do banco' },
        { id: 'cidade_banco', nome: 'Cidade do banco' },
        { id: 'pais_banco', nome: 'País do banco' },
        { id: 'swift', nome: 'SWIFT' },
        { id: 'iban', nome: 'IBAN' }
    ];
    
    for (const { id, nome } of obrigatorios) {
        const valor = document.getElementById(id).value.trim();
        if (!valor) {
            showAlert(`❌ ${nome} é obrigatório`, 'error');
            document.getElementById(id).focus();
            return false;
        }
    }
    
    // 3. VALIDAR VALOR
    if (dados.valor <= 0 || isNaN(dados.valor)) {
        showAlert('❌ Digite um valor válido (> 0)', 'error');
        return false;
    }
    
    // 4. VALIDAR SALDO
    const contaSelect = document.getElementById('conta_origem');
    const saldo = parseFloat(contaSelect.options[contaSelect.selectedIndex]?.dataset.saldo || 0);
    
    if (dados.valor > saldo) {
        showAlert(`❌ Saldo insuficiente! Disponível: ${saldo.toFixed(2)} ${dados.moeda}`, 'error');
        return false;
    }
    
    // 5. ENVIAR
    const btn = document.getElementById('submitBtn');
    const originalText = btn.innerHTML;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Enviando...';
    btn.disabled = true;
    
    try {
        // Preparar FormData para enviar arquivo também
        const formData = new FormData();
        formData.append('dados', JSON.stringify(dados));
        
        // Adicionar arquivo se existir
        if (selectedFile) {
            formData.append('invoice', selectedFile);
            console.log('📎 Adicionando arquivo:', selectedFile.name);
        }
        
        // Enviar para API
        const response = await fetch('/api/transferencias/criar', {
            method: 'POST',
            body: formData
        });
        
        const resultado = await response.json();
        console.log('✅ Resposta API:', resultado);
        
        if (!response.ok) throw new Error(resultado.message || `Erro ${response.status}`);
        
        if (resultado.success) {
            console.log('🎯🎯🎯 TRANSFERÊNCIA BEM-SUCEDIDA 🎯🎯🎯');
            
            // 🎯 1. MOSTRAR POPUP
            try {
                garantirPopupSucesso(resultado.transferencia_id, dados.valor.toFixed(2), dados.moeda);
            } catch (error) {
                console.error('❌ Erro no popup:', error);
                mostrarPopupSimples(resultado.transferencia_id, dados.valor.toFixed(2), dados.moeda);
            }
            
            // 🎯 2. ATUALIZAR SALDO IMEDIATAMENTE
            setTimeout(() => {
                atualizarSaldoAposTransferencia();
            }, 1000);
            
            // 🎯 3. SALVAR BENEFICIÁRIO (opcional)
            if (document.getElementById('salvar_beneficiario')?.checked) {
                setTimeout(async () => {
                    try {
                        await salvarBeneficiario(dados);
                    } catch (error) {
                        console.warn('⚠️ Erro ao salvar beneficiário:', error);
                    }
                }, 200);
            }
            
            // 🎯 4. LIMPAR FORMULÁRIO
            document.getElementById('transferenciaForm').reset();
            selectedFile = null;
            document.getElementById('filePreview').classList.add('hidden');
            document.getElementById('saldo_valor').textContent = '--';
        }
        
    } catch (error) {
        console.error('❌ Erro:', error);
        showAlert(`❌ ${error.message}`, 'error');
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
    
    return false;
};

// Função para atualizar saldo APÓS transferência
async function atualizarSaldoAposTransferencia() {
    console.log('🔄 Atualizando saldo após transferência...');
    
    try {
        const response = await fetch('/api/user/contas');
        if (response.ok) {
            const data = await response.json();
            if (data.success && data.contas) {
                userContas = data.contas;
                
                // ⚠️ IMPORTANTE: Atualizar o select
                updateContasSelect();
                
                // Manter a seleção atual
                const select = document.getElementById('conta_origem');
                if (select.value) {
                    // Disparar evento para atualizar display
                    select.dispatchEvent(new Event('change'));
                }
            }
        }
    } catch (error) {
        console.warn('⚠️ Erro ao atualizar saldo:', error);
    }
}

// ============================================
// FUNÇÃO AUXILIAR: SALVAR BENEFICIÁRIO (OPCIONAL)
// ============================================

async function salvarBeneficiario(dados) {
    try {
        const benef = {
            nome: dados.beneficiario,
            endereco: dados.endereco_beneficiario,
            cidade: dados.cidade,
            pais: dados.pais,
            banco: dados.nome_banco,
            endereco_banco: dados.endereco_banco,
            cidade_banco: dados.cidade_banco,
            pais_banco: dados.pais_banco,
            swift: dados.codigo_swift,
            iban: dados.iban_account,
            aba: dados.aba_routing || '',
            cliente_username: window.USER?.username || 'pantanal',
            ativo: true
        };
        
        console.log('💾 Salvando beneficiário:', benef);
        
        const response = await fetch('/api/beneficiarios', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(benef)
        });
        
        if (response.ok) {
            const result = await response.json();
            console.log('✅ Beneficiário salvo:', result);
            // Não mostra alerta para não poluir - transferência já teve sucesso
        } else {
            console.warn('⚠️ Erro ao salvar beneficiário, status:', response.status);
            const errorData = await response.json().catch(() => ({}));
            console.warn('📋 Detalhes do erro:', errorData);
        }
    } catch (error) {
        console.warn('⚠️ Erro ao salvar beneficiário:', error);
        // NÃO LANÇA ERRO - É OPICIONAL!
    }
}

// ============================================
// CONFIGURAR FORMULÁRIO PARA USAR FUNÇÃO GLOBAL
// ============================================

// Configurar evento de submit
document.getElementById('transferenciaForm').addEventListener('submit', function(e) {
    window.enviarTransferencia(e);
});

// Tornar outras funções globais
window.carregarContas = loadContas;
window.carregarBeneficiarios = loadBeneficiarios;
window.mostrarAlerta = showAlert;

// Função de teste
window.testarSistema = function() {
    console.log('🧪 Sistema 100% Funcional!');
    console.log(`📊 Contas: ${userContas?.length || 0}`);
    console.log(`👤 Usuário: ${window.USER?.username}`);
    console.log('🚀 Funções disponíveis:');
    console.log('  • enviarTransferencia()');
    console.log('  • carregarContas()');
    console.log('  • testarSistema()');
};

console.log('✅ Sistema de transferência PRONTO!');

// Fechar dropdown ao clicar fora
document.addEventListener('click', function(e) {
    const dropdown = document.getElementById('userDropdown');
    const userMenu = document.querySelector('.user-menu');
    
    if (dropdown && dropdown.classList.contains('show')) {
        if (!dropdown.contains(e.target) && !userMenu?.contains(e.target)) {
            dropdown.classList.remove('show');
        }
    }
});

// Fechar ao pressionar ESC
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        const dropdown = document.getElementById('userDropdown');
        if (dropdown && dropdown.classList.contains('show')) {
            dropdown.classList.remove('show');
        }
    }
});

// Reposicionar dropdown ao redimensionar a janela
window.addEventListener('resize', function() {
    const dropdown = document.getElementById('userDropdown');
    if (dropdown && dropdown.classList.contains('show')) {
        positionDropdown(dropdown);
    }
});

// TESTE AUTOMÁTICO GARANTIDO
setTimeout(() => {
    console.log('🧪 TESTE AUTOMÁTICO GARANTIDO');
    
    const select = document.getElementById('conta_origem');
    if (!select) {
        console.error('❌ Select não existe!');
        return;
    }
    
    console.log('📊 Status:');
    console.log('  - Opções:', select.options.length);
    console.log('  - onchange:', select.onchange ? '✅ CONFIGURADO' : '❌ NÃO CONFIGURADO');
    
    // Se não tem evento, forçar configuração
    if (!select.onchange && userContas && userContas.length > 0) {
        console.log('⚠️ Evento não configurado! Forçando...');
        configurarSelectGarantido();
    }
    
    // Testar seleção automática
    if (select.options.length > 1) {
        console.log('🔄 Selecionando primeira conta para teste...');
        select.selectedIndex = 1;
        
        // Disparar evento
        if (select.onchange) {
            select.onchange();
        } else {
            const event = new Event('change');
            select.dispatchEvent(event);
        }
    }
}, 2000);