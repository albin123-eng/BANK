// base.js (clean version) - works with your FastAPI routes
// Backend: http://127.0.0.1:8000

const API_BASE = "http://127.0.0.1:8000";

// ---------------- Token ----------------
function setToken(token) {
  localStorage.setItem("access_token", token);
}
function getToken() {
  return localStorage.getItem("access_token");
}
function clearToken() {
  localStorage.removeItem("access_token");
}

// ---------------- UI helpers ----------------
function el(id) {
  return document.getElementById(id);
}
function setText(id, text) {
  const node = el(id);
  if (node) node.textContent = text ?? "";
}
function setHTML(id, html) {
  const node = el(id);
  if (node) node.innerHTML = html ?? "";
}
function showMsg(message, type = "info") {
  const node = el("msg");
  if (!node) return;
  node.className = `alert alert-${type}`;
  node.textContent = message;
  node.style.display = "block";
}
function hideMsg() {
  const node = el("msg");
  if (!node) return;
  node.style.display = "none";
}

// ---------------- Fetch helper ----------------
async function apiFetch(path, { method = "GET", json, form, auth = false } = {}) {
  const headers = {};
  let body;

  if (json !== undefined) {
    headers["Content-Type"] = "application/json";
    body = JSON.stringify(json);
  }

  if (form !== undefined) {
    headers["Content-Type"] = "application/x-www-form-urlencoded";
    body = new URLSearchParams(form).toString();
  }

  if (auth) {
    const token = getToken();
    if (!token) throw new Error("You are not logged in.");
    headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}${path}`, { method, headers, body });

  // try parse JSON, otherwise text
  const text = await res.text();
  let data = null;
  try { data = JSON.parse(text); } catch { data = null; }

  if (!res.ok) {
    const detail = data?.detail || text || `Request failed (${res.status})`;
    throw new Error(detail);
  }

  return data ?? text;
}

// ---------------- API functions ----------------
async function registerUser(payload) {
  return apiFetch("/auth/register", { method: "POST", json: payload });
}

async function loginUser(username, password) {
  const data = await apiFetch("/auth/token", {
    method: "POST",
    form: { username, password }
  });

  if (!data?.access_token) throw new Error("Login failed: no token returned.");
  setToken(data.access_token);
  return data;
}

async function loadMyAccount() {
  const data = await apiFetch("/account/me", { auth: true });
  // your backend returns {account_id, balance}
  setText("account_id", data.account_id);
  setText("balance", data.balance);
  return data;
}

async function loadMyTransactions() {
  const txs = await apiFetch("/transactions/me", { auth: true });
  if (!Array.isArray(txs)) return txs;

  const tbody = el("tx_body");
  if (!tbody) return txs;

  tbody.innerHTML = txs.map(tx => `
    <tr>
      <td>${tx.id ?? ""}</td>
      <td>${tx.type ?? ""}</td>
      <td>${tx.amount ?? ""}</td>
      <td>${tx.created_at ?? ""}</td>
    </tr>
  `).join("");

  return txs;
}

async function deposit(amount) {
  return apiFetch("/api/account/deposit", {
    method: "POST",
    json: { amount: Number(amount) },
    auth: true,
  });
}

async function withdraw(amount) {
  return apiFetch("/api/account/withdraw", {
    method: "POST",
    json: { amount: Number(amount) },
    auth: true,
  });
}

async function transfer(to_account_id, amount) {
  return apiFetch("/transfer", {
    method: "POST",
    json: { to_account_id: Number(to_account_id), amount: Number(amount) },
    auth: true,
  });
}

async function loadAllTransactionsAdmin() {
  const txs = await apiFetch("/admin/see_All_transactions", { auth: true });
  if (!Array.isArray(txs)) return txs;

  const tbody = el("admin_tx_body");
  if (!tbody) return txs;

  tbody.innerHTML = txs.map(tx => `
    <tr>
      <td>${tx.id ?? ""}</td>
      <td>${tx.account_id ?? ""}</td>
      <td>${tx.type ?? ""}</td>
      <td>${tx.amount ?? ""}</td>
      <td>${tx.created_at ?? ""}</td>
    </tr>
  `).join("");

  return txs;
}

// ---------------- Page wiring ----------------
function protectPageIfNeeded() {
  // If the page has this meta tag: <meta name="requires-auth" content="true">
  const meta = document.querySelector('meta[name="requires-auth"]');
  if (!meta) return;

  if (!getToken()) {
    window.location.href = "/login";
  }
}

function setLoggedInBadge() {
  setText("logged_in", getToken() ? "Yes" : "No");
}

// Disable submit button while async runs
async function withButtonDisabled(form, fn) {
  const btn = form.querySelector('button[type="submit"]');
  if (btn) btn.disabled = true;
  try {
    await fn();
  } finally {
    if (btn) btn.disabled = false;
  }
}

document.addEventListener("DOMContentLoaded", () => {
  hideMsg();
  protectPageIfNeeded();
  setLoggedInBadge();

  // -------- Register page --------
  const registerForm = el("registerForm");
  if (registerForm) {
    registerForm.addEventListener("submit", (e) => {
      e.preventDefault();

      withButtonDisabled(registerForm, async () => {
        try {
          const fd = new FormData(registerForm);
          await registerUser({
            username: fd.get("username"),
            email: fd.get("email"),
            first_name: fd.get("first_name"),
            last_name: fd.get("last_name"),
            password: fd.get("password"),
          });

          showMsg("Registered successfully! Redirecting to login...", "success");
          registerForm.reset();

          setTimeout(() => {
            window.location.href = "/login";
          }, 700);

        } catch (err) {
          showMsg(err.message, "danger");
        }
      });
    });
  }

  // -------- Login page --------
  const loginForm = el("loginForm");
  if (loginForm) {
    loginForm.addEventListener("submit", (e) => {
      e.preventDefault();

      withButtonDisabled(loginForm, async () => {
        try {
          const fd = new FormData(loginForm);
          await loginUser(fd.get("username"), fd.get("password"));

          showMsg("Login successful! Redirecting...", "success");
          setTimeout(() => {
            window.location.href = "/account";
          }, 500);

        } catch (err) {
          showMsg(err.message, "danger");
        }
      });
    });
  }

  // -------- Logout button (in layout) --------
  const logoutBtn = el("logoutBtn");
  if (logoutBtn) {
    logoutBtn.addEventListener("click", () => {
      clearToken();
      setLoggedInBadge();
      showMsg("Logged out.", "info");
      // optional: send them to login
      setTimeout(() => window.location.href = "/login", 400);
    });
  }

  // -------- Account auto-load (if elements exist) --------
  // On account/deposit/withdraw/transfer/transactions pages
  if (getToken() && el("account_id") && el("balance")) {
    loadMyAccount().catch(err => showMsg(err.message, "danger"));
  }
  if (getToken() && el("tx_body")) {
    loadMyTransactions().catch(err => showMsg(err.message, "danger"));
  }

  // -------- Deposit --------
  const depositForm = el("depositForm");
  if (depositForm) {
    depositForm.addEventListener("submit", (e) => {
      e.preventDefault();

      withButtonDisabled(depositForm, async () => {
        try {
          const fd = new FormData(depositForm);
          await deposit(fd.get("amount"));
          showMsg("Deposit successful.", "success");
          await loadMyAccount();
          await loadMyTransactions().catch(() => {});
          depositForm.reset();
        } catch (err) {
          showMsg(err.message, "danger");
        }
      });
    });
  }

  // -------- Withdraw --------
  const withdrawForm = el("withdrawForm");
  if (withdrawForm) {
    withdrawForm.addEventListener("submit", (e) => {
      e.preventDefault();

      withButtonDisabled(withdrawForm, async () => {
        try {
          const fd = new FormData(withdrawForm);
          await withdraw(fd.get("amount"));
          showMsg("Withdraw successful.", "success");
          await loadMyAccount();
          await loadMyTransactions().catch(() => {});
          withdrawForm.reset();
        } catch (err) {
          showMsg(err.message, "danger");
        }
      });
    });
  }

  // -------- Transfer --------
  const transferForm = el("transferForm");
  if (transferForm) {
    transferForm.addEventListener("submit", (e) => {
      e.preventDefault();

      withButtonDisabled(transferForm, async () => {
        try {
          const fd = new FormData(transferForm);
          await transfer(fd.get("to_account_id"), fd.get("amount"));
          showMsg("Transfer successful.", "success");
          await loadMyAccount();
          await loadMyTransactions().catch(() => {});
          transferForm.reset();
        } catch (err) {
          showMsg(err.message, "danger");
        }
      });
    });
  }

  // -------- Admin (optional button) --------
  const adminBtn = el("loadAdminTxBtn");
  if (adminBtn) {
    adminBtn.addEventListener("click", () => {
      withButtonDisabled({ querySelector: () => adminBtn }, async () => {
        try {
          await loadAllTransactionsAdmin();
          showMsg("Admin transactions loaded.", "success");
        } catch (err) {
          showMsg(err.message, "danger");
        }
      });
    });
  }
});
async function loadMyAccount() {
  const data = await apiFetch("/api/account/me", { auth: true });
  setText("account_id", data.account_id);
  setText("balance", data.balance);
  return data;
}


// Expose some functions for inline buttons (like onclick="loadMyAccount()")
window.loadMyAccount = loadMyAccount;
window.loadMyTransactions = loadMyTransactions;
window.loadAllTransactionsAdmin = loadAllTransactionsAdmin;

