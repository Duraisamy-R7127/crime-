const BASE_URL = "http://localhost:8000";

let jwtToken = localStorage.getItem("crimevision_token");

async function login(username, password) {
    const formData = new FormData();
    formData.append("username", username);
    formData.append("password", password);
    const res = await fetch(`${BASE_URL}/token`, {
        method: "POST",
        body: formData
    });
    if(!res.ok) throw new Error("Login failed");
    const data = await res.json();
    jwtToken = data.access_token;
    localStorage.setItem("crimevision_token", jwtToken);
    return data;
}

function logout() {
    jwtToken = null;
    localStorage.removeItem("crimevision_token");
    window.location.reload();
}

async function apiFetch(endpoint, options = {}) {
    if(!jwtToken) {
        // Show login modal
        document.getElementById('loginModal').style.display = 'flex';
        throw new Error("Unauthorized");
    }
    options.headers = {
        ...options.headers,
        "Authorization": `Bearer ${jwtToken}`
    };
    const res = await fetch(`${BASE_URL}${endpoint}`, options);
    if(res.status === 401) {
        logout();
    }
    return res.json();
}
