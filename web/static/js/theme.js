// ============================================
// TEMA GLOBAL
// ============================================

function toggleTheme() {
    const root = document.documentElement;
    const currentTheme = root.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    
    root.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    
    // Atualizar ícone do botão se existir
    const btnIcon = document.querySelector('#btnTheme i');
    if (btnIcon) {
        btnIcon.className = newTheme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
    }
}

function loadTheme() {
    // 🔥 TEMA ESCURO É O PADRÃO 🔥
    const savedTheme = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
    
    const btnIcon = document.querySelector('#btnTheme i');
    if (btnIcon) {
        btnIcon.className = savedTheme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
    }
}

// Carregar tema quando a página carregar
document.addEventListener('DOMContentLoaded', loadTheme);