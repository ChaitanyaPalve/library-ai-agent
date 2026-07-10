/**
 * auth.js — Firebase Authentication integration (ES Module)
 *
 * Reads Firebase config from window.FIREBASE_CONFIG (injected by the server
 * via a meta tag or env var) or falls back to a placeholder.
 *
 * Wires up:
 *   - Email/password sign-in via #loginForm
 *   - Google sign-in via #googleSignInBtn
 *   - Auth state observer → calls window._onAuthSignIn / window._onAuthSignOut
 *   - window._firebaseSignOut exposed for the Sign out button in app.js
 *
 * To use:
 *   1. Create a Firebase project at https://console.firebase.google.com/
 *   2. Enable Email/Password and Google providers under Authentication > Sign-in method
 *   3. Copy your Firebase web config into .env as FIREBASE_CONFIG (JSON string)
 *      or set window.FIREBASE_CONFIG before this script loads.
 *   4. In app.py, optionally inject the config into the HTML template.
 */

import { initializeApp }                              from "https://www.gstatic.com/firebasejs/10.12.2/firebase-app.js";
import {
  getAuth,
  onAuthStateChanged,
  signInWithEmailAndPassword,
  signInWithPopup,
  GoogleAuthProvider,
  signOut,
} from "https://www.gstatic.com/firebasejs/10.12.2/firebase-auth.js";

// ---------------------------------------------------------------------------
// Firebase config — reads from window.FIREBASE_CONFIG or falls back to stub.
// Replace the stub values with your real project config.
// ---------------------------------------------------------------------------
const firebaseConfig = window.FIREBASE_CONFIG || {
  apiKey:            "YOUR_API_KEY",
  authDomain:        "YOUR_PROJECT.firebaseapp.com",
  projectId:         "YOUR_PROJECT_ID",
  storageBucket:     "YOUR_PROJECT.appspot.com",
  messagingSenderId: "YOUR_SENDER_ID",
  appId:             "YOUR_APP_ID",
};

// Guard: only initialise if a real config is provided.
const isConfigured = firebaseConfig.apiKey && firebaseConfig.apiKey !== "YOUR_API_KEY";

if (!isConfigured) {
  console.info(
    "[auth.js] Firebase config not set — login overlay will work in demo mode only. " +
    "Set window.FIREBASE_CONFIG or FIREBASE_CONFIG env var."
  );
}

// ---------------------------------------------------------------------------
// DOM refs
// ---------------------------------------------------------------------------
const loginForm      = document.getElementById("loginForm");
const loginEmail     = document.getElementById("loginEmail");
const loginPassword  = document.getElementById("loginPassword");
const loginError     = document.getElementById("loginError");
const loginBtn       = document.getElementById("loginBtn");
const googleSignInBtn = document.getElementById("googleSignInBtn");

function showLoginError(msg) {
  loginError.textContent = msg;
  loginError.classList.remove("hidden");
}
function clearLoginError() {
  loginError.textContent = "";
  loginError.classList.add("hidden");
}

// ---------------------------------------------------------------------------
// Initialise Firebase (only if configured)
// ---------------------------------------------------------------------------
if (isConfigured) {
  const app      = initializeApp(firebaseConfig);
  const auth     = getAuth(app);
  const provider = new GoogleAuthProvider();

  // ── Auth state observer ──
  onAuthStateChanged(auth, (user) => {
    if (user) {
      window._onAuthSignIn?.(user);
      // Persist student record in MongoDB — best-effort, fire-and-forget.
      const sid = (window._getStudentId?.() || user.email?.split("@")[0] || "")
        .replace(/[^A-Za-z0-9_\-]/g, "")
        .slice(0, 20);
      if (sid.length >= 2) {
        fetch("/api/students", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ student_id: sid, firebase_uid: user.uid, email: user.email || "" }),
        }).catch(() => {});   // silently ignore network errors
      }
    } else {
      window._onAuthSignOut?.();
    }
  });

  // ── Email / password sign-in ──
  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    clearLoginError();
    const email    = loginEmail.value.trim();
    const password = loginPassword.value;
    if (!email || !password) { showLoginError("Please enter email and password."); return; }

    loginBtn.disabled    = true;
    loginBtn.textContent = "Signing in…";
    try {
      await signInWithEmailAndPassword(auth, email, password);
      // onAuthStateChanged fires and calls window._onAuthSignIn
    } catch (err) {
      showLoginError(friendlyFirebaseError(err.code));
    } finally {
      loginBtn.disabled    = false;
      loginBtn.textContent = "Sign in";
    }
  });

  // ── Google sign-in ──
  googleSignInBtn.addEventListener("click", async () => {
    clearLoginError();
    try {
      await signInWithPopup(auth, provider);
    } catch (err) {
      if (err.code !== "auth/popup-closed-by-user") {
        showLoginError(friendlyFirebaseError(err.code));
      }
    }
  });

  // ── Sign out (exposed globally for app.js) ──
  window._firebaseSignOut = () => signOut(auth);

} else {
  // ── Demo mode — login overlay dismisses on submit with any non-empty credentials ──
  loginForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const email = loginEmail.value.trim();
    if (!email) { showLoginError("Enter an email address to continue."); return; }
    // Synthesise a user-like object for the callback
    window._onAuthSignIn?.({ email, displayName: email.split("@")[0], uid: "demo" });
  });

  googleSignInBtn.addEventListener("click", () => {
    window._onAuthSignIn?.({ email: "demo@library.ai", displayName: "Demo User", uid: "demo" });
  });

  window._firebaseSignOut = () => window._onAuthSignOut?.();
}

// ---------------------------------------------------------------------------
// Human-readable Firebase error messages
// ---------------------------------------------------------------------------
function friendlyFirebaseError(code) {
  const map = {
    "auth/invalid-email":          "Invalid email address.",
    "auth/user-not-found":         "No account found for that email.",
    "auth/wrong-password":         "Incorrect password.",
    "auth/too-many-requests":      "Too many attempts. Please wait and try again.",
    "auth/network-request-failed": "Network error. Check your connection.",
    "auth/email-already-in-use":   "An account with that email already exists.",
    "auth/weak-password":          "Password must be at least 6 characters.",
    "auth/invalid-credential":     "Invalid credentials. Check your email and password.",
  };
  return map[code] || `Authentication error (${code}).`;
}
