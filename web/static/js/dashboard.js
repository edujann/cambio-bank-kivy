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
    if (lastUpdate) {
        lastUpdate.textContent = `Atualizado ${agora.toLocaleTimeString('pt-BR', {hour: '2-digit', minute: '2-digit'})}`;
    }
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
                if (loading) loading.style.display = 'none';
                if (dashboardContainer) dashboardContainer.style.display = 'block';
                
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
    console.log('🔍 DEBUG [renderizarTransacoes MELHORADA]: Iniciando...');
    console.log('👤 Usuário atual:', USER.username); // ← ADICIONE ESTA LINHA
    
    const transacoesLista = document.getElementById('transacoesLista');
    if (!transacoesLista) {
        console.warn('⚠️ DEBUG: transacoesLista não encontrado');
        return;
    }
    
    if (!transacoes || transacoes.length === 0) {
        transacoesLista.innerHTML = `
            <div class="vazio-message">
                <i class="fas fa-history"></i>
                <p>Nenhuma transação recente</p>
            </div>
        `;
        return;
    }
    
    // Filtra transações do usuário atual e ordena por data (mais recente primeiro)
    const transacoesUsuario = transacoes
        .filter(trans => {
            // Inclui transações onde o usuário é remetente, destinatário ou cliente
            return trans.usuario === USER.username || 
                   trans.cliente === USER.username ||
                   trans.conta_remetente === USER.username ||
                   trans.conta_destinatario === USER.username;
        })
        .sort((a, b) => new Date(b.data || b.created_at) - new Date(a.data || a.created_at))
        .slice(0, 8); // Limita às 8 mais recentes
    
    console.log(`📊 DEBUG: ${transacoes.length} transações totais, ${transacoesUsuario.length} do usuário`);
    
    if (transacoesUsuario.length === 0) {
        transacoesLista.innerHTML = `
            <div class="vazio-message">
                <i class="fas fa-history"></i>
                <p>Nenhuma transação recente</p>
            </div>
        `;
        return;
    }
    
    // Renderiza cada transação
    transacoesLista.innerHTML = transacoesUsuario.map(trans => {
        try {
            const tipo = classificarTransacao(trans);
            const fluxo = determinarFluxoTransacao(trans);
            const config = obterConfiguracaoTransacao(tipo, trans);
            const detalhes = formatarDetalhesTransacao(trans);
            
            // CORREÇÃO: Título específico para câmbio
            let tituloFinal = config.titulo;
            if (tipo === 'cambio_cliente') {
                const descUpper = (trans.descricao || '').toUpperCase();
                if (descUpper.includes('COMPRA')) {
                    tituloFinal = 'Compra de Moeda';
                } else if (descUpper.includes('VENDA')) {
                    tituloFinal = 'Venda de Moeda';
                }
            } else if (tipo === 'cambio_admin') {
                // Para câmbio admin, podemos deixar "Câmbio Administrativo"
                // ou adicionar informação específica se quiser
                tituloFinal = 'Câmbio Administrativo';
            }
            
            return `
                <div class="transacao-item ${fluxo.tipoFluxo}" 
                     data-tipo="${tipo}" 
                     data-status="${trans.status}"
                     data-id="${trans.id}">
                    <div class="transacao-icon" style="color: ${config.corIcone};">
                        <i class="${config.icone}"></i>
                    </div>
                    <div class="transacao-detalhes">
                        <div class="transacao-titulo">${tituloFinal}</div>
                        <div class="transacao-desc">${detalhes.descricao}</div>
                        ${detalhes.detalhes ? `<div class="transacao-info">${detalhes.detalhes}</div>` : ''}
                    </div>
                    <div class="transacao-lado-direito">
                        <div class="transacao-valor ${fluxo.ehEntrada ? 'positivo' : 'negativo'}">
                            ${fluxo.ehEntrada ? '+' : '-'} ${formatarMoeda(trans.valor || 0, trans.moeda || 'BRL')}
                        </div>
                        <div class="transacao-meta">
                            <div class="transacao-data">${formatarData(trans.data || trans.created_at)}</div>
                            <div class="transacao-status status-${trans.status}">
                                ${config.statusFormatado}
                            </div>
                        </div>
                    </div>
                </div>
            `;
        } catch (error) {
            console.error('❌ Erro ao renderizar transação', trans.id, error);
            return `
                <div class="transacao-item">
                    <div class="transacao-icon" style="color: #7f8c8d;">
                        <i class="fas fa-exclamation-triangle"></i>
                    </div>
                    <div class="transacao-detalhes">
                        <div class="transacao-titulo">Erro ao carregar</div>
                        <div class="transacao-desc">Transação ${trans.id}</div>
                    </div>
                </div>
            `;
        }
    }).join('');
    
    console.log(`✅ DEBUG: ${transacoesUsuario.length} transações renderizadas com sucesso`);
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
// FUNÇÕES PARA CLASSIFICAR TRANSAÇÕES (NOVAS)
// ============================================

function classificarTransacao(trans) {
    /**
     * Classifica uma transação em tipos específicos para melhor exibição
     */
    console.log('🔍 DEBUG [classificarTransacao]:', trans.id, trans.tipo, trans.operacao);
    
    // 1. Câmbio (cliente ou admin)
    if (trans.tipo === 'cambio') {
        // Verifica se é cambio_admin
        if (trans.operacao === 'cambio_admin') {
            return 'cambio_admin';
        }
        
        // Tenta detectar compra/venda pela descrição se operacao estiver undefined
        const descricao = (trans.descricao || '').toUpperCase();
        if (descricao.includes('COMPRA') || descricao.includes('COMPRA -')) {
            console.log('✅ Detectado: Câmbio COMPRA pela descrição');
            return 'cambio_cliente';
        } else if (descricao.includes('VENDA') || descricao.includes('VENDA -')) {
            console.log('✅ Detectado: Câmbio VENDA pela descrição');
            return 'cambio_cliente';
        }
        
        // Se tem par_moedas e campos de câmbio, assume que é cambio_cliente
        if (trans.par_moedas || trans.moeda_origem || trans.moeda_destino) {
            console.log('✅ Detectado: Câmbio cliente por campos de câmbio');
            return 'cambio_cliente';
        }
        
        // Fallback para cambio_admin se executado por admin
        if (trans.executado_por === 'admin' || trans.usuario === 'admin') {
            return 'cambio_admin';
        }
    }
    
    // 2. Transferências
    if (trans.tipo === 'transferencia_internacional') return 'transferencia_exterior';
    if (trans.tipo === 'transferencia_interna_cliente') return 'transferencia_interna';
    
    // 3. Ajustes administrativos
    if (trans.tipo === 'ajuste_admin') {
        if (trans.tipo_ajuste === 'CREDITO') return 'ajuste_credito';
        if (trans.tipo_ajuste === 'DEBITO') return 'ajuste_debito';
    }
    
    // 4. Receitas (taxas do banco) - LEMBRAR: é DESPESA para o cliente!
    if (trans.tipo === 'receita') return 'taxa_banco';
    
    // 5. Outros tipos (fallback)
    console.log('⚠️ DEBUG: Tipo não classificado:', trans.tipo);
    return trans.tipo || 'desconhecido';
}

function extrairMoedasCambio(descricao) {
    /**
     * Extrai moeda origem e destino de descrições de câmbio
     * Exemplos:
     * - "CÂMBIO CLIENTE - COMPRA - USD → EUR" → { origem: "USD", destino: "EUR", operacao: "compra" }
     * - "CÂMBIO ADMIN - USD → BRL" → { origem: "USD", destino: "BRL", operacao: null }
     * - "CÂMBIO CLIENTE - VENDA - BRL → USD" → { origem: "BRL", destino: "USD", operacao: "venda" }
     */
    if (!descricao) return { origem: null, destino: null, operacao: null };
    
    const desc = descricao.toUpperCase();
    let origem = null;
    let destino = null;
    let operacao = null;
    
    // Detecta operação
    if (desc.includes('COMPRA')) {
        operacao = 'compra';
    } else if (desc.includes('VENDA')) {
        operacao = 'venda';
    }
    
    // Padrão 1: "USD → EUR" (com seta unicode)
    const padraoSeta = desc.match(/([A-Z]{3})\s*→\s*([A-Z]{3})/);
    if (padraoSeta) {
        origem = padraoSeta[1];
        destino = padraoSeta[2];
    } else {
        // Padrão 2: "USD->EUR" (com traço)
        const padraoTrace = desc.match(/([A-Z]{3})\s*[-]\s*([A-Z]{3})/);
        if (padraoTrace) {
            origem = padraoTrace[1];
            destino = padraoTrace[2];
        } else {
            // Padrão 3: "USD EUR" (apenas espaços)
            const padraoEspaco = desc.match(/([A-Z]{3})\s+([A-Z]{3})/);
            if (padraoEspaco) {
                origem = padraoEspaco[1];
                destino = padraoEspaco[2];
            }
        }
    }
    
    console.log('🔍 extrairMoedasCambio:', { 
        descricao: descricao.substring(0, 50),
        origem, 
        destino, 
        operacao 
    });
    
    return { origem, destino, operacao };
}

function determinarFluxoTransacao(trans) {
    /**
     * Determina se uma transação é ENTRADA ou SAÍDA para o usuário atual
     * Retorna: { ehEntrada: boolean, tipoFluxo: 'entrada' | 'saida' }
     */
    const usuarioAtual = USER.username;
    if (!usuarioAtual) {
        console.warn('⚠️ DEBUG [determinarFluxo]: USER.username não definido');
        return { ehEntrada: false, tipoFluxo: 'saida' };
    }
    
    const tipo = classificarTransacao(trans);
    let ehEntrada = false;
    let tipoFluxo = 'saida';
    
    console.log('🔍 DEBUG [determinarFluxo]:', trans.id, 'Tipo:', tipo, 'Usuário:', usuarioAtual);
    
    switch(tipo) {
        case 'transferencia_exterior':
        case 'transferencia_interna':
            // É entrada se o usuário for o DESTINATÁRIO
            if (trans.conta_destinatario === usuarioAtual) {
                ehEntrada = true;
                tipoFluxo = 'entrada';
                console.log('✅ É ENTRADA: usuário é destinatário');
            } else {
                console.log('✅ É SAÍDA: usuário é remetente');
            }
            break;
            
        case 'cambio_cliente':
            // Usa função especializada para extrair moedas
            const moedas = extrairMoedasCambio(trans.descricao);
            
            let moedaOrigem = trans.moeda_origem || moedas.origem;
            let moedaDestino = trans.moeda_destino || moedas.destino;
            let operacao = trans.operacao || moedas.operacao;
            
            // Fallback: se ainda não tem moeda origem, usa a moeda da transação
            if (!moedaOrigem) {
                moedaOrigem = trans.moeda || '???';
            }
            
            // Fallback para moeda destino
            if (!moedaDestino) {
                moedaDestino = '???';
            }
            
            // Fallback para operação
            if (!operacao) {
                operacao = 'desconhecida';
            }
            
            // Montar descrição FINAL
            if (operacao === 'compra') {
                descricao = `Comprou ${moedaDestino} com ${moedaOrigem}`;
            } else if (operacao === 'venda') {
                descricao = `Vendeu ${moedaOrigem} por ${moedaDestino}`;
            } else if (moedaOrigem && moedaDestino) {
                descricao = `Câmbio ${moedaOrigem} → ${moedaDestino}`;
            } else {
                descricao = 'Operação de câmbio';
            }
            
            // Adicionar detalhes (cotação)
            if (trans.cotacao) {
                detalhes = `Cotação: ${parseFloat(trans.cotacao).toFixed(4)}`;
            } else if (trans.descricao && (trans.descricao.includes('→') || trans.descricao.includes('-'))) {
                detalhes = 'Operação de câmbio';
            }
            break;
            
        case 'cambio_admin':
            // Cambio admin: geralmente entrada (crédito) ou saída (débito)
            // Lógica simplificada: se tem valor_destino e usuário recebeu
            ehEntrada = trans.conta_destinatario === usuarioAtual;
            tipoFluxo = ehEntrada ? 'entrada' : 'saida';
            break;
            
        case 'ajuste_credito':
            // Crédito administrativo é SEMPRE entrada
            ehEntrada = true;
            tipoFluxo = 'entrada';
            console.log('✅ É ENTRADA: ajuste crédito');
            break;
            
        case 'ajuste_debito':
        case 'taxa_banco':
            // Débito e taxas são SEMPRE saída
            ehEntrada = false;
            tipoFluxo = 'saida';
            console.log('✅ É SAÍDA: ajuste débito ou taxa');
            break;
            
        default:
            // Lógica padrão: baseado em conta_destinatario
            ehEntrada = trans.conta_destinatario === usuarioAtual;
            tipoFluxo = ehEntrada ? 'entrada' : 'saida';
            console.log(`✅ Tipo ${tipo}: ${ehEntrada ? 'ENTRADA' : 'SAÍDA'} (padrão)`);
    }
    
    return { ehEntrada, tipoFluxo };
}

function formatarStatusTransacao(status) {
    /**
     * Formata o status para exibição amigável
     */
    if (!status) return 'Desconhecido';
    
    const statusMap = {
        'solicitada': 'Solicitada',
        'pendente': 'Pendente',
        'aprovada': 'Aprovada',
        'approved': 'Aprovada',
        'completed': 'Concluída',
        'concluida': 'Concluída',
        'finalizada': 'Concluída',
        'recusada': 'Recusada',
        'rejected': 'Recusada',
        'cancelada': 'Cancelada',
        'cancelled': 'Cancelada',
        'processing': 'Processando'
    };
    
    return statusMap[status.toLowerCase()] || status;
}

function formatarDetalhesTransacao(trans) {
    /**
     * Formata detalhes específicos baseados no tipo de transação
     * Retorna: { descricao: string, detalhes: string }
     */
    const tipo = classificarTransacao(trans);
    const fluxo = determinarFluxoTransacao(trans);  // Calculado uma vez só
    
    console.log('🔍 DEBUG [formatarDetalhes]:', trans.id, 'Tipo:', tipo, 'Fluxo:', fluxo.ehEntrada ? 'ENTRADA' : 'SAÍDA');
    
    let descricao = '';
    let detalhes = '';
    
    switch(tipo) {
        case 'cambio_cliente':
            // Extrair informações da descrição (padrão: "CÂMBIO CLIENTE - COMPRA - USD → EUR")
            let moedaOrigem = trans.moeda_origem;
            let moedaDestino = trans.moeda_destino;
            let operacao = trans.operacao;
            
            // 1. Se não tem operação, tenta detectar pela descrição
            if (!operacao && trans.descricao) {
                const descUpper = trans.descricao.toUpperCase();
                if (descUpper.includes('COMPRA') || descUpper.includes('COMPRA -')) {
                    operacao = 'compra';
                } else if (descUpper.includes('VENDA') || descUpper.includes('VENDA -')) {
                    operacao = 'venda';
                }
            }
            
            // 2. Extrair moedas da descrição usando REGEX melhorado
            if (trans.descricao && (!moedaOrigem || !moedaDestino)) {
                // Padrões: "USD → EUR", "BRL → USD", "USD->EUR"
                const padraoMoedas = trans.descricao.match(/([A-Z]{3})\s*[→-]\s*([A-Z]{3})/i);
                if (padraoMoedas) {
                    moedaOrigem = moedaOrigem || padraoMoedas[1];
                    moedaDestino = moedaDestino || padraoMoedas[2];
                    console.log('✅ Câmbio cliente: moedas extraídas', { moedaOrigem, moedaDestino });
                }
            }
            
            // 3. Fallback: se ainda não tem moeda origem, usa a moeda da transação
            if (!moedaOrigem) {
                moedaOrigem = trans.moeda || '???';
            }
            
            // 4. Fallback para moeda destino
            if (!moedaDestino) {
                moedaDestino = '???';
            }
            
            // 5. Montar descrição FINAL
            if (operacao === 'compra') {
                descricao = `Comprou ${moedaDestino} com ${moedaOrigem}`;
            } else if (operacao === 'venda') {
                descricao = `Vendeu ${moedaOrigem} por ${moedaDestino}`;
            } else if (moedaOrigem && moedaDestino) {
                descricao = `Câmbio ${moedaOrigem} → ${moedaDestino}`;
            } else {
                descricao = 'Operação de câmbio';
            }
            
            // 6. Adicionar detalhes (cotação)
            if (trans.cotacao) {
                detalhes = `Cotação: ${parseFloat(trans.cotacao).toFixed(4)}`;
            } else if (trans.descricao && (trans.descricao.includes('→') || trans.descricao.includes('-'))) {
                detalhes = 'Operação de câmbio';
            }
            break;
            
        case 'cambio_admin':
            // CÂMBIO ADMINISTRATIVO (executado pelo sistema)
            
            // 1. Tentar extrair moedas da descrição se campos estiverem missing
            let moedaOrigemAdmin = trans.moeda_origem;
            let moedaDestinoAdmin = trans.moeda_destino;
            
            if ((!moedaOrigemAdmin || !moedaDestinoAdmin) && trans.descricao) {
                // Padrão: "CÂMBIO ADMIN - USD → BRL" ou "CÂMBIO ADMIN - USD->BRL"
                const padrao = trans.descricao.match(/([A-Z]{3})\s*[→-]\s*([A-Z]{3})/i);
                if (padrao) {
                    moedaOrigemAdmin = moedaOrigemAdmin || padrao[1];
                    moedaDestinoAdmin = moedaDestinoAdmin || padrao[2];
                    console.log('✅ Câmbio admin: moedas extraídas', { moedaOrigemAdmin, moedaDestinoAdmin });
                }
            }
            
            // Fallbacks
            if (!moedaOrigemAdmin) moedaOrigemAdmin = trans.moeda || '???';
            if (!moedaDestinoAdmin) moedaDestinoAdmin = '???';
            
            // 2. Montar descrição baseada no fluxo (já calculado)
            if (fluxo.ehEntrada) {
                // Usuário RECEBEU moeda (entrada)
                descricao = `Recebeu ${moedaDestinoAdmin} (câmbio administrativo)`;
            } else {
                // Usuário ENVIOU moeda (saída)
                descricao = `Pagou ${moedaOrigemAdmin} (câmbio administrativo)`;
            }
            
            // 3. Detalhes
            if (trans.cotacao) {
                detalhes = `Cotação: ${parseFloat(trans.cotacao).toFixed(4)}`;
            } else if (trans.taxa_principal_registro) {
                detalhes = `Taxa usada: ${parseFloat(trans.taxa_principal_registro).toFixed(4)}`;
            } else if (trans.descricao) {
                // Tenta extrair info útil da descrição
                const descLimpa = trans.descricao.replace('CÂMBIO ADMIN - ', '').replace('CÂMBIO ADMIN ', '');
                if (descLimpa && descLimpa !== trans.descricao) {
                    detalhes = descLimpa;
                } else {
                    detalhes = 'Câmbio executado pelo sistema';
                }
            } else {
                detalhes = 'Câmbio administrativo';
            }
            break;
            
        case 'transferencia_exterior':
            // MOSTRA APENAS O NOME DO BENEFICIÁRIO (não a palavra "Beneficiário")
            if (trans.beneficiario && trans.beneficiario.trim() !== '') {
                descricao = trans.beneficiario;
            } else if (trans.descricao && trans.descricao.trim() !== '') {
                descricao = trans.descricao;
            } else {
                descricao = 'Transferência internacional';
            }
            
            // Detalhes: cidade/pais (apenas se existir)
            if (trans.cidade || trans.pais) {
                detalhes = `${trans.cidade || ''}${trans.cidade && trans.pais ? ', ' : ''}${trans.pais || ''}`;
            }
            if (trans.invoice_info) {
                detalhes += (detalhes ? ' • ' : '') + '📄 Tem invoice';
            }
            break;
            
        case 'transferencia_interna':
            // Já tem fluxo calculado, não precisa chamar novamente
            if (fluxo.ehEntrada) {
                descricao = 'Recebido de outro cliente';
            } else {
                descricao = 'Enviado para outro cliente';
            }
            if (trans.descricao) {
                detalhes = trans.descricao;
            }
            break;
            
        case 'ajuste_credito':
            descricao = trans.descricao_ajuste || 'Crédito administrativo';
            detalhes = 'Executado pelo sistema';
            break;
            
        case 'ajuste_debito':
            descricao = trans.descricao_ajuste || 'Débito administrativo';
            detalhes = 'Executado pelo sistema';
            break;
            
        case 'taxa_banco':
            descricao = trans.descricao_receita || 'Taxa bancária';
            if (trans.categoria_receita) {
                detalhes = trans.categoria_receita;
            }
            break;
            
        default:
            descricao = trans.descricao || 'Transação';
            if (trans.tipo) {
                detalhes = `Tipo: ${trans.tipo}`;
            }
    }
    
    // Limita o tamanho da descrição
    if (descricao.length > 60) {
        descricao = descricao.substring(0, 57) + '...';
    }
    
    return { descricao, detalhes };
}

function obterConfiguracaoTransacao(tipo, trans) {
    /**
     * Retorna configurações visuais (ícone, cor, título) baseadas no tipo
     */
    const configs = {
        'cambio_cliente': {
            icone: 'fas fa-exchange-alt',
            corIcone: '#1a5fb4',
            titulo: 'Operação de Câmbio'  // ← Título padrão
        },
        'cambio_admin': {
            icone: 'fas fa-cogs',
            corIcone: '#9b59b6', // Roxo
            titulo: 'Câmbio Administrativo'
        },
        'transferencia_exterior': {
            icone: 'fas fa-globe-americas',
            corIcone: '#2ecc71', // Verde
            titulo: 'Transferência Internacional'
        },
        'transferencia_interna': {
            icone: 'fas fa-users',
            corIcone: '#f39c12', // Laranja
            titulo: 'Transferência entre Clientes'
        },
        'ajuste_credito': {
            icone: 'fas fa-plus-circle',
            corIcone: '#27ae60', // Verde escuro
            titulo: 'Crédito Administrativo'
        },
        'ajuste_debito': {
            icone: 'fas fa-minus-circle',
            corIcone: '#e74c3c', // Vermelho
            titulo: 'Débito Administrativo'
        },
        'taxa_banco': {
            icone: 'fas fa-file-invoice-dollar',
            corIcone: '#34495e', // Cinza escuro
            titulo: trans.descricao_receita || 'Taxa do Banco'
        },
        'desconhecido': {
            icone: 'fas fa-question-circle',
            corIcone: '#7f8c8d', // Cinza
            titulo: 'Transação'
        }
    };
    
    const config = configs[tipo] || configs['desconhecido'];
    
    // Adiciona status formatado
    config.statusFormatado = formatarStatusTransacao(trans.status);
    
    return config;
}

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