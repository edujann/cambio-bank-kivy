// app_simples.js - Versão mínima sem erros
console.log('✅ app_simples.js carregado');

// Funções básicas
function abrirSidebar() {
    console.log('Abrir sidebar');
    const sidebar = document.getElementById('sidebar');
    if (sidebar) sidebar.classList.add('show');
}

function fecharSidebar() {
    console.log('Fechar sidebar');
    const sidebar = document.getElementById('sidebar');
    if (sidebar) sidebar.classList.remove('show');
}

// Quando a página carrega
document.addEventListener('DOMContentLoaded', function() {
    console.log('✅ Página carregada');
    
    // Configurar menu mobile
    const btnMenu = document.querySelector('.btn-menu-mobile');
    if (btnMenu) {
        btnMenu.addEventListener('click', abrirSidebar);
        console.log('✅ Botão menu configurado');
    }
    
    // Configurar cards
    const cards = document.querySelectorAll('.acao-card');
    cards.forEach(card => {
        card.addEventListener('click', function() {
            alert('Funcionalidade: ' + this.querySelector('.card-title').textContent);
        });
    });
    
    console.log('✅ Tudo configurado!');
});

function selecionarMoeda(moeda) {
    const cards = document.querySelectorAll('.saldo-moeda-card');
    cards.forEach(card => {
        card.style.border = '1px solid var(--cor-borda)';
    });
    
    const cardSelecionado = document.querySelector(`[data-moeda="${moeda}"]`);
    if (cardSelecionado) {
        cardSelecionado.style.border = '2px solid var(--cor-primaria)';
        mostrarNotificacao(`Moeda ${moeda} selecionada para operações`, 'info');
    }
}