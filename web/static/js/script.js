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
        option.value = conta.numero;
        option.textContent = `${conta.numero} | ${conta.moeda} | Saldo: ${conta.saldo.toFixed(2)}`;
        option.dataset.moeda = conta.moeda;
        option.dataset.saldo = conta.saldo;
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
        const response = await fetch(`/api/beneficiarios/${this.value}`);
        if (response.ok) {
            const data = await response.json();
            if (data.success) {
                const benef = data.beneficiario;
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
            }
        }
    } catch (error) {
        console.error('Erro ao carregar beneficiário:', error);
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
        icon.style.color = '#e74c3c';
    } else {
        icon.className = 'fas fa-file-image';
        icon.style.color = '#3498db';
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
        
        // Validar saldo
        const contaSelect = document.getElementById('conta_origem');
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
        
        // Adicionar usuário atual
        const user = await loadUserData();
        formJson.usuario = user?.username || 'cliente';
        
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