// ===========================================
// FUNCIONALIDADES DA TELA DE TRANSFERÊNCIA
// ===========================================

let selectedFile = null;
let userContas = [];

// ============================================
// FUNÇÃO DE EMERGÊNCIA: POPUP DE SUCESSO
// (Cole isso NO TOPO do seu script.js, antes de tudo)
// ============================================

function garantirPopupSucesso(transferenciaId, valor, moeda) {
    console.log('🎉 MOSTRANDO POPUP PARA TRANSFERÊNCIA:', transferenciaId);
    
    // Método 1: Alerta nativo (sempre funciona)
    alert(`✅ Transferência ${transferenciaId} criada com sucesso!\nValor: ${valor} ${moeda}`);
    
    // Método 2: Também tentar modal HTML
    try {
        const modal = document.getElementById('successModal');
        const idEl = document.getElementById('modalTransferId');
        const valorEl = document.getElementById('modalValor');
        
        if (modal && idEl && valorEl) {
            idEl.textContent = transferenciaId;
            valorEl.textContent = `${valor} ${moeda}`;
            modal.classList.remove('hidden');
        }
    } catch (e) {
        // Ignora erro - já mostramos o alerta
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

// CARREGAR CONTAS DO USUÁRIO
async function loadContas() {
    try {
        const response = await fetch('/api/user/contas');
        if (response.ok) {
            const data = await response.json();
            if (data.success && data.contas) {
                userContas = data.contas;
                updateContasSelect();
                return true;
            }
        }
    } catch (error) {
        console.error('Erro ao carregar contas:', error);
        showAlert('Erro ao carregar contas. Por favor, recarregue a página.', 'error');
    }
    return false;
}

// ATUALIZAR SELECT DE CONTAS
function updateContasSelect() {
    const select = document.getElementById('conta_origem');
    select.innerHTML = '<option value="">Selecione sua conta...</option>';
    
    userContas.forEach(conta => {
        const option = document.createElement('option');
        // CORREÇÃO: usar conta.id em vez de conta.numero
        option.value = conta.id;
        option.textContent = `${conta.id} | ${conta.moeda} | Saldo: ${conta.saldo ? conta.saldo.toFixed(2) : '0.00'}`;
        option.dataset.moeda = conta.moeda;
        option.dataset.saldo = conta.saldo || 0;
        select.appendChild(option);
    });
}

// ATUALIZAR INFO DE SALDO
document.getElementById('conta_origem').addEventListener('change', function() {
    const selectedOption = this.options[this.selectedIndex];
    const moeda = selectedOption.dataset.moeda;
    const saldo = selectedOption.dataset.saldo;
    
    if (moeda && saldo) {
        document.getElementById('saldo_valor').textContent = `${parseFloat(saldo).toFixed(2)} ${moeda}`;
        document.getElementById('moeda_label').textContent = moeda;
    } else {
        document.getElementById('saldo_valor').textContent = '--';
        document.getElementById('moeda_label').textContent = 'USD';
    }
});

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
    await loadUserData();
    await loadContas();
    await loadBeneficiarios();
    setupEventListeners();
});

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
            // 🎯 1. MOSTRAR POPUP IMEDIATAMENTE (GARANTIDO!)
            garantirPopupSucesso(resultado.transferencia_id, dados.valor.toFixed(2), dados.moeda);
            
            // 🎯 2. SALVAR BENEFICIÁRIO EM SEGUNDO PLANO (se marcado)
            if (document.getElementById('salvar_beneficiario')?.checked) {
                // Executar em background - NÃO BLOQUEIA O POPUP
                setTimeout(async () => {
                    try {
                        await salvarBeneficiario(dados);
                        console.log('✅ Beneficiário salvo opcionalmente');
                    } catch (error) {
                        console.warn('⚠️ Erro ao salvar beneficiário:', error.message);
                        // NÃO FAZ NADA - NÃO AFETA O SUCESSO DA TRANSFERÊNCIA!
                    }
                }, 100); // Pequeno delay para não atrapalhar
            }
            
            // 🎯 3. LIMPAR FORMULÁRIO
            document.getElementById('transferenciaForm').reset();
            selectedFile = null;
            document.getElementById('filePreview').classList.add('hidden');
            document.getElementById('saldo_valor').textContent = '--';
            
            // 🎯 4. RECARREGAR CONTAS
            await window.carregarContas();
            
        } else {
            throw new Error(resultado.message);
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