// frontend/src/api.js
const BASE = '/api';

const storage = {
    getAccess: () => localStorage.getItem('access_token'),
    getRefresh: () => localStorage.getItem('refresh_token'),
    saveTokens: (access, refresh) => { localStorage.setItem('access_token', access); localStorage.setItem('refresh_token', refresh); },
    clear: () => { localStorage.removeItem('access_token'); localStorage.removeItem('refresh_token'); }
};

async function request(path, options = {}, retry = true) {
    const headers = options.headers || {};
    const access = storage.getAccess();
    if (access) headers['Authorization'] = `Bearer ${access}`;
    if (!options.body && !(options.body instanceof FormData)) {
        headers['Content-Type'] = 'application/json';
    }

    const res = await fetch(`${BASE}${path}`, { ...options, headers });

    if (res.status === 401 && retry) {
        // try refresh once
        const ok = await tryRefresh();
        if (ok) return request(path, options, false);
    }

    const text = await res.text();
    let data = null;
    try { data = text ? JSON.parse(text) : null; } catch (e) { data = text; }
    if (!res.ok) {
        const err = new Error(data && data.detail ? data.detail : (data && data.error) || res.statusText || 'Erro na requisição');
        err.status = res.status;
        err.data = data;
        throw err;
    }
    return data;
}

async function tryRefresh() {
    const refresh = storage.getRefresh();
    if (!refresh) return false;
    try {
        const res = await fetch(`${BASE}/token/refresh/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh }),
        });
        if (!res.ok) return false;
        const data = await res.json();
        if (data.access) {
            storage.saveTokens(data.access, refresh);
            return true;
        }
        return false;
    } catch (e) {
        return false;
    }
}

export async function login(email, password) {
    const data = await request('/token/', { method: 'POST', body: JSON.stringify({ email, password }) }, false);
    // token endpoint from simplejwt returns access and refresh
    if (data.access && data.refresh) {
        storage.saveTokens(data.access, data.refresh);
    }
    return data;
}

export async function logout() {
    storage.clear();
}

export async function register({ email, first_name, password }) {
    return request('/usuarios/', { method: 'POST', body: JSON.stringify({ email, first_name, password }) });
}

export async function getMe() {
    return request('/usuarios/', { method: 'GET' });
}

export async function requestPasswordReset(email) {
    return request('/password-reset/', { method: 'POST', body: JSON.stringify({ email }) });
}

export async function confirmPasswordReset(token, new_password, confirm_password) {
    return request('/password-reset/confirm/', { method: 'POST', body: JSON.stringify({ token, new_password, confirm_password }) });
}

export async function listTasks(params = '') {
    const q = params ? `?${params}` : '';
    return request(`/tarefas/${q}`, { method: 'GET' });
}

export async function createTask({ titulo, descricao }) {
    return request('/tarefas/', { method: 'POST', body: JSON.stringify({ titulo, descricao }) });
}

export async function updateTask(id, payload) {
    return request(`/tarefas/${id}/`, { method: 'PATCH', body: JSON.stringify(payload) });
}

export async function deleteTask(id) {
    return request(`/tarefas/${id}/`, { method: 'DELETE' });
}

export default {
    login, logout, register, getMe, listTasks, createTask, updateTask, deleteTask
};
