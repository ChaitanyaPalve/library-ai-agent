/**
 * login-auth.js — Firebase Auth for login.html
 *
 * Demo accounts (always work, no Firebase needed):
 *   1234  / 123456
 *   edunet / edunet
 *
 * Custom accounts: stored in localStorage as
 *   "lib_users" → { [studentId]: { name, passwordHash } }
 *   (SHA-256 hex of the password — good enough for a demo app)
 *
 * Firebase mode: maps studentId → studentId@library.local email.
 */

import { initializeApp }              from "https://www.gstatic.com/firebasejs/10.12.2/firebase-app.js";
import { getAuth, signInWithEmailAndPassword,
         createUserWithEmailAndPassword,
         onAuthStateChanged }          from "https://www.gstatic.com/firebasejs/10.12.2/firebase-auth.js";

const firebaseConfig = window.FIREBASE_CONFIG || {
  apiKey:            "YOUR_API_KEY",
  authDomain:        "YOUR_PROJECT.firebaseapp.com",
  projectId:         "YOUR_PROJECT_ID",
  storageBucket:     "YOUR_PROJECT.appspot.com",
  messagingSenderId: "YOUR_SENDER_ID",
  appId:             "YOUR_APP_ID",
};

const isConfigured = firebaseConfig.apiKey && firebaseConfig.apiKey !== "YOUR_API_KEY";

// ── DOM refs ──────────────────────────────────────────────────────────────────
const loginForm      = document.getElementById("loginForm");
const sidInput       = document.getElementById("loginStudentId");
const pwdInput       = document.getElementById("loginPassword");
const loginBtn       = document.getElementById("loginBtn");
const loginError     = document.getElementById("loginError");
const registerPanel  = document.getElementById("registerPanel");
const registerToggle = document.getElementById("registerToggleBtn");
const registerForm   = document.getElementById("registerForm");
const registerBtn    = document.getElementById("registerBtn");
const regName        = document.getElementById("regName");
const regSid         = document.getElementById("regStudentId");
const regPwd         = document.getElementById("regPassword");
const registerError  = document.getElementById("registerError");
const registerSuccess = document.getElementById("registerSuccess");

// ── Built-in demo credentials ────────────────────────────────────────────────
const DEMO_ACCOUNTS = {
  "1234":    "123456",
  "edunet":  "edunet",
};

// ── Helpers ───────────────────────────────────────────────────────────────────
function showError(el, msg)   { el.textContent = msg; el.classList.remove("hidden"); }
function clearError(el)       { el.classList.add("hidden"); }
function showSuccess(el, msg) { el.textContent = msg; el.classList.remove("hidden"); }

async function sha256(str) {
  const buf    = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(str));
  return Array.from(new Uint8Array(buf)).map((b) => b.toString(16).padStart(2, "0")).join("");
}

function getUsers() {
  try { return JSON.parse(localStorage.getItem("lib_users") || "{}"); } catch { return {}; }
}
function saveUsers(u) { localStorage.setItem("lib_users", JSON.stringify(u)); }

// ── Demo-pill auto-fill ───────────────────────────────────────────────────────
document.querySelectorAll(".demo-pill").forEach((pill) => {
  pill.addEventListener("click", () => {
    sidInput.value = pill.dataset.id;
    pwdInput.value = pill.dataset.pwd;
    sidInput.focus();
    clearError(loginError);
  });
});

// ── Register panel toggle ─────────────────────────────────────────────────────
registerToggle.addEventListener("click", () => {
  const open = registerPanel.classList.toggle("open");
  registerToggle.setAttribute("aria-expanded", String(open));
  registerPanel.setAttribute("aria-hidden", String(!open));
  registerToggle.textContent = open ? "− Hide registration" : "＋ Register your own Student ID";
  if (open) regName.focus();
});

// ── Sign-in logic (shared between demo & Firebase mode) ──────────────────────
async function attemptSignIn(sid, pwd) {
  // 1. Built-in demo accounts
  if (DEMO_ACCOUNTS[sid] !== undefined) {
    if (pwd === DEMO_ACCOUNTS[sid]) return { ok: true };
    return { ok: false, msg: `Incorrect password for demo account "${sid}".` };
  }

  // 2. Custom registered accounts (localStorage)
  const users = getUsers();
  if (users[sid]) {
    const hash = await sha256(pwd);
    if (hash === users[sid].passwordHash) return { ok: true };
    return { ok: false, msg: "Incorrect password." };
  }

  return null; // unknown — let Firebase handle it (or show "not found" in demo mode)
}

// ── Registration logic ────────────────────────────────────────────────────────
async function attemptRegister(name, sid, pwd) {
  if (!name.trim())        return { ok: false, msg: "Please enter your name." };
  if (sid.length < 2)      return { ok: false, msg: "Student ID must be at least 2 characters." };
  if (!/^[A-Za-z0-9_-]+$/.test(sid)) return { ok: false, msg: "Student ID may only contain letters, digits, - and _." };
  if (pwd.length < 4)      return { ok: false, msg: "Password must be at least 4 characters." };
  if (DEMO_ACCOUNTS[sid])  return { ok: false, msg: `"${sid}" is a reserved demo ID. Choose a different one.` };

  const users = getUsers();
  if (users[sid])          return { ok: false, msg: `Student ID "${sid}" is already registered on this device.` };

  const hash = await sha256(pwd);
  users[sid] = { name: name.trim(), passwordHash: hash };
  saveUsers(users);
  return { ok: true };
}

// =============================================================================
// FIREBASE MODE
// =============================================================================
if (isConfigured) {
  const app  = initializeApp(firebaseConfig);
  const auth = getAuth(app);

  onAuthStateChanged(auth, (user) => {
    if (user) window.location.replace("/");
  });

  // ── Sign in ──
  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    clearError(loginError);
    const sid = sidInput.value.trim();
    const pwd = pwdInput.value;
    if (!sid || !pwd) { showError(loginError, "Enter your Student ID and password."); return; }

    loginBtn.disabled    = true;
    loginBtn.textContent = "Signing in…";

    try {
      // Check demo / custom accounts first (no Firebase round-trip needed)
      const local = await attemptSignIn(sid, pwd);
      if (local) {
        if (!local.ok) { showError(loginError, local.msg); return; }
        // Persist to both sessionStorage and localStorage so the session survives
        // across tabs and page reloads on browsers that isolate sessionStorage per tab.
        sessionStorage.setItem("studentId", sid);
        sessionStorage.setItem("demoUser", "1");
        localStorage.setItem("libStudentId", sid);
        localStorage.setItem("libDemoUser", "1");
        window.location.replace("/");
        return;
      }

      // Fallback to Firebase email/password
      const email = sid.toLowerCase() + "@library.local";
      await signInWithEmailAndPassword(auth, email, pwd);
      sessionStorage.setItem("studentId", sid);
      window.location.replace("/");
    } catch (err) {
      const map = {
        "auth/user-not-found":     "No account found for that Student ID.",
        "auth/wrong-password":     "Incorrect password.",
        "auth/too-many-requests":  "Too many attempts. Please wait a moment.",
        "auth/invalid-credential": "Invalid Student ID or password.",
        "auth/invalid-email":      "Invalid Student ID format.",
      };
      showError(loginError, map[err.code] || `Error: ${err.code}`);
    } finally {
      loginBtn.disabled    = false;
      loginBtn.textContent = "Sign in";
    }
  });

  // ── Register (Firebase: create account, then sign in) ──
  registerForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    clearError(registerError);
    clearError(registerSuccess);
    const name = regName.value.trim();
    const sid  = regSid.value.trim();
    const pwd  = regPwd.value;

    registerBtn.disabled    = true;
    registerBtn.textContent = "Creating…";

    try {
      // Save to localStorage regardless (for next-device fallback)
      const reg = await attemptRegister(name, sid, pwd);
      if (!reg.ok) { showError(registerError, reg.msg); return; }

      // Also create in Firebase so Firebase-backed login works
      const email = sid.toLowerCase() + "@library.local";
      try {
        await createUserWithEmailAndPassword(auth, email, pwd);
      } catch (fbErr) {
        if (fbErr.code !== "auth/email-already-in-use") {
          // Non-fatal — local account already saved, just warn
          showError(registerError, `Firebase: ${fbErr.code}. Account saved locally only.`);
        }
      }

      showSuccess(registerSuccess, `Account created for "${sid}" (${name}). You can now sign in!`);
      regName.value = "";
      regSid.value  = "";
      regPwd.value  = "";
    } finally {
      registerBtn.disabled    = false;
      registerBtn.textContent = "Create Account";
    }
  });

// =============================================================================
// DEMO MODE  (no Firebase configured)
// =============================================================================
} else {
  // ── Sign in ──
  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    clearError(loginError);
    const sid = sidInput.value.trim();
    const pwd = pwdInput.value;
    if (!sid || !pwd) { showError(loginError, "Enter your Student ID and password."); return; }

    loginBtn.disabled    = true;
    loginBtn.textContent = "Signing in…";

    try {
      const result = await attemptSignIn(sid, pwd);
      if (result && result.ok) {
        sessionStorage.setItem("studentId", sid);
        sessionStorage.setItem("demoUser", "1");
        localStorage.setItem("libStudentId", sid);
        localStorage.setItem("libDemoUser", "1");
        window.location.replace("/");
      } else if (result && !result.ok) {
        showError(loginError, result.msg);
      } else {
        showError(loginError, "No account found for that Student ID. Use a demo account or register below.");
      }
    } finally {
      loginBtn.disabled    = false;
      loginBtn.textContent = "Sign in";
    }
  });

  // ── Register ──
  registerForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    clearError(registerError);
    registerSuccess.classList.add("hidden");
    const name = regName.value.trim();
    const sid  = regSid.value.trim();
    const pwd  = regPwd.value;

    registerBtn.disabled    = true;
    registerBtn.textContent = "Creating…";

    try {
      const reg = await attemptRegister(name, sid, pwd);
      if (!reg.ok) { showError(registerError, reg.msg); return; }
      showSuccess(registerSuccess, `Account created for "${sid}" (${name}). You can now sign in above!`);
      regName.value = "";
      regSid.value  = "";
      regPwd.value  = "";
    } finally {
      registerBtn.disabled    = false;
      registerBtn.textContent = "Create Account";
    }
  });
}
