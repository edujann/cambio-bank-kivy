// ============================================
// CONFIGURAÇÕES DA API
// ============================================
const API_URL = 'http://localhost:5000';  // URL da sua API Flask

// ============================================
// ELEMENTOS DO DOM
// ============================================
const loginForm = document.getElementById('loginForm');
const usernameInput = document.getElementById('username');
const passwordInput = document.getElementById('password');
const btnLogin = document.getElementById('btnLogin');
const statusMessage = document.getElementById('statusMessage');
const apiStatus = document.getElementById('apiStatus');

// ============================================
// FUNÇÕES DE UTILIDADE
// ============================================
function showStatus(message, type = 'info') {
    statusMessage.textContent = message;
    statusMessage.className = 'status';
    
    if (type !== 'info') {
        statusMessage.classList.add(type);
    }
}

function showLoading(loading = true) {
    if (loading) {
        btnLogin.disabled = true;
        btnLogin.innerHTML = '<i class="fas fa-spinner fa-spin"></i><span>Entrando...</span>';
        showStatus('Autenticando...', 'loading');
    } else {
        btnLogin.disabled = false;
        btnLogin.innerHTML = '<i class="fas fa-sign-in-alt"></i><span>Entrar</span>';
    }
}

function checkAPIStatus() {
    fetch(`${API_URL}/api/status`)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'operacional') {
                apiStatus.textContent = 'API Online';
                apiStatus.className = 'online';
            }
        })
        .catch(error => {
            apiStatus.textContent = 'API Offline';
            apiStatus.className = 'offline';
            console.error('Erro ao conectar na API:', error);
        });
}

// ============================================
// FUNÇÃO DE LOGIN
// ============================================
async function fazerLogin(username, password) {
    showLoading(true);
    
    try {
        const response = await fetch(`${API_URL}/api/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                usuario: username,
                senha: password
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showStatus('✅ Login realizado com sucesso!', 'success');
            
            // Armazena os dados do usuário
            localStorage.setItem('usuario', JSON.stringify(data.usuario));
            localStorage.setItem('token', 'fake-token-' + Date.now()); // Em produção, use JWT real
            
            console.log('Usuário logado:', data.usuario);
            
            // Redireciona para o dashboard após 1.5 segundos
            setTimeout(() => {
                window.location.href = '/dashboard';
            }, 1500);
            
        } else {
            showStatus(`❌ ${data.message}`, 'error');
            showLoading(false);
            
            // Efeito visual de erro
            usernameInput.style.borderColor = '#e01b24';
            passwordInput.style.borderColor = '#e01b24';
            
            setTimeout(() => {
                usernameInput.style.borderColor = '';
                passwordInput.style.borderColor = '';
            }, 2000);
        }
        
    } catch (error) {
        console.error('Erro no login:', error);
        showStatus('❌ Erro de conexão com o servidor', 'error');
        showLoading(false);
    }
}

// ============================================
// VALIDAÇÃO DO FORMULÁRIO
// ============================================
function validarFormulario() {
    const username = usernameInput.value.trim();
    const password = passwordInput.value.trim();
    
    if (!username) {
        showStatus('❌ Digite o nome de usuário', 'error');
        usernameInput.focus();
        return false;
    }
    
    if (!password) {
        showStatus('❌ Digite a senha', 'error');
        passwordInput.focus();
        return false;
    }
    
    if (password.length < 6) {
        showStatus('❌ Senha deve ter pelo menos 6 caracteres', 'error');
        passwordInput.focus();
        return false;
    }
    
    return true;
}

// ============================================
// EVENT LISTENERS
// ============================================
loginForm.addEventListener('submit', function(event) {
    event.preventDefault();
    
    if (validarFormulario()) {
        const username = usernameInput.value.trim();
        const password = passwordInput.value.trim();
        
        fazerLogin(username, password);
    }
});

// Limpa mensagens de erro ao digitar
usernameInput.addEventListener('input', () => {
    statusMessage.textContent = '';
    statusMessage.className = 'status';
});

passwordInput.addEventListener('input', () => {
    statusMessage.textContent = '';
    statusMessage.className = 'status';
});

// Foco automático no campo de usuário
document.addEventListener('DOMContentLoaded', function() {
    usernameInput.focus();
    
    // Verifica se já está logado
    const usuario = localStorage.getItem('usuario');
    if (usuario) {
        showStatus('✅ Você já está logado. Redirecionando...', 'success');
        setTimeout(() => {
            window.location.href = '/dashboard';
        }, 1000);
    }
    
    // Verifica status da API
    checkAPIStatus();
    setInterval(checkAPIStatus, 30000); // Verifica a cada 30 segundos
    
    // Sugestão de usuário para teste (apenas em desenvolvimento)
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        console.log('💡 Dica para teste:');
        console.log('Usuário: hidroamerica');
        console.log('Senha: cliente123');
    }
});

// ============================================
// FUNÇÕES EXTRAS (para testes)
// ============================================
function preencherCredenciaisTeste() {
    // Apenas para desenvolvimento - NÃO usar em produção!
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        usernameInput.value = 'hidroamerica';
        passwordInput.value = 'cliente123';
        showStatus('Credenciais de teste preenchidas', 'info');
    }
}

// Adiciona atalho de teclado para testes (Ctrl+Shift+T)
document.addEventListener('keydown', function(event) {
    if (event.ctrlKey && event.shiftKey && event.key === 'T') {
        event.preventDefault();
        preencherCredenciaisTeste();
    }
});