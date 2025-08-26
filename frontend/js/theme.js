// ============================================
// THEME MANAGEMENT
// ============================================
export function initTheme() {
    // Check for saved theme preference or default to 'dark'
    const savedTheme = localStorage.getItem('theme') || 'dark';
    setTheme(savedTheme);
}

export function setTheme(theme) {
    localStorage.setItem('theme', theme);

    if (theme === 'dark') {
        document.documentElement.classList.add('dark');
    } else {
        document.documentElement.classList.remove('dark');
    }

    // Update theme toggle buttons
    updateThemeToggleButtons(theme);
}

export function toggleTheme() {
    const currentTheme = localStorage.getItem('theme') || 'dark';
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
}

function updateThemeToggleButtons(theme) {
    const sunIcons = document.querySelectorAll('#sunIcon, #mobileSunIcon');
    const moonIcons = document.querySelectorAll('#moonIcon, #mobileMoonIcon');

    if (theme === 'dark') {
        sunIcons.forEach(icon => icon.classList.remove('hidden'));
        moonIcons.forEach(icon => icon.classList.add('hidden'));
    } else {
        sunIcons.forEach(icon => icon.classList.add('hidden'));
        moonIcons.forEach(icon => icon.classList.remove('hidden'));
    }
}
