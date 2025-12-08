// ============================================
// CONFIGURAÇÕES E CONSTANTES
// ============================================
const USER = window.USER || JSON.parse(localStorage.getItem('usuario') || '{"username": "pantanal"}');
const API_URL = window.API_URL || '';
const TOKEN = localStorage.getItem('token') || 'dummy-token';

// ============================================
// ELEMENTOS DO DOM
// ============================================
const loading = document.getElementById('loading');
const dashboardContainer = document.getElementById('dashboardContainer');
const userInfo = document.getElementById('userInfo');
const userNameSidebar = document.getElementById('userNameSidebar');
const userEmailSidebar = document.getElementById('userEmailSidebar');
const saldoTotal = document.getElementById('saldoTotal');
const quantidadeContas = document.getElementById('quantidadeContas');
const moedasDisponiveis = document.getElementById('moedasDisponiveis');
const ultimaAtualizacao = document.getElementById('ultimaAtualizacao');
const contasBadge = document.getElementById('contasBadge');
const beneficiariosBadge = document.getElementById('beneficiariosBadge');
const contasList = document.getElementById('contasList');
const beneficiariosList = document.getElementById('beneficiariosList');
const transacoesList = document.getElementById('transacoesList');
const acoesGrid = document.getElementById('acoesGrid');
const btnMenu = document.getElementById('btnMenu');
const btnCloseSidebar = document.getElementById('btnCloseSidebar');
const sidebar = document.getElementById('sidebar');
const sidebarOverlay = document.getElementById('sidebarOverlay');
const btnLogout = document.getElementById('btnLogout');
const menuLogout = document.getElementById('menuLogout');
const btnRefresh = document.getElementById('btnRefresh');
const lastUpdate = document.getElementById('lastUpdate');
const notificationsContainer = document.getElementById('notificationsContainer');

// ============================================
// FUNÇÕES DE UTILIDADE
// ============================================
function formatarMoeda(valor, moeda = 'BRL') {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: moeda,
        minimumFractionDigits: 2
    }).format(valor);
}

function formatarData(dataString) {
    if (!dataString) return 'N/A';
    
    const data = new Date(dataString);
    return data.toLocaleDateString('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function mostrarNotificacao(titulo, mensagem, tipo = 'info', duracao = 5000) {
    console.log(`🔍 DEBUG [notificação]: ${tipo} - ${titulo}: ${mensagem}`);
    
    try {
        // Cria container se não existir
        let container = document.getElementById('notificationsContainer');
        if (!container) {
            console.log('🔧 DEBUG: Criando notificationsContainer...');
            container = document.createElement('div');
            container.id = 'notificationsContainer';
            container.className = 'notifications-container';
            document.body.appendChild(container);
            console.log('✅ DEBUG: notificationsContainer criado');
        }
        
        const icons = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-circle',
            warning: 'fas fa-exclamation-triangle',
            info: 'fas fa-info-circle'
        };
        
        const notification = document.createElement('div');
        notification.className = `notification ${tipo}`;
        
        notification.innerHTML = `
            <div class="notification-icon">
                <i class="${icons[tipo]}"></i>
            </div>
            <div class="notification-content">
                <div class="notification-title">${titulo}</div>
                <div class="notification-message">${mensagem}</div>
            </div>
        `;
        
        container.appendChild(notification);
        console.log(`✅ DEBUG: Notificação "${titulo}" adicionada`);
        
        // Remove após a duração
        setTimeout(() => {
            notification.classList.add('hiding');
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.remove();
                    console.log(`✅ DEBUG: Notificação "${titulo}" removida`);
                }
            }, 300);
        }, duracao);
        
    } catch (error) {
        console.error('❌ DEBUG: Erro ao mostrar notificação:', error);
        // Fallback: alert simples se tudo falhar
        alert(`${titulo}: ${mensagem}`);
    }
}

function atualizarTempoAtualizacao() {
    const agora = new Date();
    lastUpdate.textContent = `Atualizado ${agora.toLocaleTimeString('pt-BR', {hour: '2-digit', minute: '2-digit'})}`;
}

// ============================================
// FUNÇÕES DE CARREGAMENTO DE DADOS
// ============================================
async function carregarDashboard() {
    console.log('🔍 DEBUG [1]: Iniciando carregarDashboard()');
    console.log('🔍 DEBUG [2]: USER =', USER);
    console.log('🔍 DEBUG [3]: USER.username =', USER.username);
    console.log('🔍 DEBUG [4]: API_URL =', API_URL);
    
    if (!USER.username) {
        console.log('❌ DEBUG [5]: Usuário não identificado - redirecionando para login');
        mostrarNotificacao('Erro', 'Usuário não identificado. Faça login novamente.', 'error');
        setTimeout(() => window.location.href = '/login', 2000);
        return;
    }
    
    console.log(`🔍 DEBUG [6]: Tentando fetch: ${API_URL}/api/dashboard/${USER.username}`);
    
    try {
        const response = await fetch(`${API_URL}/api/dashboard/${USER.username}`);
        
        console.log('🔍 DEBUG [7]: Response recebida');
        console.log('  - Status:', response.status);
        console.log('  - OK:', response.ok);
        console.log('  - Headers:', Object.fromEntries([...response.headers]));
        
        if (response.status === 401) {
            console.log('❌ DEBUG [8]: Status 401 - Não autorizado');
            mostrarNotificacao('Sessão expirada', 'Faça login novamente.', 'warning');
            setTimeout(() => window.location.href = '/login', 2000);
            return;
        }
        
        if (!response.ok) {
            console.log(`❌ DEBUG [9]: Response não OK: ${response.status} ${response.statusText}`);
            throw new Error(`Erro HTTP: ${response.status}`);
        }
        
        console.log('🔍 DEBUG [10]: Tentando parse JSON...');
        const data = await response.json();
        console.log('🔍 DEBUG [11]: JSON parseado com sucesso');
        console.log('  - data.success:', data.success);
        console.log('  - data.usuario:', data.usuario ? 'SIM' : 'NÃO');
        console.log('  - data.dashboard:', data.dashboard ? 'SIM' : 'NÃO');
        
        if (data.success) {
            console.log('✅ DEBUG [12]: Data.success = TRUE - Processando dados...');
            mostrarDadosUsuario(data.usuario);
            mostrarDadosDashboard(data.dashboard);
            
            console.log('🔍 DEBUG [13]: Dados processados. Escondendo loading...');
            
            // Esconde loading e mostra dashboard
            setTimeout(() => {
                console.log('🔍 DEBUG [14]: Timeout executado - Mostrando dashboard');
                loading.style.display = 'none';
                dashboardContainer.style.display = 'block';
                
                // 🔥 NOVO: Configura event listeners AGORA que o DOM está visível
                configurarEventListeners();
                
                mostrarNotificacao('Bem-vindo!', 'Dashboard carregado com sucesso.', 'success', 3000);
                console.log('✅ DEBUG [15]: Dashboard visível!');
            }, 500);
            
        } else {
            console.log(`❌ DEBUG [16]: Data.success = FALSE: ${data.message}`);
            throw new Error(data.message || 'Erro ao carregar dashboard');
        }
        
    } catch (error) {
        console.error('❌ DEBUG [17]: Erro CATCH:', error);
        console.error('  - Mensagem:', error.message);
        console.error('  - Stack:', error.stack);
        
        mostrarNotificacao('Erro', 'Não foi possível carregar os dados.', 'error');
        
        console.log('🔧 DEBUG [18]: Forçando mostrar dashboard com dados padrão...');
        
        // Mostra dashboard mesmo com erro (com dados padrão)
        setTimeout(() => {
            console.log('🔧 DEBUG [19]: Mostrando dashboard forçado');
            loading.style.display = 'none';
            dashboardContainer.style.display = 'block';
            
            // 🔥 NOVO: Configura event listeners também no fallback
            configurarEventListeners();
            
            mostrarDadosUsuario(USER);
            console.log('⚠️ DEBUG [20]: Dashboard mostrado (modo fallback)');
        }, 1000);
    }
    
    console.log('🔍 DEBUG [21]: Função carregarDashboard() finalizada');
}

function mostrarDadosUsuario(usuario) {
    console.log('🔍 DEBUG [mostrarDadosUsuario]: Iniciando...');
    console.log('  - Usuário recebido:', usuario);
    
    if (!usuario) {
        console.error('❌ DEBUG: usuário é null ou undefined');
        return;
    }
    
    // 1. Atualiza nome no header (userMenu)
    try {
        const userMenu = document.getElementById('userMenu');
        if (userMenu) {
            const userNameElement = userMenu.querySelector('.user-name');
            if (userNameElement) {
                userNameElement.textContent = usuario.nome || usuario.username || 'Usuário';
                console.log('✅ DEBUG: Nome atualizado no header:', userNameElement.textContent);
            } else {
                console.warn('⚠️ DEBUG: Elemento .user-name não encontrado no userMenu');
            }
        } else {
            console.warn('⚠️ DEBUG: Elemento userMenu não encontrado');
        }
    } catch (error) {
        console.error('❌ DEBUG: Erro ao atualizar header:', error);
    }
    
    // 2. Se tiver sidebar (opcional - se seu novo layout tiver)
    try {
        const userNameSidebar = document.getElementById('userNameSidebar');
        const userEmailSidebar = document.getElementById('userEmailSidebar');
        
        if (userNameSidebar) {
            userNameSidebar.textContent = usuario.nome || usuario.username || 'Usuário';
        }
        
        if (userEmailSidebar && usuario.email) {
            userEmailSidebar.textContent = usuario.email;
        }
    } catch (error) {
        // Não é crítico se não tiver sidebar
        console.log('ℹ️ DEBUG: Elementos da sidebar não encontrados (normal se não existirem)');
    }
    
    // 3. Remove a lógica antiga do statusBadge (não existe no novo layout)
    // ❌ NÃO FAZER: const statusBadge = document.querySelector('.status-badge');
    // O novo layout do protótipo não tem status badge visível
    
    console.log('✅ DEBUG [mostrarDadosUsuario]: Concluído com sucesso');
}

function mostrarDadosDashboard(dashboard) {
    console.log('🔍 DEBUG [mostrarDadosDashboard SIMPLIFICADA]: Iniciando...');
    
    try {
        // 1. APENAS O ESSENCIAL: Mostra saldos por moeda
        mostrarSaldosPorMoeda(dashboard.contas);
        
        // 2. Ações rápidas (já funciona)
        renderizarAcoesRapidas();
        
        // 3. Transações (já funciona)
        renderizarTransacoes(dashboard.ultimas_transferencias);
        
        // 4. ❌ REMOVER: renderizarContas (não existe no protótipo)
        // 5. ❌ REMOVER: renderizarBeneficiarios (não existe no protótipo)
        
        console.log('✅ DEBUG [mostrarDadosDashboard]: Concluído (apenas saldos + ações + transações)');
        
    } catch (error) {
        console.error('❌ DEBUG [mostrarDadosDashboard]: Erro:', error);
        // Não relança - continua mesmo com erro parcial
        mostrarNotificacao('Aviso', 'Alguns dados não puderam ser carregados.', 'warning');
    }
}

function mostrarSaldosPorMoeda(contas) {
    console.log('🔍 DEBUG [mostrarSaldosPorMoeda]: Contas recebidas:', contas);
    
    // Inicializa com zeros
    const saldos = {
        USD: { valor: 0, conta: '--' },
        EUR: { valor: 0, conta: '--' },
        GBP: { valor: 0, conta: '--' },
        BRL: { valor: 0, conta: '--' }
    };
    
    // Preenche com dados reais
    contas.forEach(conta => {
        const moeda = conta.moeda;
        if (saldos[moeda] !== undefined) {
            saldos[moeda].valor = conta.saldo || 0;
            saldos[moeda].conta = conta.id || '--';
        }
    });
    
    console.log('🔍 Saldos processados:', saldos);
    
    // Atualiza SOMENTE os elementos que EXISTEM
    const saldoUSDElem = document.getElementById('saldoUSD');
    const saldoBRLElem = document.getElementById('saldoBRL');
    const saldoEURElem = document.getElementById('saldoEUR');
    const saldoGBPElem = document.getElementById('saldoGBP');
    
    if (saldoUSDElem) saldoUSDElem.textContent = formatarMoeda(saldos.USD.valor, 'USD');
    if (saldoBRLElem) saldoBRLElem.textContent = formatarMoeda(saldos.BRL.valor, 'BRL');
    if (saldoEURElem) saldoEURElem.textContent = formatarMoeda(saldos.EUR.valor, 'EUR');
    if (saldoGBPElem) saldoGBPElem.textContent = formatarMoeda(saldos.GBP.valor, 'GBP');
    
    // Elementos de conta (se não existirem, não tenta atualizar)
    const contaUSDElem = document.getElementById('contaUSD');
    const contaBRLElem = document.getElementById('contaBRL');
    const contaEURElem = document.getElementById('contaEUR');
    const contaGBPElem = document.getElementById('contaGBP');
    
    if (contaUSDElem) contaUSDElem.textContent = `Conta: ${saldos.USD.conta}`;
    if (contaBRLElem) contaBRLElem.textContent = `Conta: ${saldos.BRL.conta}`;
    if (contaEURElem) contaEURElem.textContent = `Conta: ${saldos.EUR.conta}`;
    if (contaGBPElem) contaGBPElem.textContent = `Conta: ${saldos.GBP.conta}`;
    
    // Calcula saldo total
    const saldoTotalBRL = 
        (saldos.USD.valor * 5.3) +  // USD → BRL
        (saldos.EUR.valor * 6.1) +  // EUR → BRL
        (saldos.GBP.valor * 7.1) +  // GBP → BRL
        saldos.BRL.valor;
    
    const saldoTotalElem = document.getElementById('saldoTotal');
    if (saldoTotalElem) {
        saldoTotalElem.textContent = formatarMoeda(saldoTotalBRL, 'BRL');
    }
}

// ============================================
// FUNÇÕES DE RENDERIZAÇÃO
// ============================================
function renderizarContas(contas) {
    console.log('🔍 DEBUG: renderizarContas (ignorado - não existe no protótipo)');
    // Não faz nada - as contas já são mostradas nos saldos por moeda
    return;
}

function renderizarBeneficiarios(beneficiarios) {
    console.log('🔍 DEBUG: renderizarBeneficiarios (ignorado - não existe no protótipo)');
    // Não faz nada - não existe esta seção no protótipo
    return;
}

function renderizarTransacoes(transacoes) {
    console.log('🔍 DEBUG: renderizarTransacoes');
    
    const transacoesList = document.getElementById('transacoesList');
    if (!transacoesList) {
        console.warn('⚠️ DEBUG: transacoesList não encontrado');
        return;
    }
    
    if (!transacoes || transacoes.length === 0) {
        transacoesList.innerHTML = `
            <div class="vazio-message">
                <i class="fas fa-history"></i>
                <p>Nenhuma transação recente</p>
            </div>
        `;
        return;
    }
    
    transacoesList.innerHTML = transacoes.map(trans => {
        const isEntrada = trans.conta_destinatario === USER.username;
        const iconClass = isEntrada ? 'fas fa-arrow-down' : 'fas fa-arrow-up';
        const iconColor = isEntrada ? '#2ec27e' : '#e01b24';
        const valorClass = isEntrada ? 'positivo' : 'negativo';
        const sinal = isEntrada ? '+' : '-';
        
        return `
            <div class="transacao-item ${isEntrada ? 'recebida' : 'sucesso'}">
                <div class="transacao-icon">
                    <i class="${iconClass}"></i>
                </div>
                <div class="transacao-detalhes">
                    <div class="transacao-titulo">${trans.descricao || 'Transferência'}</div>
                    <div class="transacao-desc">${trans.conta_remetente || 'Remetente'} → ${trans.conta_destinatario || 'Destinatário'}</div>
                </div>
                <div class="transacao-valor ${valorClass}">
                    ${sinal} ${formatarMoeda(trans.valor || 0, trans.moeda || 'BRL')}
                </div>
                <div class="transacao-data">${formatarData(trans.data)}</div>
            </div>
        `;
    }).join('');
}

function renderizarBeneficiarios(beneficiarios) {
    if (!beneficiarios || beneficiarios.length === 0) {
        beneficiariosList.innerHTML = `
            <div class="vazio-message">
                <i class="fas fa-users"></i>
                <p>Nenhum beneficiário cadastrado</p>
            </div>
        `;
        return;
    }
    
    beneficiariosList.innerHTML = beneficiarios.map(benef => {
        return `
            <div class="beneficiario-item">
                <div class="beneficiario-icon">
                    <i class="fas fa-user-tie"></i>
                </div>
                <div class="beneficiario-info">
                    <div class="beneficiario-nome">${benef.nome}</div>
                    <div class="beneficiario-banco">${benef.banco || 'Banco não informado'}</div>
                </div>
                <div class="beneficiario-status">
                    ${benef.ativo ? '<span class="status-ativo">● Ativo</span>' : '<span class="status-inativo">● Inativo</span>'}
                </div>
            </div>
        `;
    }).join('');
}

function renderizarAcoesRapidas() {
    console.log('🔍 DEBUG: renderizarAcoesRapidas');
    
    const acoesGrid = document.getElementById('acoesGrid');
    if (!acoesGrid) {
        console.warn('⚠️ DEBUG: acoesGrid não encontrado');
        return;
    }
    
    const acoes = [
        {
            id: 'transferencia',
            icon: 'fas fa-exchange-alt',
            title: 'Transferência',
            desc: 'Envie dinheiro para beneficiários',
            color: '#1a5fb4'
        },
        {
            id: 'cambio',
            icon: 'fas fa-chart-line',
            title: 'Câmbio',
            desc: 'Compra e venda de moedas',
            color: '#2ec27e'
        },
        {
            id: 'extrato',
            icon: 'fas fa-file-invoice-dollar',
            title: 'Extrato',
            desc: 'Consulte suas transações',
            color: '#f39c12'
        },
        {
            id: 'beneficiarios',
            icon: 'fas fa-users',
            title: 'Beneficiários',
            desc: 'Gerencie seus contatos',
            color: '#9b59b6'
        }
    ];
    
    acoesGrid.innerHTML = acoes.map(acao => {
        return `
            <div class="acao-card" data-action="${acao.id}">
                <div class="card-icon" style="background: ${acao.color}15; border: 1px solid ${acao.color}30;">
                    <i class="${acao.icon}" style="color: ${acao.color};"></i>
                </div>
                <h3 class="card-title">${acao.title}</h3>
                <p class="card-desc">${acao.desc}</p>
            </div>
        `;
    }).join('');
}

// ============================================
// FUNÇÕES DO MENU/SIDEBAR
// ============================================
function toggleSidebar(show) {
    if (show) {
        sidebar.classList.add('show');
        sidebarOverlay.style.display = 'block';
        document.body.style.overflow = 'hidden';
    } else {
        sidebar.classList.remove('show');
        sidebarOverlay.style.display = 'none';
        document.body.style.overflow = '';
    }
}

function logout() {
    mostrarNotificacao('Saindo...', 'Você será redirecionado para o login.', 'info');
    
    // Limpa localStorage
    localStorage.removeItem('usuario');
    localStorage.removeItem('token');
    
    // Redireciona após 1.5 segundos
    setTimeout(() => {
        window.location.href = '/login';
    }, 1500);
}

// ============================================
// FUNÇÃO PARA CONFIGURAR EVENT LISTENERS
// ============================================
function configurarEventListeners() {
    console.log('🔍 DEBUG: Configurando event listeners...');
    
    // Menu sidebar
    if (btnMenu) btnMenu.addEventListener('click', () => toggleSidebar(true));
    if (btnCloseSidebar) btnCloseSidebar.addEventListener('click', () => toggleSidebar(false));
    if (sidebarOverlay) sidebarOverlay.addEventListener('click', () => toggleSidebar(false));
    
    // Logout
    if (btnLogout) btnLogout.addEventListener('click', logout);
    if (menuLogout) {
        menuLogout.addEventListener('click', (e) => {
            e.preventDefault();
            logout();
        });
    }
    
    // Refresh
    if (btnRefresh) {
        btnRefresh.addEventListener('click', () => {
            btnRefresh.querySelector('i').classList.add('fa-spin');
            mostrarNotificacao('Atualizando', 'Buscando dados atualizados...', 'info', 2000);
            
            setTimeout(() => {
                carregarDashboard();
                btnRefresh.querySelector('i').classList.remove('fa-spin');
            }, 1000);
        });
    }
    
    // Navegação por ações rápidas
    document.addEventListener('click', (e) => {
        const acaoCard = e.target.closest('.acao-card');
        if (acaoCard) {
            const action = acaoCard.dataset.action;
            mostrarNotificacao('Em desenvolvimento', `Funcionalidade "${action}" em breve.`, 'info');
        }
    });
    
    // Navegação do menu
    document.querySelectorAll('.menu-item').forEach(item => {
        item.addEventListener('click', (e) => {
            if (item.dataset.page === 'dashboard') {
                e.preventDefault();
                toggleSidebar(false);
            } else if (item.dataset.page) {
                e.preventDefault();
                mostrarNotificacao('Em desenvolvimento', `Página "${item.dataset.page}" em breve.`, 'info');
                toggleSidebar(false);
            }
        });
    });
    
    console.log('✅ DEBUG: Event listeners configurados');
}

// Navegação por ações rápidas
document.addEventListener('click', (e) => {
    const acaoCard = e.target.closest('.acao-card');
    if (acaoCard) {
        const action = acaoCard.dataset.action;
        mostrarNotificacao('Em desenvolvimento', `Funcionalidade "${action}" em breve.`, 'info');
    }
});

// Navegação do menu
document.querySelectorAll('.menu-item').forEach(item => {
    item.addEventListener('click', (e) => {
        if (item.dataset.page === 'dashboard') {
            e.preventDefault();
            toggleSidebar(false);
        } else if (item.dataset.page) {
            e.preventDefault();
            mostrarNotificacao('Em desenvolvimento', `Página "${item.dataset.page}" em breve.`, 'info');
            toggleSidebar(false);
        }
    });
});

// ============================================
// INICIALIZAÇÃO
// ============================================
document.addEventListener('DOMContentLoaded', () => {
    // Verifica se usuário está logado
    //if (!USER.username || !TOKEN) {
    //    mostrarNotificacao('Acesso negado', 'Faça login para acessar o dashboard.', 'error');
    //    setTimeout(() => window.location.href = '/login', 2000);
    //    return;
    //}
    
    // Carrega dados do dashboard
    carregarDashboard();
    
    // Atualiza tempo a cada minuto
    setInterval(atualizarTempoAtualizacao, 60000);
    
    // Log para debug
    console.log('Dashboard inicializado para:', USER.username);
    console.log('API URL:', API_URL);
});