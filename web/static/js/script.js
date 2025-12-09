// ===========================================
// FUNCIONALIDADES DA TELA DE TRANSFERÊNCIA
// ===========================================

let selectedFile = null;
let userContas = [];

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

// ENVIAR FORMULÁRIO
document.getElementById('transferenciaForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const submitBtn = document.getElementById('submitBtn');
    const originalText = submitBtn.innerHTML;
    
    try {
        // Desabilitar botão
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processando...';
        
    // Validar se uma conta foi selecionada
    const contaSelect = document.getElementById('conta_origem');
    if (!contaSelect.value || contaSelect.value === '' || contaSelect.value === 'undefined') {
        showAlert('❌ Por favor, selecione uma conta de origem!', 'error');
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
        return;
    }

    // Obter a moeda da conta selecionada
    const moedaConta = contaSelect.options[contaSelect.selectedIndex].dataset.moeda;
    console.log('💰 Moeda selecionada:', moedaConta);

    // SÓ DEPOIS validar saldo
    const valor = parseFloat(document.getElementById('valor').value);
    const saldo = parseFloat(contaSelect.options[contaSelect.selectedIndex]?.dataset.saldo || 0);

    if (valor > saldo) {
        showAlert(`Saldo insuficiente! Disponível: ${saldo.toFixed(2)}`, 'error');
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
        return;
    }
        
    // Coletar dados do formulário
    const formData = new FormData();
    const formJson = {};

    // Adicionar campos do formulário
    const formElements = this.elements;
    for (let element of formElements) {
        if (element.name && !element.disabled) {
            if (element.type === 'checkbox') {
                formJson[element.name] = element.checked;
            } else {
                formJson[element.name] = element.value;
            }
        }
    }

    // Adicionar moeda (que veio da conta selecionada)
    formJson.moeda = moedaConta;
    console.log('📤 Dados completos com moeda:', formJson);
        
        // ********** NOVO CÓDIGO: SALVAR BENEFICIÁRIO **********
        // VERIFICAR SE DEVE SALVAR BENEFICIÁRIO
        const checkboxSalvar = document.getElementById('salvar_beneficiario');
        const deveSalvarBeneficiario = checkboxSalvar && checkboxSalvar.checked;
        
        if (deveSalvarBeneficiario) {
            console.log('💾 CHECKBOX MARCADO - Salvando beneficiário...');
            
            // Preparar dados do beneficiário
            const beneficiarioData = {
                nome: formJson.beneficiario,
                banco: formJson.banco,
                swift: formJson.swift,
                iban: formJson.iban || '',
                endereco: formJson.endereco || '',
                cidade: formJson.cidade || '',
                pais: formJson.pais || '',
                cliente_username: USER.username,
                ativo: true
            };
            
            console.log('📝 Dados do beneficiário:', beneficiarioData);
            
            // Verificar campos obrigatórios
            if (beneficiarioData.nome && beneficiarioData.banco && beneficiarioData.swift) {
                try {
                    console.log('🌐 Enviando para API /api/beneficiarios...');
                    const benefResponse = await fetch('/api/beneficiarios', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(beneficiarioData)
                    });
                    
                    console.log('📨 Resposta da API:', benefResponse.status, benefResponse.statusText);
                    
                    if (benefResponse.ok) {
                        const benefResult = await benefResponse.json();
                        if (benefResult.success) {
                            console.log('✅ Beneficiário salvo com sucesso! ID:', benefResult.id);
                        } else {
                            console.warn('⚠️ API respondeu com erro:', benefResult.message);
                        }
                    } else {
                        console.warn('⚠️ Erro HTTP ao salvar beneficiário:', benefResponse.status);
                    }
                } catch (benefError) {
                    console.error('❌ Erro ao salvar beneficiário:', benefError);
                    // Não impedir a transferência por causa disso
                }
            } else {
                console.warn('⚠️ Campos obrigatórios do beneficiário faltando, não será salvo');
            }
        } else {
            console.log('📝 Checkbox NÃO marcado - Não salvando beneficiário');
        }
        // ********** FIM DO NOVO CÓDIGO **********
        
        // Adicionar usuário atual
        //const user = await loadUserData();
        //formJson.usuario = user?.username || 'cliente';
        
        // Adicionar arquivo se existir
        if (selectedFile) {
            formData.append('invoice', selectedFile);
        }
        
        // Adicionar dados JSON
        formData.append('dados', JSON.stringify(formJson));
        
        // Enviar para API
        const response = await fetch('/api/transferencias/criar', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Mostrar modal de sucesso
            document.getElementById('modalTransferId').textContent = data.transferencia_id;
            document.getElementById('modalValor').textContent = 
                `${parseFloat(formJson.valor).toFixed(2)} ${formJson.moeda}`;
            
            const modal = document.getElementById('successModal');
            modal.classList.remove('hidden');
            modal.classList.add('show');
            
            // Limpar formulário
            this.reset();
            selectedFile = null;
            document.getElementById('filePreview').classList.add('hidden');
            document.getElementById('saldo_valor').textContent = '--';
            
        } else {
            showAlert(data.message || 'Erro ao criar transferência', 'error');
        }
        
    } catch (error) {
        console.error('Erro ao enviar formulário:', error);
        showAlert('Erro de conexão. Tente novamente.', 'error');
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
    }
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