/**
 * Library AI Agent — Frontend JavaScript
 *
 * Handles:
 *   - Sticky nav panel switching + filter chip strip
 *   - Search form (nav search bar) → POST /api/search
 *   - Pin-grid masonry card rendering with colour-block thumbnails
 *   - Reserve / waitlist modal → POST /api/reserve  (with duplicate-hold guard)
 *   - Cancel reservation → DELETE /api/reserve/:id
 *   - All Books panel → GET /api/books
 *   - Dashboard: high-demand + IBM Robo automation alerts
 *   - Light / dark theme toggle (persisted to localStorage)
 *   - Firebase Auth integration (login overlay + sign-in/sign-out)
 *   - Student ID live validation
 */

// ─────────────────────────────────────────────────────────────────────────────
// State
// ─────────────────────────────────────────────────────────────────────────────
const state = {
  studentId: sessionStorage.getItem("studentId") || "1234",
  reservations: [],
  activeFilter: "all",
  homeGenre: "all",
};

// ─────────────────────────────────────────────────────────────────────────────
// DOM refs
// ─────────────────────────────────────────────────────────────────────────────
const $ = (id) => document.getElementById(id);

const searchBtn         = $("searchBtn");
const queryInput        = $("queryInput");
const studentIdInput    = $("studentId");
const studentIdError    = $("studentIdError");
const nluInsights       = $("nluInsights");
const aiMessage         = $("aiMessage");
const aiMessageText     = $("aiMessageText");
const resultsSection    = $("resultsSection");
const booksGrid         = $("booksGrid");
const resultsTitle      = $("resultsTitle");
const emptyState        = $("emptyState");
const loadingState      = $("loadingState");
const reserveModal      = $("reserveModal");
const modalTitle        = $("modalTitle");
const modalSubtitle     = $("modalSubtitle");
const modalBody         = $("modalBody");
const modalConfirm      = $("modalConfirm");
const modalCancel       = $("modalCancel");
const modalClose        = $("modalClose");
const reservationsList  = $("reservationsList");
const highDemandList    = $("highDemandList");
const automationAlerts  = $("automationAlerts");
const runRoboBtn        = $("runRoboBtn");
const toastEl           = $("toast");
const homeBooksGrid     = $("homeBooksGrid");
const homeBooksCount    = $("homeBooksCount");
const homeBooksLoading  = $("homeBooksLoading");
const homeBooksSection  = $("homeBooksSection");

// ─────────────────────────────────────────────────────────────────────────────
// Theme toggle  (persisted to localStorage)
// ─────────────────────────────────────────────────────────────────────────────
const htmlEl         = document.documentElement;
const themeToggle    = $("themeToggle");
const themeIconLight = $("themeIconLight");
const themeIconDark  = $("themeIconDark");

function applyTheme(theme) {
  htmlEl.setAttribute("data-theme", theme);
  if (theme === "dark") {
    themeIconLight.classList.add("hidden");
    themeIconDark.classList.remove("hidden");
  } else {
    themeIconLight.classList.remove("hidden");
    themeIconDark.classList.add("hidden");
  }
}

// Restore from storage or default to light
applyTheme(localStorage.getItem("theme") || "light");

themeToggle.addEventListener("click", () => {
  const next = htmlEl.getAttribute("data-theme") === "dark" ? "light" : "dark";
  applyTheme(next);
  localStorage.setItem("theme", next);
});

function validateStudentIdInput(value) {
  if (!value) return "Student ID is required";
  return null;
}

// ─────────────────────────────────────────────────────────────────────────────
// Panel navigation
// ─────────────────────────────────────────────────────────────────────────────
function switchPanel(panelName) {
  document.querySelectorAll(".panel").forEach((p) => p.classList.remove("active"));
  const target = document.getElementById(`panel-${panelName}`);
  if (target) target.classList.add("active");
  if (panelName === "reservations") fetchAndRenderReservations();
  if (panelName === "dashboard")    loadDashboard();
  if (panelName === "search")       { hideResults(); loadHomeBooks(state.homeGenre); }
}

$("navResBtn").addEventListener("click",   () => switchPanel("reservations"));
$("navRecsBtn").addEventListener("click",  () => { switchPanel("recommendations"); loadRecommendations(); });
$("navDashBtn").addEventListener("click",  () => switchPanel("dashboard"));
$("homeBtn").addEventListener("click", (e) => { e.preventDefault(); switchPanel("search"); });

// ─── Side Drawer ─────────────────────────────────────────────────────────────
const sideDrawer  = $("sideDrawer");
const drawerScrim = $("drawerScrim");

function openDrawer()  {
  sideDrawer.classList.add("open");
  drawerScrim.classList.add("open");
  $("menuToggle").setAttribute("aria-expanded", "true");
}
function closeDrawer() {
  sideDrawer.classList.remove("open");
  drawerScrim.classList.remove("open");
  $("menuToggle").setAttribute("aria-expanded", "false");
}

$("menuToggle").addEventListener("click", openDrawer);
$("drawerClose").addEventListener("click", closeDrawer);
drawerScrim.addEventListener("click", closeDrawer);

// Drawer panel links
sideDrawer.querySelectorAll(".drawer__item[data-panel]").forEach((btn) => {
  btn.addEventListener("click", () => { switchPanel(btn.dataset.panel); closeDrawer(); });
});

// Drawer genre links
sideDrawer.querySelectorAll(".drawer__item[data-genre]").forEach((btn) => {
  btn.addEventListener("click", () => {
    const genre = btn.dataset.genre;
    switchPanel("search");
    setHomeGenre(genre);
    closeDrawer();
  });
});

// Unified genre strip — browse books & sync active state
document.querySelectorAll("#homeGenreStrip .filter-chip").forEach((chip) => {
  chip.addEventListener("click", () => {
    setHomeGenre(chip.dataset.genre);
  });
});

function setHomeGenre(genre) {
  document.querySelectorAll("#homeGenreStrip .filter-chip").forEach((c) => c.classList.remove("filter-chip--active"));
  const chip = document.querySelector(`#homeGenreStrip .filter-chip[data-genre="${genre}"]`);
  if (chip) chip.classList.add("filter-chip--active");
  state.homeGenre = genre;
  loadHomeBooks(genre, true);
}

// ─────────────────────────────────────────────────────────────────────────────
// Search
// ─────────────────────────────────────────────────────────────────────────────
searchBtn.addEventListener("click", doSearch);
queryInput.addEventListener("keydown", (e) => { if (e.key === "Enter") doSearch(); });

async function doSearch() {
  const query = queryInput.value.trim();
  if (!query) return;
  state.studentId = sessionStorage.getItem("studentId") || state.studentId || "anonymous";

  switchPanel("search");
  setLoading(true);
  hideResults();
  homeBooksSection.classList.add("hidden");

  try {
    const res = await fetch("/api/search", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ student_id: state.studentId, query }),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    setLoading(false);

    if (data.search_terms && data.search_terms.length) {
      nluInsights.innerHTML =
        '<span class="nlu-label">Watson NLU extracted:</span>' +
        data.search_terms.map((t) => `<span class="nlu-pill">${esc(t)}</span>`).join("");
      nluInsights.classList.remove("hidden");
    }

    if (data.ai_message) {
      aiMessageText.textContent = data.ai_message;
      aiMessage.classList.remove("hidden");
    }

    if (data.books && data.books.length > 0) {
      resultsTitle.textContent = `${data.total} book${data.total !== 1 ? "s" : ""} found`;
      booksGrid.innerHTML = data.books.map((b, i) => renderPinCard(b, i)).join("");
      resultsSection.classList.remove("hidden");
      attachReserveListeners(booksGrid);
      attachTagListeners(booksGrid);
    } else {
      emptyState.classList.remove("hidden");
    }

  } catch {
    setLoading(false);
    showToast("Search failed. Check your connection.", true);
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Home books loader (replaces old All Books panel)
// ─────────────────────────────────────────────────────────────────────────────
let _homeBooksGenreLoaded = "";

async function loadHomeBooks(genre = "all", force = false) {
  if (!force && _homeBooksGenreLoaded === genre) return;

  // Show skeleton placeholders while loading
  homeBooksGrid.innerHTML = Array.from({length: 8}, () => `
    <div class="skeleton-card">
      <div class="sk-img skeleton"></div>
      <div class="sk-line skeleton"></div>
      <div class="sk-line sk-line--short skeleton"></div>
    </div>`).join("");
  homeBooksLoading.classList.remove("hidden");
  homeBooksCount.textContent = "";
  homeBooksSection.classList.remove("hidden");

  try {
    const url = genre && genre !== "all"
      ? `/api/books?subject=${encodeURIComponent(genre)}&limit=200`
      : `/api/books?limit=200`;
    const res  = await fetch(url);
    const data = await res.json();
    homeBooksLoading.classList.add("hidden");

    homeBooksCount.textContent = `${data.total} book${data.total !== 1 ? "s" : ""}`;
    homeBooksGrid.innerHTML = (data.books || []).map((b, i) => renderPinCard(b, i)).join("");
    attachReserveListeners(homeBooksGrid);
    attachTagListeners(homeBooksGrid);
    _homeBooksGenreLoaded = genre;
  } catch {
    homeBooksLoading.classList.add("hidden");
    showToast("Failed to load books.", true);
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Pin card renderer
// ─────────────────────────────────────────────────────────────────────────────
const RATIOS = ["ratio-square", "ratio-portrait", "ratio-tall", "ratio-xl"];

function renderPinCard(book, index) {
  const avail       = book.available_copies > 0;
  const ratio       = RATIOS[index % RATIOS.length];
  const thumbClass  = `pin-thumb--${index % 18}`;
  const primaryTag  = (book.subject_tags && book.subject_tags[0]) ? book.subject_tags[0] : null;
  const demandBadge = book.demand_score >= 5
    ? `<div class="pin-card__demand-badge">🔥 ${book.demand_score}</div>` : "";
  const overlayPill = primaryTag
    ? `<div class="pin-card__overlay-pill">${esc(primaryTag)}</div>` : "";
  const tags = (book.subject_tags || []).slice(1, 4)
    .map((t) => `<span class="pin-tag" data-tag="${esc(t)}">${esc(t)}</span>`).join("");

  const badgeClass = avail ? "avail-badge--available" : "avail-badge--unavailable";
  const badgeText  = avail ? `✓ ${book.available_copies} available` : "✗ Unavailable";
  const btnClass   = avail ? "" : "btn-pin-action--waitlist";
  const btnText    = avail ? "Reserve" : "Waitlist";

  const isbnText   = book.isbn ? `ISBN ${esc(book.isbn)}` : "";
  const copiesText = `${book.total_copies || 1} cop${(book.total_copies || 1) === 1 ? "y" : "ies"} total`;
  const quickInfo  = `<div class="pin-card__quick-info">${isbnText ? isbnText + " · " : ""}${copiesText}</div>`;

  // Book cover: coloured block with title + author overlaid
  const thumbCover = `
    <div class="pin-card__cover-title">${esc(book.title)}</div>
    <div class="pin-card__cover-author">${esc(book.author)}</div>`;

  return `
    <article class="pin-card pin-card--${ratio}" role="listitem"
             data-id="${esc(book._id)}" aria-label="${esc(book.title)}">
      <div class="pin-card__image">
        <div class="pin-card__thumb ${thumbClass}">${thumbCover}</div>
        ${demandBadge}
        ${overlayPill}
        ${quickInfo}
      </div>
      <div class="pin-card__meta">
        <div class="pin-card__title">${esc(book.title)}</div>
        <div class="pin-card__author">${esc(book.author)}</div>
      </div>
      ${tags ? `<div class="pin-card__tags">${tags}</div>` : ""}
      <div class="pin-card__footer">
        <span class="avail-badge ${badgeClass}">${badgeText}</span>
        <button class="btn-pin-action ${btnClass}"
                data-id="${esc(book._id)}"
                data-title="${esc(book.title)}"
                data-author="${esc(book.author)}"
                data-avail="${avail}">
          ${btnText}
        </button>
        <button class="btn-pin-review"
                data-id="${esc(book._id)}"
                data-title="${esc(book.title)}"
                aria-label="Read &amp; write reviews">
          Reviews
        </button>
      </div>
    </article>`;
}

function attachReserveListeners(container = document) {
  container.querySelectorAll(".btn-pin-action").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      openReserveModal(
        btn.dataset.id,
        btn.dataset.title,
        btn.dataset.author,
        btn.dataset.avail === "true"
      );
    });
  });
  container.querySelectorAll(".btn-pin-review").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      openReviewsPanel(btn.dataset.id, btn.dataset.title);
    });
  });
}

// Tag clicks → filter books by that tag
function attachTagListeners(container = document) {
  container.querySelectorAll(".pin-tag[data-tag]").forEach((tag) => {
    tag.addEventListener("click", (e) => {
      e.stopPropagation();
      const genre = tag.dataset.tag;
      // Try to match an existing genre chip; otherwise do a search
      const chip = document.querySelector(`#homeGenreStrip .filter-chip[data-genre="${genre}"]`);
      if (chip) {
        setHomeGenre(genre);
      } else {
        queryInput.value = genre;
        doSearch();
      }
    });
  });
}

// ─────────────────────────────────────────────────────────────────────────────
// Reservation modal
// ─────────────────────────────────────────────────────────────────────────────
let _pendingBookId = null;

function openReserveModal(bookId, title, author, available) {
  const sid = state.studentId;
  _pendingBookId = bookId;
  modalTitle.textContent    = available ? "Reserve this book" : "Join the waitlist";
  modalSubtitle.textContent = `"${title}" by ${author}`;
  modalBody.innerHTML = available
    ? `<p>You are about to reserve a copy for student <strong>${esc(sid)}</strong>.</p>
       <p style="margin-top:8px;color:var(--color-mute);font-size:14px">Held for up to 14 days — IBM Robo will auto-release after that.</p>`
    : `<p>All copies are currently checked out.</p>
       <p style="margin-top:8px;color:var(--color-mute);font-size:14px">Join the waitlist and IBM Robo will promote you automatically when a copy is returned.</p>`;
  modalConfirm.textContent = available ? "Confirm Reservation" : "Join Waitlist";
  reserveModal.classList.remove("hidden");
}

function closeModal() { reserveModal.classList.add("hidden"); }
modalClose.addEventListener("click", closeModal);
modalCancel.addEventListener("click", closeModal);
reserveModal.querySelector(".modal__scrim").addEventListener("click", closeModal);

modalConfirm.addEventListener("click", async () => {
  if (!_pendingBookId) return;
  const bookId = _pendingBookId;
  closeModal();

  try {
    const res = await fetch("/api/reserve", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ student_id: state.studentId, book_id: bookId }),
    });
    const data = await res.json();

    // Show specific error (including duplicate-hold message from backend)
    if (data.error) {
      showToast(data.error, true);
      return;
    }

    state.reservations.push({
      id:         data._id,
      bookId,
      bookTitle:  data.book_title,
      bookAuthor: data.book_author,
      status:     data.status,
      message:    data.ai_message || "",
    });

    const msg = data.status === "active" ? "Reservation confirmed!" : "Added to waitlist.";
    showToast(msg);
    _pendingBookId = null;
    updatePinCardState(bookId, data.status);
  } catch {
    showToast("Reservation failed. Try again.", true);
  }
});

function updatePinCardState(bookId, status) {
  // Update cards in both grids
  document.querySelectorAll(`.pin-card[data-id="${bookId}"]`).forEach((card) => {
    const badge = card.querySelector(".avail-badge");
    const btn   = card.querySelector(".btn-pin-action");
    if (badge) {
      badge.className = "avail-badge avail-badge--unavailable";
      badge.textContent = "✗ Unavailable";
    }
    if (btn) {
      btn.className = "btn-pin-action btn-pin-action--waitlist";
      btn.textContent = "Waitlist";
      btn.dataset.avail = "false";
    }
  });
}

// ─────────────────────────────────────────────────────────────────────────────
// Reservations panel
// ─────────────────────────────────────────────────────────────────────────────
// ── Fetch active reservations from API (called on panel open) ──────────────
async function fetchAndRenderReservations() {
  reservationsList.innerHTML = `
    <div class="state-card">
      <div class="lib-spinner" aria-hidden="true"><div class="lib-spinner__ring"></div></div>
      <p class="state-card__sub">Loading your holds…</p>
    </div>`;

  try {
    const sid = state.studentId;
    // Fetch reservations for this student via profile endpoint (has history)
    const res  = await fetch(`/api/profile/${encodeURIComponent(sid)}`);
    const data = await res.json();

    // Fetch ALL reservations to find active/waitlisted for this student
    const resRes  = await fetch(`/api/reservations/${encodeURIComponent(sid)}`);
    if (resRes.ok) {
      const resData = await resRes.json();
      const fetched = (resData.reservations || []).map((r) => ({
        id:         r._id,
        bookId:     r.book_id,
        bookTitle:  r.book_title || r.book_id,
        bookAuthor: r.book_author || "",
        status:     r.status,
        message:    "",
      }));
      // Merge: keep any in-session ones not yet in fetched, add fetched ones not in session
      const sessionIds = new Set(state.reservations.map((x) => x.id));
      fetched.forEach((r) => { if (!sessionIds.has(r.id)) state.reservations.push(r); });
    }
  } catch {
    // API may not have the reservations endpoint — fall through to render what we have
  }
  renderReservations();
}

function renderReservations() {
  const active = state.reservations.filter((r) => r.status !== "cancelled");
  if (!state.reservations.length && !active.length) {
    reservationsList.innerHTML = `
      <div class="state-card">
        <svg width="48" height="48" viewBox="0 0 48 48" fill="none" aria-hidden="true">
          <rect x="8" y="12" width="32" height="28" rx="3" fill="var(--color-surface-card)" stroke="var(--color-hairline)" stroke-width="1.5"/>
          <path d="M24 20v12M18 26h12" stroke="var(--color-ash)" stroke-width="1.5" stroke-linecap="round"/>
        </svg>
        <p class="state-card__title">No holds yet</p>
        <p class="state-card__sub">Search for a book and tap Reserve to add your first hold</p>
      </div>`;
    return;
  }

  reservationsList.innerHTML = state.reservations.map((r) => {
    const chipClass = `status-chip status-chip--${r.status}`;
    return `
      <div class="res-card" data-res-id="${esc(r.id)}">
        <div class="res-card__info">
          <div class="res-card__title">${esc(r.bookTitle || "Unknown Book")}</div>
          <div class="res-card__meta">${esc(r.bookAuthor || "")} · Student: ${esc(state.studentId)}</div>
          ${r.message ? `<div class="res-card__message">${esc(r.message)}</div>` : ""}
        </div>
        <div class="res-card__actions">
          <span class="${chipClass}">${r.status}</span>
          ${r.status !== "cancelled"
            ? `<button class="btn-cancel" data-id="${esc(r.id)}" aria-label="Cancel reservation">Cancel</button>`
            : ""}
        </div>
      </div>`;
  }).join("");

  document.querySelectorAll(".btn-cancel").forEach((btn) => {
    btn.addEventListener("click", () => cancelReservation(btn.dataset.id));
  });
}

async function cancelReservation(resId) {
  try {
    const res  = await fetch(`/api/reserve/${resId}`, { method: "DELETE" });
    const data = await res.json();
    if (data.error) { showToast(data.error, true); return; }
    const r = state.reservations.find((x) => x.id === resId);
    if (r) r.status = "cancelled";
    renderReservations();
    showToast("Reservation cancelled.");
  } catch {
    showToast("Cancel failed.", true);
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Dashboard panel (lazy — only fetches when first opened)
// ─────────────────────────────────────────────────────────────────────────────
let _dashboardLoaded = false;

async function loadDashboard() {
  loadOrchStatus();
  loadExplain();

  if (_dashboardLoaded) return;
  highDemandList.innerHTML   = `<p style="color:var(--color-ash);font-size:13px">Loading…</p>`;
  automationAlerts.innerHTML = `<p style="color:var(--color-ash);font-size:13px">Loading…</p>`;

  try {
    const [demandRes, alertsRes] = await Promise.all([
      fetch("/api/books/high-demand?threshold=3"),
      fetch("/api/automation/alerts"),
    ]);
    const demandData = await demandRes.json();
    const alertsData = await alertsRes.json();

    if (demandData.books && demandData.books.length) {
      highDemandList.innerHTML = demandData.books.map((b) => `
        <div class="demand-item">
          <span class="demand-item__title">${esc(b.title)}</span>
          <span class="demand-score">🔥 ${b.demand_score}</span>
        </div>`).join("");
    } else {
      highDemandList.innerHTML = `<p style="color:var(--color-ash);font-size:13px">No high-demand books yet.</p>`;
    }

    if (alertsData.alerts && alertsData.alerts.length) {
      automationAlerts.innerHTML = alertsData.alerts.map((a) => `
        <div class="alert-item">
          <div class="alert-item__type">${esc(a.type)}</div>
          <div class="alert-item__title">${esc(a.title)}</div>
          <div class="alert-item__meta">Demand: ${a.demand_score} · ${
            new Date(a.raised_at).toLocaleDateString("en-US", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" })
          }</div>
        </div>`).join("");
    } else {
      automationAlerts.innerHTML = `<p style="color:var(--color-ash);font-size:13px">No alerts yet. Run Robo Rules to scan the database.</p>`;
    }

    _dashboardLoaded = true;
  } catch {
    showToast("Dashboard failed to load.", true);
  }
}

runRoboBtn.addEventListener("click", async () => {
  runRoboBtn.disabled = true;
  runRoboBtn.textContent = "Running…";
  try {
    const res  = await fetch("/api/automation/run");
    const data = await res.json();
    showToast(
      `Robo ran — ${data.high_demand_alerts.length} demand alerts, ` +
      `${data.expired_reservations.length} expired, ` +
      `${data.low_stock_reorders.length} reorder alerts.`
    );
    _dashboardLoaded = false;   // Force refresh on next open
    loadDashboard();
  } catch {
    showToast("Automation run failed.", true);
  } finally {
    runRoboBtn.disabled = false;
    runRoboBtn.textContent = "Run Robo Rules";
  }
});

// ─────────────────────────────────────────────────────────────────────────────
// Orchestration status
// ─────────────────────────────────────────────────────────────────────────────
const orchStatus      = $("orchStatus");
const refreshStatusBtn = $("refreshStatusBtn");

async function loadOrchStatus() {
  orchStatus.innerHTML = `<p style="color:var(--color-ash);font-size:13px">Checking services…</p>`;
  try {
    const res  = await fetch("/api/status");
    const data = await res.json();
    orchStatus.innerHTML = Object.entries(data.services).map(([key, s]) => {
      const cls   = s.ok ? "ok" : "fail";
      const badge = s.ok ? "Connected" : "Error";
      const detail = s.ok
        ? `<div class="orch-card__detail">${esc(s.detail || "")}</div>
           <div class="orch-card__latency">${s.latency_ms} ms</div>`
        : `<div class="orch-card__error">${esc((s.error || "").slice(0, 120))}</div>
           ${s.fix ? `<div class="orch-card__fix">Fix: ${esc(s.fix)}</div>` : ""}`;
      return `
        <div class="orch-card orch-card--${cls}">
          <div class="orch-card__service">${esc(key.replace("_", " "))}</div>
          <div class="orch-card__label">${esc(s.label)}</div>
          <div class="orch-card__badge orch-card__badge--${cls}">${badge}</div>
          <div class="orch-card__detail" style="margin-top:2px">${esc(s.description)}</div>
          ${detail}
        </div>`;
    }).join("");
  } catch {
    orchStatus.innerHTML = `<p style="color:var(--color-error);font-size:13px">Could not reach /api/status — is the server running?</p>`;
  }
}

refreshStatusBtn.addEventListener("click", loadOrchStatus);

// ─────────────────────────────────────────────────────────────────────────────
// AI Pipeline explainer
// ─────────────────────────────────────────────────────────────────────────────
const explainPanel     = $("explainPanel");
const toggleExplainBtn = $("toggleExplainBtn");
let _explainLoaded = false;

async function loadExplain() {
  if (_explainLoaded) return;
  try {
    const res  = await fetch("/api/explain");
    const data = await res.json();
    const steps = data.pipeline.map((p, i) => `
      ${i > 0 ? '<div class="pipeline-connector"></div>' : ""}
      <div class="pipeline-step">
        <div class="step-num">${p.step}</div>
        <div class="step-body">
          <div class="step-service">${esc(p.service)}</div>
          <div class="step-role">${esc(p.role)}</div>
          <div class="step-desc">${esc(p.what_it_does)}</div>
          <div class="step-output">${esc(p.output)}</div>
          <div class="step-path">${esc(p.ibm_cloud_path)}</div>
        </div>
      </div>`).join("");
    explainPanel.innerHTML = steps +
      `<div class="explain-summary">${esc(data.architecture_summary)}</div>`;
    _explainLoaded = true;
  } catch {
    explainPanel.innerHTML = `<p style="color:var(--color-error);font-size:13px">Could not load AI explanation.</p>`;
  }
}

toggleExplainBtn.addEventListener("click", () => {
  const hidden = explainPanel.classList.toggle("hidden");
  toggleExplainBtn.textContent = hidden ? "Show" : "Hide";
  if (!hidden && !_explainLoaded) loadExplain();
});

// ─────────────────────────────────────────────────────────────────────────────
// Auth integration (auth.js calls these via window)
// ─────────────────────────────────────────────────────────────────────────────
const logoutNavBtn = $("logoutNavBtn");

logoutNavBtn.addEventListener("click", () => {
  if (window._firebaseSignOut) window._firebaseSignOut();
});

window._onAuthSignIn = (user) => {
  const sid = sessionStorage.getItem("studentId") || user.displayName || "student";
  state.studentId = sid;
  studentIdInput.value = sid;
  // Load homepage books and WRTD banner after sign-in
  loadHomeBooks("all");
  loadWRTD();
};

window._getStudentId = () => state.studentId;

// ─────────────────────────────────────────────────────────────────────────────
// Helpers
// ─────────────────────────────────────────────────────────────────────────────
// Initial load — if auth.js doesn't fire _onAuthSignIn before DOMContentLoaded
// (demo mode sets it synchronously via sessionStorage check), load books now.
if (sessionStorage.getItem("studentId")) {
  loadHomeBooks("all");
  loadWRTD();
}

function hideResults() {
  nluInsights.classList.add("hidden");
  aiMessage.classList.add("hidden");
  resultsSection.classList.add("hidden");
  emptyState.classList.add("hidden");
  loadingState.classList.add("hidden");
  homeBooksSection.classList.remove("hidden");
}

function setLoading(on) {
  loadingState.classList.toggle("hidden", !on);
}

let _toastTimer = null;
function showToast(msg, error = false) {
  toastEl.textContent = msg;
  toastEl.className   = "toast" + (error ? " toast--error" : "");
  void toastEl.offsetWidth;   // force reflow so transition fires on re-show
  toastEl.classList.add("toast--visible");
  clearTimeout(_toastTimer);
  _toastTimer = setTimeout(() => toastEl.classList.remove("toast--visible"), 3600);
}

function esc(str) {
  if (str == null) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

// =============================================================================
// REVIEWS  (Watson NLU sentiment analysis)
// =============================================================================

let _currentReviewBookId   = null;
let _currentReviewBookTitle = "";

/**
 * Switch to the reviews panel and load existing reviews for a book.
 * Called when user clicks the "Reviews" button on a book card.
 */
function openReviewsPanel(bookId, bookTitle) {
  _currentReviewBookId    = bookId;
  _currentReviewBookTitle = bookTitle;
  $("reviewsPanelTitle").textContent = `Reviews: ${bookTitle}`;
  $("reviewsPanelSub").textContent   = "Watson NLU sentiment analysis of reader reviews";
  $("reviewTextarea").value          = "";
  $("reviewFormError").classList.add("hidden");
  $("reviewFormCard").classList.remove("hidden");
  switchPanel("reviews");
  _loadReviews(bookId);
}

async function _loadReviews(bookId) {
  const list = $("reviewsList");
  list.innerHTML = `<p style="color:var(--color-ash);font-size:13px">Loading reviews…</p>`;
  try {
    const res  = await fetch(`/api/reviews/${bookId}`);
    const data = await res.json();
    _renderReviews(data.reviews || []);
  } catch {
    list.innerHTML = `<p style="color:var(--color-error);font-size:13px">Could not load reviews.</p>`;
  }
}

function _renderReviews(reviews) {
  const list = $("reviewsList");
  if (!reviews.length) {
    list.innerHTML = `
      <div class="state-card">
        <p class="state-card__title">No reviews yet</p>
        <p class="state-card__sub">Be the first to review this book</p>
      </div>`;
    return;
  }
  list.innerHTML = reviews.map((r) => {
    const cls   = `sentiment-pill sentiment-pill--${r.sentiment_label || "neutral"}`;
    const score = typeof r.sentiment_score === "number"
      ? ` (${r.sentiment_score >= 0 ? "+" : ""}${r.sentiment_score.toFixed(2)})`
      : "";
    const date  = r.created_at
      ? new Date(r.created_at).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" })
      : "";
    return `
      <div class="review-card">
        <div class="review-card__header">
          <span class="review-card__student">${esc(r.student_id)}</span>
          <span class="${cls}">${esc(r.sentiment_label || "neutral")}${esc(score)}</span>
          <span class="review-card__date">${esc(date)}</span>
        </div>
        <p class="review-card__body">${esc(r.review_text)}</p>
      </div>`;
  }).join("");
}

$("submitReviewBtn").addEventListener("click", async () => {
  const text = $("reviewTextarea").value.trim();
  const errEl = $("reviewFormError");
  if (!text) {
    errEl.textContent = "Please write something before submitting.";
    errEl.classList.remove("hidden");
    return;
  }
  errEl.classList.add("hidden");
  $("submitReviewBtn").disabled     = true;
  $("submitReviewBtn").textContent  = "Analysing…";
  try {
    const res  = await fetch("/api/reviews", {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify({
        student_id: state.studentId,
        book_id:    _currentReviewBookId,
        review:     text,
      }),
    });
    const data = await res.json();
    if (data.error) { showToast(data.error, true); return; }
    const label = (data.sentiment && data.sentiment.label) || "neutral";
    showToast(`Review saved! Sentiment: ${label}`);
    $("reviewTextarea").value = "";
    _loadReviews(_currentReviewBookId);
  } catch {
    showToast("Could not save review.", true);
  } finally {
    $("submitReviewBtn").disabled    = false;
    $("submitReviewBtn").textContent = "Submit & Analyse Sentiment";
  }
});


// =============================================================================
// RECOMMENDATIONS  (WatsonX AI personalised suggestions)
// =============================================================================

let _recsLoaded = false;

async function loadRecommendations(force = false) {
  if (_recsLoaded && !force) return;
  const aiCard    = $("recsAiCard");
  const aiText    = $("recsAiText");
  const histSec   = $("recsHistorySection");
  const histTitle = $("recsHistoryTitle");
  const histGrid  = $("recsHistoryGrid");
  const loading   = $("recsLoading");
  const empty     = $("recsEmpty");

  aiCard.classList.add("hidden");
  histSec.classList.add("hidden");
  empty.classList.add("hidden");
  loading.classList.remove("hidden");

  try {
    const res  = await fetch(`/api/recommendations/${encodeURIComponent(state.studentId)}`);
    const data = await res.json();

    loading.classList.add("hidden");

    if (!data.history || !data.history.length) {
      empty.classList.remove("hidden");
      return;
    }

    // Show reading history mini-grid
    histTitle.textContent = `Based on ${data.history_count} book${data.history_count !== 1 ? "s" : ""} in your history`;
    histGrid.innerHTML = data.history.map((b, i) => renderPinCard(b, i)).join("");
    attachReserveListeners(histGrid);
    attachTagListeners(histGrid);
    histSec.classList.remove("hidden");

    // Show AI recommendation text
    aiText.textContent = data.recommendations || "";
    aiCard.classList.remove("hidden");
    _recsLoaded = true;
  } catch {
    loading.classList.add("hidden");
    showToast("Could not load recommendations.", true);
  }
}

// =============================================================================
// WHAT TO READ TODAY  (WatsonX AI — homepage banner)
// =============================================================================

const wrtdBanner  = $("wrtdBanner");
const wrtdLoading = $("wrtdLoading");
const wrtdText    = $("wrtdText");
const wrtdShelf   = $("wrtdShelf");

// Shelf book mini-card (horizontal strip)
function renderShelfCard(book, index) {
  const thumbClass = `pin-thumb--${index % 18}`;
  const avail = book.available_copies > 0;
  return `
    <div class="shelf-card ${thumbClass}">
      <div class="shelf-card__title">${esc(book.title)}</div>
      <div class="shelf-card__author">${esc(book.author)}</div>
      <button class="shelf-card__btn btn-pin-action${avail ? "" : " btn-pin-action--waitlist"}"
              data-id="${esc(book._id)}"
              data-title="${esc(book.title)}"
              data-author="${esc(book.author)}"
              data-avail="${avail}">
        ${avail ? "Reserve" : "Waitlist"}
      </button>
    </div>`;
}

let _wrtdLoaded = false;

async function loadWRTD(force = false) {
  if (_wrtdLoaded && !force) return;

  wrtdBanner.classList.add("hidden");
  wrtdLoading.classList.remove("hidden");

  try {
    const sid = state.studentId;
    const res  = await fetch(`/api/recommendations/${encodeURIComponent(sid)}`);
    const data = await res.json();

    wrtdLoading.classList.add("hidden");

    // Pick 4 random books from catalogue if no history yet
    let books = [];
    if (data.history && data.history.length) {
      // Use reading-history books as "what you might re-explore" + random popular
      const popularRes = await fetch("/api/books/high-demand?threshold=1&limit=8");
      const popularData = await popularRes.json();
      books = (popularData.books || []).slice(0, 5);
      // AI summary from recommendations
      const summary = (data.recommendations || "").split("\n")[0] || "Here are today's top picks for you.";
      wrtdText.textContent = summary.replace(/^•\s*/, "").slice(0, 120);
    } else {
      // No history — show popular books
      const popularRes = await fetch("/api/books/high-demand?threshold=0&limit=5");
      const popularData = await popularRes.json();
      books = popularData.books || [];
      wrtdText.textContent = "Popular in your library right now — reserve one to build your reading history.";
    }

    if (books.length) {
      wrtdShelf.innerHTML = books.map((b, i) => renderShelfCard(b, i)).join("");
      attachReserveListeners(wrtdShelf);
      wrtdBanner.classList.remove("hidden");
      _wrtdLoaded = true;
    }
  } catch {
    wrtdLoading.classList.add("hidden");
    // Silently skip — banner is non-critical
  }
}

$("wrtdBtn").addEventListener("click", () => {
  switchPanel("recommendations");
  loadRecommendations();
});
