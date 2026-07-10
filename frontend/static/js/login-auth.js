/**
 * login-auth.js — Firebase Auth for login.html
 * Student ID is mapped to email as: studentId@library.local
 * Demo mode: ID=1234 / password=1234 accepted without Firebase.
 */

import { initializeApp }              from "https://www.gstatic.com/firebasejs/10.12.2/firebase-app.js";
import { getAuth, signInWithEmailAndPassword, onAuthStateChanged }
                                       from "https://www.gstatic.com/firebasejs/10.12.2/firebase-auth.js";

const firebaseConfig = window.FIREBASE_CONFIG || {
  apiKey:            "YOUR_API_KEY",
  authDomain:        "YOUR_PROJECT.firebaseapp.com",
  projectId:         "YOUR_PROJECT_ID",
  storageBucket:     "YOUR_PROJECT.appspot.com",
  messagingSenderId: "YOUR_SENDER_ID",
  appId:             "YOUR_APP_ID",
};

const isConfigured = firebaseConfig.apiKey && firebaseConfig.apiKey !== "YOUR_API_KEY";

const loginForm     = document.getElementById("loginForm");
const studentIdInput = document.getElementById("loginStudentId");
const passwordInput = document.getElementById("loginPassword");
const loginBtn      = document.getElementById("loginBtn");
const loginError    = document.getElementById("loginError");

function showError(msg) {
  loginError.textContent = msg;
  loginError.classList.remove("hidden");
}
function clearError() {
  loginError.classList.add("hidden");
}

if (isConfigured) {
  const app  = initializeApp(firebaseConfig);
  const auth = getAuth(app);

  // If already signed in, go straight to main app
  onAuthStateChanged(auth, (user) => {
    if (user) window.location.replace("/");
  });

  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    clearError();
    const sid = studentIdInput.value.trim();
    const pwd = passwordInput.value;
    if (!sid || !pwd) { showError("Enter your Student ID and password."); return; }

    loginBtn.disabled    = true;
    loginBtn.textContent = "Signing in…";
    try {
      // Map student ID → email
      const email = sid.toLowerCase() + "@library.local";
      await signInWithEmailAndPassword(auth, email, pwd);
      sessionStorage.setItem("studentId", sid);
      window.location.replace("/");
    } catch (err) {
      const map = {
        "auth/invalid-email":      "Invalid Student ID format.",
        "auth/user-not-found":     "No account found for that Student ID.",
        "auth/wrong-password":     "Incorrect password.",
        "auth/too-many-requests":  "Too many attempts. Please wait.",
        "auth/invalid-credential": "Invalid Student ID or password.",
      };
      showError(map[err.code] || `Error: ${err.code}`);
    } finally {
      loginBtn.disabled    = false;
      loginBtn.textContent = "Sign in";
    }
  });

} else {
  // ── Demo mode ──
  loginForm.addEventListener("submit", (e) => {
    e.preventDefault();
    clearError();
    const sid = studentIdInput.value.trim();
    const pwd = passwordInput.value;
    if (!sid || !pwd) { showError("Enter your Student ID and password."); return; }
    if (sid === "1234" && pwd === "1234") {
      sessionStorage.setItem("studentId", sid);
      sessionStorage.setItem("demoUser", "1");
      window.location.replace("/");
    } else {
      showError("Invalid Student ID or password. (Use 1234 / 1234 for demo)");
    }
  });
}
