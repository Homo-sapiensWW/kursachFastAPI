// ===== НАСТРОЙКИ: поправь под свой бэкенд =====
const API_URL = 'http://localhost:8000';
const ROUTES = {
    login: '/auth/login',    // если у роутера есть prefix, например '/auth' -> '/auth/login'
    cars: '/cars',     // список машин
    marks: '/cars/marks',   // список марок
    models: '/cars/models'  // список моделей
};
// ==============================================

// Читаем токен и достаём из него данные (role, exp). Если токена нет или он протух - null.
function parseToken() {
    const t = localStorage.getItem('token');
    if (!t) return null;
    try {
        const payload = JSON.parse(atob(t.split('.')[1].replace(/-/g, '+').replace(/_/g, '/')));
        if (payload.exp && payload.exp * 1000 < Date.now()) {
            localStorage.removeItem('token');
            return null;
        }
        return payload;
    } catch (e) {
        return null;
    }
}

function getRole() {
    const p = parseToken();
    return p ? p.role : null;   // 'dealer' | 'client' | null
}

function logout() {
    localStorage.removeItem('token');
    location.href = 'index.html';
}

// Обёртка над fetch: сама подставляет токен, при 401 отправляет на страницу входа
async function apiFetch(path, options = {}) {
    const headers = new Headers(options.headers || {});
    const token = localStorage.getItem('token');
    if (token) headers.set('Authorization', 'Bearer ' + token);
    const res = await fetch(API_URL + path, { ...options, headers });
    if (res.status === 401 && !options.noRedirect) {
        localStorage.removeItem('token');
        location.href = 'login.html';
    }
    return res;
}

// Рисует бургер-меню в зависимости от роли
function renderMenu() {
    const ul = document.getElementById('menu');
    if (!ul) return;
    const role = getRole();
    const items = [['index.html', 'Головна']];
    if (role === 'dealer') {
        items.push(['add_car.html', 'Додати авто'], ['admin.html', 'Панель керування'],
                   ['dealer_stats.html', 'Моя статистика'], ['all_deals.html', 'Всі договори']);
    } else if (role === 'client') {
        items.push(['profile.html', 'Мій кабінет']);
    } else {
        items.push(['login.html', 'Вхід'], ['register.html', 'Реєстрація']);
    }
    if (role) items.push(['#', 'Вихід', logout]);
    items.push(['#', 'Контакти']);

    ul.innerHTML = '';
    for (const [href, text, onClick] of items) {
        const li = document.createElement('li');
        const a = document.createElement('a');
        a.className = 'menu-item';
        a.href = href;
        a.textContent = text;
        if (onClick) a.addEventListener('click', (e) => { e.preventDefault(); onClick(); });
        li.appendChild(a);
        ul.appendChild(li);
    }
}