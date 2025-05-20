// Theme management
function initializeTheme() {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'light') {
        document.documentElement.setAttribute('data-theme', 'light');
        const themeIcon = document.querySelector('#theme-toggle i');
        if (themeIcon) {
            themeIcon.classList.replace('fa-moon', 'fa-sun');
        }
    }
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    
    const themeIcon = document.querySelector('#theme-toggle i');
    if (themeIcon) {
        themeIcon.classList.replace(
            currentTheme === 'light' ? 'fa-sun' : 'fa-moon',
            newTheme === 'light' ? 'fa-moon' : 'fa-sun'
        );
    }
}

// Initialize theme when DOM is loaded
document.addEventListener('DOMContentLoaded', initializeTheme);

// Add theme toggle button if it doesn't exist
function addThemeToggle() {
    if (!document.querySelector('#theme-toggle')) {
        const nav = document.querySelector('.nav');
        if (nav) {
            const themeToggle = document.createElement('button');
            themeToggle.id = 'theme-toggle';
            themeToggle.className = 'btn btn-link nav-link';
            themeToggle.innerHTML = '<i class="fas fa-moon"></i>';
            themeToggle.onclick = toggleTheme;
            nav.appendChild(themeToggle);
        }
    }
}

// Add theme toggle button when DOM is loaded
document.addEventListener('DOMContentLoaded', addThemeToggle); 