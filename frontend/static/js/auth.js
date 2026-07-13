/**
 * auth.js — Firebase Auth for index.html (main app)
 * Redirects to /login if not authenticated.
 */

import { initializeApp }           from "https://www.gstatic.com/firebasejs/10.12.2/firebase-app.js";
import { getAuth, onAuthStateChanged, signOut }
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

if (isConfigured) {
  const app  = initializeApp(firebaseConfig);
  const auth = getAuth(app);

  onAuthStateChanged(auth, (user) => {
    if (user) {
      const sid = user.email?.split("@")[0] || sessionStorage.getItem("studentId") || "student";
      sessionStorage.setItem("studentId", sid);
      window._onAuthSignIn?.({ email: user.email, displayName: sid, uid: user.uid });
      // Persist student record — best-effort
      fetch("/api/students", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ student_id: sid, firebase_uid: user.uid, email: user.email || "" }),
      }).catch(() => {});
    } else {
      // No Firebase session — fall back to demo/local account stored in sessionStorage.
      // This handles the case where the user logged in with a demo or locally-registered
      // account (which skips Firebase sign-in) even when Firebase is configured.
      const demoUser = sessionStorage.getItem("demoUser");
      const sid      = sessionStorage.getItem("studentId");
      if (demoUser && sid) {
        window._onAuthSignIn?.({ email: sid + "@demo", displayName: sid, uid: "demo" });
      } else {
        window.location.replace("/login");
      }
    }
  });

  window._firebaseSignOut = () => {
    sessionStorage.clear();
    signOut(auth).then(() => window.location.replace("/login"));
  };

} else {
  // Demo mode — check sessionStorage
  const demoUser = sessionStorage.getItem("demoUser");
  const sid      = sessionStorage.getItem("studentId");
  if (!demoUser || !sid) {
    window.location.replace("/login");
  } else {
    window._onAuthSignIn?.({ email: sid + "@demo", displayName: sid, uid: "demo" });
  }
  window._firebaseSignOut = () => {
    sessionStorage.clear();
    window.location.replace("/login");
  };
}
