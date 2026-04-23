const API_URL = window.location.origin;

// State
let state = {
    token: localStorage.getItem("token") || null,
    user: null // {user_id, role}
};

// DOM Elements
const authView = document.getElementById("auth-view");
const dashboardView = document.getElementById("dashboard-view");
const loginForm = document.getElementById("login-form");
const signupForm = document.getElementById("signup-form");
const toggleAuthBtn = document.getElementById("toggle-auth");
const authToggleText = document.getElementById("auth-toggle-text");
const logoutBtn = document.getElementById("logout-btn");
const contentArea = document.getElementById("content-area");
const navLinks = document.getElementById("nav-links");
const headerActions = document.getElementById("header-actions");
const pageTitle = document.getElementById("page-title");
const modalOverlay = document.getElementById("modal-overlay");
const modalTitle = document.getElementById("modal-title");
const modalBody = document.getElementById("modal-body");
const closeModal = document.getElementById("close-modal");

// Utility: Decode JWT
function parseJwt(token) {
    try {
        const base64Url = token.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
            return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
        }).join(''));
        return JSON.parse(jsonPayload);
    } catch (e) {
        return null;
    }
}

// Utility: API Fetch
async function apiFetch(endpoint, method = "GET", body = null, customToken = null) {
    const headers = { "Content-Type": "application/json" };
    const authToken = customToken || state.token;
    if (authToken) {
        headers["Authorization"] = `Bearer ${authToken}`;
    }
    
    const options = { method, headers };
    if (body) options.body = JSON.stringify(body);

    const res = await fetch(`${API_URL}${endpoint}`, options);
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "API Error");
    return data;
}

// Initialization
function init() {
    if (state.token) {
        const payload = parseJwt(state.token);
        if (payload && payload.exp * 1000 > Date.now()) {
            state.user = payload;
            showDashboard();
        } else {
            logout();
        }
    } else {
        showAuth();
    }
}

// UI Navigation
function showAuth() {
    authView.classList.add("active");
    dashboardView.classList.remove("active");
    dashboardView.classList.add("hidden");
    authView.classList.remove("hidden");
}

function showDashboard() {
    authView.classList.remove("active");
    authView.classList.add("hidden");
    dashboardView.classList.add("active");
    dashboardView.classList.remove("hidden");
    
    // Update User Profile UI
    document.getElementById("user-role-display").innerText = state.user.role.replace("_", " ");
    document.getElementById("user-avatar").innerText = state.user.role.charAt(0).toUpperCase();

    renderNav();
    loadDashboardHome();
}

function logout() {
    state.token = null;
    state.user = null;
    localStorage.removeItem("token");
    showAuth();
}

// Auth Handlers
loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const btn = document.getElementById("login-btn");
    const spinner = btn.querySelector(".spinner");
    const errorMsg = document.getElementById("login-error");
    
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    
    try {
        btn.disabled = true;
        spinner.classList.remove("hidden");
        errorMsg.classList.add("hidden");
        
        const data = await apiFetch("/auth/login", "POST", { email, password });
        state.token = data.access_token;
        localStorage.setItem("token", state.token);
        init();
    } catch (err) {
        errorMsg.innerText = err.message;
        errorMsg.classList.remove("hidden");
    } finally {
        btn.disabled = false;
        spinner.classList.add("hidden");
    }
});

document.getElementById("signup-role").addEventListener("change", (e) => {
    const instGroup = document.getElementById("institution-id-group");
    const instInput = document.getElementById("signup-institution-id");
    if (e.target.value === "institution") {
        instGroup.classList.remove("hidden");
        instInput.required = true;
    } else {
        instGroup.classList.add("hidden");
        instInput.required = false;
    }
});

signupForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const btn = document.getElementById("signup-btn");
    const spinner = btn.querySelector(".spinner");
    const errorMsg = document.getElementById("signup-error");
    
    const payload = {
        name: document.getElementById("signup-name").value,
        email: document.getElementById("signup-email").value,
        password: document.getElementById("signup-password").value,
        role: document.getElementById("signup-role").value,
    };
    
    if (payload.role === "institution") {
        payload.institution_id = parseInt(document.getElementById("signup-institution-id").value) || null;
    }
    
    try {
        btn.disabled = true;
        spinner.classList.remove("hidden");
        errorMsg.classList.add("hidden");
        
        await apiFetch("/auth/signup", "POST", payload);
        const loginData = await apiFetch("/auth/login", "POST", { email: payload.email, password: payload.password });
        state.token = loginData.access_token;
        localStorage.setItem("token", state.token);
        init();
    } catch (err) {
        errorMsg.innerText = err.message;
        errorMsg.classList.remove("hidden");
    } finally {
        btn.disabled = false;
        spinner.classList.add("hidden");
    }
});

toggleAuthBtn.addEventListener("click", (e) => {
    e.preventDefault();
    const isLogin = !loginForm.classList.contains("hidden");
    if (isLogin) {
        loginForm.classList.add("hidden");
        signupForm.classList.remove("hidden");
        authToggleText.innerHTML = 'Already have an account? <a href="#" id="toggle-auth">Sign in</a>';
    } else {
        signupForm.classList.add("hidden");
        loginForm.classList.remove("hidden");
        authToggleText.innerHTML = 'Need an account? <a href="#" id="toggle-auth">Sign up</a>';
    }
    document.getElementById("toggle-auth").addEventListener("click", arguments.callee);
});

logoutBtn.addEventListener("click", logout);
closeModal.addEventListener("click", () => modalOverlay.classList.add("hidden"));

// Dashboard Logic
function renderNav() {
    navLinks.innerHTML = "";
    const links = [{ id: "home", label: "Overview" }];
    
    if (state.user.role === "student" || state.user.role === "trainer") {
        links.push({ id: "join", label: "Join Batch" });
    }
    
    links.forEach(l => {
        const li = document.createElement("li");
        li.className = "nav-item";
        li.innerText = l.label;
        li.onclick = () => {
            document.querySelectorAll(".nav-item").forEach(el => el.classList.remove("active"));
            li.classList.add("active");
            if(l.id === "home") loadDashboardHome();
            if(l.id === "join") renderJoinBatch();
        };
        navLinks.appendChild(li);
    });
    navLinks.firstChild.classList.add("active");
}

async function loadDashboardHome() {
    pageTitle.innerText = "Overview";
    headerActions.innerHTML = "";
    contentArea.innerHTML = '<div class="spinner" style="margin: 2rem auto;"></div>';
    
    try {
        let html = "";
    if (state.user.role === "programme_manager") {
            const data = await apiFetch("/programme/summary");
            html = `
                <div class="grid">
                    <div class="stat-card"><h3>Institutions</h3><div class="value">${data.total_institutions}</div></div>
                    <div class="stat-card"><h3>Total Students</h3><div class="value">${data.total_students}</div></div>
                    <div class="stat-card"><h3>Total Batches</h3><div class="value">${data.total_batches}</div></div>
                </div>
                <div style="margin-top:2rem">
                    <h3>Programme Actions</h3>
                    <p style="color:var(--text-muted); margin-top:0.5rem; margin-bottom:1rem;">Create batches for any institution from here.</p>
                    <div class="action-row" style="flex-wrap:wrap;">
                        <button class="btn primary-btn" onclick="openCreateBatchModal()">+ Create Batch</button>
                        <button class="btn outline-btn" onclick="openCreateBatchModal()">Create Another Batch</button>
                    </div>
                </div>
            `;
        } else if (state.user.role === "institution") {
            const institutionId = state.user.institution_id;
            if (!institutionId) {
                contentArea.innerHTML = `<div class="error-msg">Institution ID is missing from your account. Please sign up again with an institution ID.</div>`;
                return;
            }
            
            const btn = document.createElement("button");
            btn.className = "btn primary-btn";
            btn.innerText = "+ Create Batch";
            btn.onclick = () => openCreateBatchModal(institutionId, true);
            headerActions.appendChild(btn);
            
            try {
                const data = await apiFetch(`/institutions/${institutionId}/summary`);
                html = `
                    <div class="grid">
                        <div class="stat-card"><h3>Total Batches</h3><div class="value">${data.total_batches}</div></div>
                        <div class="stat-card"><h3>Institution ID</h3><div class="value">${data.institution_id}</div></div>
                    </div>
                    <div style="margin-top:2rem">
                        <h3>Institution Actions</h3>
                        <div class="action-row" style="margin-top:1rem; align-items:center;">
                            <input type="number" id="batch-summary-id" placeholder="Batch ID" style="max-width: 150px">
                            <button class="btn outline-btn" onclick="viewBatchSummary()">View Batch</button>
                        </div>
                    </div>
                `;
            } catch(e) {
                html = `<div class="error-msg">Could not load summary.</div>`;
            }
        } else if (state.user.role === "trainer") {
             html = `
                <div class="grid">
                    <div class="stat-card"><h3>Role</h3><div class="value">Trainer</div></div>
                    <div class="stat-card"><h3>Trainer ID</h3><div class="value">${state.user.user_id}</div></div>
                </div>
                <div style="margin-top:2rem">
                    <h3>Trainer Actions</h3>
                    <div class="action-row" style="margin-top:1rem; flex-wrap:wrap;">
                        <button class="btn primary-btn" onclick="openCreateSessionModal()">+ New Session</button>
                        <button class="btn outline-btn" onclick="openMarkAttendanceModal()">Mark Attendance</button>
                    </div>
                    <div class="action-row" style="margin-top:1rem; align-items:center;">
                        <input type="number" id="session-attendance-id" placeholder="Session ID" style="max-width: 150px">
                        <button class="btn outline-btn" onclick="viewSessionAttendance()">View Attendance</button>
                    </div>
                </div>
            `;
        } else if (state.user.role === "student") {
            html = `
                <div class="grid">
                    <div class="stat-card"><h3>Role</h3><div class="value">Student</div></div>
                    <div class="stat-card"><h3>Student ID</h3><div class="value">${state.user.user_id}</div></div>
                </div>
                <div style="margin-top:2rem">
                    <h3>Student Actions</h3>
                    <p style="color:var(--text-muted); margin-top:0.5rem; margin-bottom:1rem;">Use the Join Batch tab to join a class.</p>
                    <button class="btn primary-btn" onclick="openMarkAttendanceModal()">Mark My Attendance</button>
                </div>
            `;
        } else if (state.user.role === "monitoring_officer") {
            html = `
                <div class="grid">
                    <div class="stat-card"><h3>Role</h3><div class="value">Monitoring</div></div>
                </div>
                <div style="margin-top:2rem">
                    <h3>System Monitoring</h3>
                    <p style="color:var(--text-muted); margin-bottom:1rem;">Monitoring dashboard access requires API Key generation.</p>
                    <div class="action-row" style="margin-bottom:1rem">
                        <input type="password" id="monitoring-api-key" placeholder="Enter API Key (e.g. supersecretmonitoringkey)" style="max-width:300px">
                        <button class="btn primary-btn" onclick="generateMonitoringToken()">1. Get Secure Token</button>
                    </div>
                    <div id="monitoring-token-res" style="margin-bottom:1rem; word-break:break-all; font-size:0.8rem; color:var(--success)"></div>
                    
                    <button class="btn outline-btn" onclick="viewAllAttendance()">2. Load Full Attendance Records</button>
                    <div id="monitoring-data" style="margin-top:1.5rem"></div>
                </div>
            `;
        }
        
        contentArea.innerHTML = html;
    } catch (err) {
        contentArea.innerHTML = `<div class="error-msg">Error loading dashboard: ${err.message}</div>`;
    }
}

// Feature Actions
function renderJoinBatch() {
    pageTitle.innerText = "Join Batch";
    headerActions.innerHTML = "";
    contentArea.innerHTML = `
        <div class="glass-card" style="max-width: 400px;">
            <h3>Join a Batch</h3>
            <p style="color:var(--text-muted); font-size:0.9rem; margin-bottom:1rem;">Enter the invite token provided by your institution or trainer.</p>
            <div class="input-group">
                <input type="text" id="join-token" placeholder="Invite Token...">
            </div>
            <button class="btn primary-btn" style="margin-top:1rem; width:100%" onclick="joinBatch()">Join</button>
            <div id="join-res" style="margin-top:1rem"></div>
        </div>
    `;
}

async function joinBatch() {
    const token = document.getElementById("join-token").value;
    const resDiv = document.getElementById("join-res");
    try {
        const data = await apiFetch("/batches/join", "POST", { token });
        resDiv.innerHTML = `<div class="badge present">Successfully joined batch ${data.batch_id}!</div>`;
    } catch (e) {
        resDiv.innerHTML = `<div class="error-msg">${e.message}</div>`;
    }
}

async function viewBatchSummary() {
    const id = document.getElementById("batch-summary-id").value;
    if(!id) return;
    try {
        const data = await apiFetch(`/batches/${id}/summary`);
        openModal(`Batch: ${data.name}`, `
            <div class="grid" style="grid-template-columns: 1fr 1fr; gap:1rem;">
                <div class="stat-card" style="padding:1rem"><h3>Students</h3><div class="value" style="font-size:1.5rem">${data.students_count}</div></div>
                <div class="stat-card" style="padding:1rem"><h3>Trainers</h3><div class="value" style="font-size:1.5rem">${data.trainers_count}</div></div>
                <div class="stat-card" style="padding:1rem"><h3>Sessions</h3><div class="value" style="font-size:1.5rem">${data.sessions_count}</div></div>
            </div>
            <div style="margin-top:1rem">
                <button class="btn outline-btn" onclick="generateInvite(${id})">Generate Invite Link</button>
                <div id="invite-res" style="margin-top:0.5rem; font-size:0.8rem; word-break:break-all;"></div>
            </div>
        `);
    } catch(e) {
        alert(e.message);
    }
}

async function generateInvite(batchId) {
    try {
        const data = await apiFetch(`/batches/${batchId}/invite`, "POST");
        document.getElementById("invite-res").innerHTML = `<div class="badge present">Token: ${data.invite_token}</div><br>Expires: ${new Date(data.expires_at).toLocaleString()}`;
    } catch(e) {
        document.getElementById("invite-res").innerHTML = `<span class="error-msg">${e.message}</span>`;
    }
}

async function createBatch(institutionId) {
    const name = document.getElementById("new-batch-name").value;
    const targetInstitutionId = institutionId || parseInt(document.getElementById("new-batch-institution-id").value);
    if (!name || !targetInstitutionId) {
        alert("Batch name and institution ID are required");
        return;
    }
    try {
        await apiFetch("/batches", "POST", { name, institution_id: targetInstitutionId });
        modalOverlay.classList.add("hidden");
        loadDashboardHome(); 
    } catch(e) {
        alert(e.message);
    }
}

async function openCreateBatchModal(institutionId = null, readOnlyInstitution = false) {
    const institutionField = readOnlyInstitution || institutionId
        ? `
            <div class="input-group">
                <label>Institution ID</label>
                <input type="number" id="new-batch-institution-id" value="${institutionId || ''}" ${readOnlyInstitution ? "readonly" : ""}>
            </div>
        `
        : `
            <div class="input-group">
                <label>Institution</label>
                <select id="new-batch-institution-id">
                    <option value="">Loading institutions...</option>
                </select>
            </div>
        `;

    openModal("Create Batch", `
        <div class="input-group">
            <label>Batch Name</label>
            <input type="text" id="new-batch-name" placeholder="e.g. Batch A">
        </div>
        ${institutionField}
        <div id="institution-help" style="margin-top:0.5rem; color:var(--text-muted); font-size:0.85rem;"></div>
        <button class="btn primary-btn" style="margin-top:1rem;width:100%" onclick="createBatch(${institutionId || 'null'})">Create</button>
    `);

    if (!institutionId && !readOnlyInstitution) {
        const help = document.getElementById("institution-help");
        try {
            const institutions = await apiFetch("/institutions");
            const select = document.getElementById("new-batch-institution-id");
            if (institutions.length === 0) {
                select.innerHTML = '<option value="">No institutions found. Enter an institution ID manually below.</option>';
                select.outerHTML = '<div class="input-group"><label>Institution ID</label><input type="number" id="new-batch-institution-id" placeholder="e.g. 1"></div>';
                help.innerText = "There are no institution users yet. You can still create the batch by entering the target institution ID manually.";
            } else {
                select.innerHTML = '<option value="">Select an institution</option>' + institutions.map(i => {
                    const label = i.name ? `${i.name} (${i.id})` : `Institution ${i.id}`;
                    return `<option value="${i.id}">${label}</option>`;
                }).join("");
                help.innerText = "Choose the institution that should own this batch.";
            }
        } catch (e) {
            const select = document.getElementById("new-batch-institution-id");
            if (select) {
                select.outerHTML = '<div class="input-group"><label>Institution ID</label><input type="number" id="new-batch-institution-id" placeholder="e.g. 1"></div>';
            }
            help.innerText = "Could not load institutions. Enter the institution ID manually.";
        }
    }
}

function openCreateSessionModal() {
    openModal("Create Session", `
        <div class="input-group" style="margin-bottom:1rem">
            <label>Batch ID</label>
            <input type="number" id="session-batch-id">
        </div>
        <div class="input-group" style="margin-bottom:1rem">
            <label>Title</label>
            <input type="text" id="session-title">
        </div>
        <div class="input-group" style="margin-bottom:1rem">
            <label>Date</label>
            <input type="date" id="session-date">
        </div>
        <div class="grid" style="grid-template-columns: 1fr 1fr; gap:1rem; margin-bottom:1rem;">
            <div class="input-group">
                <label>Start Time (HH:MM)</label>
                <input type="time" id="session-start">
            </div>
            <div class="input-group">
                <label>End Time (HH:MM)</label>
                <input type="time" id="session-end">
            </div>
        </div>
        <button class="btn primary-btn" style="width:100%" onclick="submitSession()">Create Session</button>
        <div id="session-res" style="margin-top:1rem"></div>
    `);
}

async function submitSession() {
    const payload = {
        batch_id: parseInt(document.getElementById("session-batch-id").value),
        title: document.getElementById("session-title").value,
        date: document.getElementById("session-date").value,
        start_time: document.getElementById("session-start").value + ":00",
        end_time: document.getElementById("session-end").value + ":00"
    };
    try {
        await apiFetch("/sessions", "POST", payload);
        document.getElementById("session-res").innerHTML = '<div class="badge present">Session created!</div>';
        setTimeout(() => modalOverlay.classList.add("hidden"), 1000);
    } catch(e) {
        document.getElementById("session-res").innerHTML = `<div class="error-msg">${e.message}</div>`;
    }
}

function openMarkAttendanceModal() {
    openModal("Mark Attendance", `
        <div class="input-group" style="margin-bottom:1rem">
            <label>Session ID</label>
            <input type="number" id="mark-session-id">
        </div>
        <div class="input-group" style="margin-bottom:1rem">
            <label>Student ID</label>
            <input type="number" id="mark-student-id" value="${state.user.role === 'student' ? state.user.user_id : ''}" ${state.user.role === 'student' ? 'readonly' : ''}>
        </div>
        <div class="input-group" style="margin-bottom:1rem">
            <label>Status</label>
            <select id="mark-status">
                <option value="present">Present</option>
                <option value="absent">Absent</option>
                <option value="late">Late</option>
            </select>
        </div>
        <button class="btn primary-btn" style="width:100%" onclick="submitAttendance()">Submit Attendance</button>
        <div id="mark-res" style="margin-top:1rem"></div>
    `);
}

async function submitAttendance() {
    const payload = {
        session_id: parseInt(document.getElementById("mark-session-id").value),
        student_id: parseInt(document.getElementById("mark-student-id").value),
        status: document.getElementById("mark-status").value
    };
    try {
        await apiFetch("/attendance/mark", "POST", payload);
        document.getElementById("mark-res").innerHTML = '<div class="badge present">Attendance Recorded!</div>';
        setTimeout(() => modalOverlay.classList.add("hidden"), 1000);
    } catch(e) {
        document.getElementById("mark-res").innerHTML = `<div class="error-msg">${e.message}</div>`;
    }
}

async function viewSessionAttendance() {
    const sessionId = document.getElementById("session-attendance-id").value;
    if(!sessionId) return;
    try {
        const data = await apiFetch(`/sessions/${sessionId}/attendance`);
        
        let tableHtml = `
            <table style="width:100%; text-align:left; border-collapse:collapse;">
                <thead>
                    <tr style="border-bottom: 1px solid var(--glass-border)">
                        <th style="padding:0.5rem">Student ID</th>
                        <th style="padding:0.5rem">Status</th>
                        <th style="padding:0.5rem">Time</th>
                    </tr>
                </thead>
                <tbody>
        `;
        data.forEach(r => {
            tableHtml += `
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.05)">
                    <td style="padding:0.5rem">${r.student_id}</td>
                    <td style="padding:0.5rem"><span class="badge ${r.status}">${r.status}</span></td>
                    <td style="padding:0.5rem">${new Date(r.marked_at).toLocaleTimeString()}</td>
                </tr>
            `;
        });
        tableHtml += `</tbody></table>`;
        
        if (data.length === 0) tableHtml = "<p>No attendance records found for this session.</p>";
        
        openModal(`Attendance for Session ${sessionId}`, tableHtml);
    } catch(e) {
        alert(e.message);
    }
}

// Monitoring Officer Special Functions
let storedMonitoringToken = null;

async function generateMonitoringToken() {
    const apiKey = document.getElementById("monitoring-api-key").value;
    if (!apiKey) return alert("Please enter API key");
    try {
        const data = await apiFetch("/auth/monitoring-token", "POST", { api_key: apiKey, token: "dummy" });
        storedMonitoringToken = data.monitoring_token;
        document.getElementById("monitoring-token-res").innerText = "Token Active: " + storedMonitoringToken.substring(0, 20) + "...";
    } catch(e) {
        alert(e.message);
    }
}

async function viewAllAttendance() {
    if (!storedMonitoringToken) return alert("You must generate a monitoring token first.");
    const container = document.getElementById("monitoring-data");
    container.innerHTML = '<div class="spinner"></div>';
    
    try {
        const data = await apiFetch("/monitoring/attendance", "GET", null, storedMonitoringToken);
        
        let tableHtml = `
            <div class="glass-card" style="padding:1rem; margin-top:1rem; overflow-x:auto;">
            <table style="width:100%; text-align:left; border-collapse:collapse;">
                <thead>
                    <tr style="border-bottom: 1px solid var(--glass-border)">
                        <th style="padding:0.5rem">Record ID</th>
                        <th style="padding:0.5rem">Session ID</th>
                        <th style="padding:0.5rem">Student ID</th>
                        <th style="padding:0.5rem">Status</th>
                        <th style="padding:0.5rem">Timestamp</th>
                    </tr>
                </thead>
                <tbody>
        `;
        data.forEach(r => {
            tableHtml += `
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.05)">
                    <td style="padding:0.5rem">${r.id}</td>
                    <td style="padding:0.5rem">${r.session_id}</td>
                    <td style="padding:0.5rem">${r.student_id}</td>
                    <td style="padding:0.5rem"><span class="badge ${r.status}">${r.status}</span></td>
                    <td style="padding:0.5rem">${new Date(r.marked_at).toLocaleString()}</td>
                </tr>
            `;
        });
        tableHtml += `</tbody></table></div>`;
        
        if (data.length === 0) tableHtml = "<p>No system attendance records found.</p>";
        
        container.innerHTML = tableHtml;
    } catch (e) {
        container.innerHTML = `<div class="error-msg">${e.message}</div>`;
    }
}

function openModal(title, html) {
    modalTitle.innerText = title;
    modalBody.innerHTML = html;
    modalOverlay.classList.remove("hidden");
}

// Start
init();
