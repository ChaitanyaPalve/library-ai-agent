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

// Quotes — defined early so all functions can use them
const LIB_QUOTES = [
  "\"A reader lives a thousand lives before he dies.\" — George R.R. Martin",
  "\"Not all those who wander are lost.\" — J.R.R. Tolkien",
  "\"A book is a dream that you hold in your hands.\" — Neil Gaiman",
  "\"Today a reader, tomorrow a leader.\" — Margaret Fuller",
  "\"The more that you read, the more things you will know.\" — Dr. Seuss",
  "\"A library is not a luxury but one of the necessities of life.\" — Henry Ward Beecher",
  "\"Think before you speak. Read before you think.\" — Fran Lebowitz",
  "\"There is no friend as loyal as a book.\" — Ernest Hemingway",
  "\"Reading is to the mind what exercise is to the body.\" — Joseph Addison",
  "\"Books are a uniquely portable magic.\" — Stephen King",
  "\"You can never get a cup of tea large enough or a book long enough to suit me.\" — C.S. Lewis",
  "\"One must always be careful of books, and what is inside them.\" — Cassandra Clare",
];
function randomQuote() {
  return LIB_QUOTES[Math.floor(Math.random() * LIB_QUOTES.length)];
}
function setQuoteEl(id) {
  const el = document.getElementById(id);
  if (el) el.textContent = randomQuote();
}

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
const historyList       = $("historyList");
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
$("navRecsBtn").addEventListener("click",  () => {
  switchPanel("recommendations");
  loadRecommendations();
  loadAIPicks(recsAiPicksSect, recsAiPicksGrid, recsAiPicksLoad);
});
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
// Pagination constant (shared by search + home books)
// ─────────────────────────────────────────────────────────────────────────────
const PAGE_SIZE = 30;

// ─────────────────────────────────────────────────────────────────────────────
// Search
// ─────────────────────────────────────────────────────────────────────────────
searchBtn.addEventListener("click", doSearch);
queryInput.addEventListener("keydown", (e) => { if (e.key === "Enter") doSearch(); });

// Search results pagination state
let _searchBooksAll = [];
let _searchBooksPage = 1;

function _renderSearchPage(page) {
  _searchBooksPage = page;
  const start = (page - 1) * PAGE_SIZE;
  const slice = _searchBooksAll.slice(start, start + PAGE_SIZE);
  const total = _searchBooksAll.length;
  const totalPages = Math.ceil(total / PAGE_SIZE);

  resultsTitle.textContent =
    `${total} book${total !== 1 ? "s" : ""} found · Page ${page} of ${totalPages}`;

  booksGrid.innerHTML = slice.map((b, i) => renderPinCard(b, start + i)).join("");
  attachReserveListeners(booksGrid);
  attachTagListeners(booksGrid);
  window._observeDescriptions?.(booksGrid);

  // Inject pagination after booksGrid
  let pagEl = document.getElementById("searchPagination");
  if (!pagEl) {
    pagEl = document.createElement("div");
    pagEl.id = "searchPagination";
    pagEl.className = "pagination";
    resultsSection.appendChild(pagEl);
  }
  if (totalPages <= 1) { pagEl.innerHTML = ""; return; }

  const visible = new Set([1, totalPages]);
  for (let p = Math.max(1, page - 2); p <= Math.min(totalPages, page + 2); p++) visible.add(p);
  const sorted = [...visible].sort((a, b) => a - b);
  let html = "", prev = 0;
  for (const p of sorted) {
    if (p - prev > 1) html += `<span class="pagination__ellipsis">…</span>`;
    html += `<button class="pagination__btn${p === page ? " pagination__btn--active" : ""}" data-page="${p}">${p}</button>`;
    prev = p;
  }
  pagEl.innerHTML =
    `<button class="pagination__btn pagination__btn--nav" data-page="${page - 1}"${page === 1 ? " disabled" : ""}>‹</button>` +
    html +
    `<button class="pagination__btn pagination__btn--nav" data-page="${page + 1}"${page === totalPages ? " disabled" : ""}>›</button>`;
  pagEl.querySelectorAll(".pagination__btn[data-page]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const p = parseInt(btn.dataset.page, 10);
      if (!isNaN(p) && p >= 1 && p <= totalPages) {
        _renderSearchPage(p);
        resultsSection.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    });
  });
}

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
      _searchBooksAll = data.books;
      resultsSection.classList.remove("hidden");
      _renderSearchPage(1);
    } else {
      // Show empty state with AI suggest message using the searched query
      emptyState.classList.remove("hidden");
      setQuoteEl("emptyQuote");
      const aiSuggestMsg = $("emptyAiSuggestMsg");
      if (aiSuggestMsg) {
        aiSuggestMsg.innerHTML = `🤖 <strong>WatsonX AI suggests:</strong> "${esc(query)}" wasn't found in our catalogue. Would you like to suggest it for acquisition?`;
        aiSuggestMsg.classList.remove("hidden");
        // Store last searched query so suggest button can pre-fill it
        aiSuggestMsg.dataset.query = query;
      }
    }

  } catch {
    setLoading(false);
    showToast("Search failed. Check your connection.", true);
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Home books loader  — paginated, 30 per page
// ─────────────────────────────────────────────────────────────────────────────
let _homeBooksGenreLoaded = "";
let _homeBooksAll = [];       // full fetched list
let _homeBooksPage = 1;       // current page (1-based)

// Tracks whether a seed/refresh has already been triggered this session
// so we don't loop infinitely if a genre genuinely has 0 books after refresh.
let _seedRefreshDone = false;

async function _refreshCatalogue() {
  if (_seedRefreshDone) return;
  _seedRefreshDone = true;
  try {
    await fetch("/api/admin/seed-books", { method: "POST" });
  } catch { /* silent — best effort */ }
}

function _renderHomePage(page) {
  _homeBooksPage = page;
  const start = (page - 1) * PAGE_SIZE;
  const slice = _homeBooksAll.slice(start, start + PAGE_SIZE);
  const total = _homeBooksAll.length;
  const totalPages = Math.ceil(total / PAGE_SIZE);

  homeBooksCount.textContent =
    `${total} book${total !== 1 ? "s" : ""} · Page ${page} of ${totalPages}`;

  homeBooksGrid.innerHTML = slice.map((b, i) => renderPinCard(b, start + i)).join("");
  attachReserveListeners(homeBooksGrid);
  attachTagListeners(homeBooksGrid);
  window._observeDescriptions?.(homeBooksGrid);

  // Render pagination below grid
  _renderPagination("homePagination", totalPages, page, _renderHomePage);
}

function _renderPagination(containerId, totalPages, currentPage, onPageClick) {
  let el = document.getElementById(containerId);
  if (!el) {
    el = document.createElement("div");
    el.id = containerId;
    el.className = "pagination";
    homeBooksSection.appendChild(el);
  }
  if (totalPages <= 1) { el.innerHTML = ""; return; }

  const pages = [];
  // Always show first, last, current ±2
  const visible = new Set([1, totalPages]);
  for (let p = Math.max(1, currentPage - 2); p <= Math.min(totalPages, currentPage + 2); p++) {
    visible.add(p);
  }
  const sorted = [...visible].sort((a, b) => a - b);

  let html = "";
  let prev = 0;
  for (const p of sorted) {
    if (p - prev > 1) html += `<span class="pagination__ellipsis">…</span>`;
    html += `<button class="pagination__btn${p === currentPage ? " pagination__btn--active" : ""}" data-page="${p}">${p}</button>`;
    prev = p;
  }

  el.innerHTML =
    `<button class="pagination__btn pagination__btn--nav" data-page="${currentPage - 1}"${currentPage === 1 ? " disabled" : ""}>‹</button>` +
    html +
    `<button class="pagination__btn pagination__btn--nav" data-page="${currentPage + 1}"${currentPage === totalPages ? " disabled" : ""}>›</button>`;

  el.querySelectorAll(".pagination__btn[data-page]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const p = parseInt(btn.dataset.page, 10);
      if (!isNaN(p) && p >= 1 && p <= totalPages) {
        onPageClick(p);
        homeBooksSection.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    });
  });
}

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
  // Clear old pagination
  const oldPag = document.getElementById("homePagination");
  if (oldPag) oldPag.innerHTML = "";

  try {
    let url;
    if (genre && genre.startsWith("mood:")) {
      const moodName = genre.slice(5);
      url = `/api/mood-books/${encodeURIComponent(moodName)}`;
    } else if (genre && genre !== "all") {
      url = `/api/books?subject=${encodeURIComponent(genre)}&limit=200`;
    } else {
      url = `/api/books?limit=200`;
    }
    const res  = await fetch(url);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    // If this genre returned 0 books, trigger a catalogue refresh once
    // (fixes stale subject_tags on existing books) then reload.
    if (!data.total && !_seedRefreshDone) {
      await _refreshCatalogue();
      homeBooksLoading.classList.add("hidden");
      _homeBooksGenreLoaded = "";
      loadHomeBooks(genre, true);
      return;
    }

    homeBooksLoading.classList.add("hidden");

    _homeBooksAll = data.books || [];
    _homeBooksGenreLoaded = genre;
    _renderHomePage(1);
  } catch (err) {
    homeBooksLoading.classList.add("hidden");
    console.error("[loadHomeBooks]", err);
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
  const btnText    = avail ? "Issue" : "Waitlist";

  const isbnText   = book.isbn ? `ISBN ${esc(book.isbn)}` : "";
  const copiesText = `${book.total_copies || 1} cop${(book.total_copies || 1) === 1 ? "y" : "ies"} total`;
  const quickInfo  = `<div class="pin-card__quick-info">${isbnText ? isbnText + " · " : ""}${copiesText}</div>`;

  // Specialty badge (genre/subject shown always at bottom-right of image)
  const specialtyLabel = primaryTag || (book.genre) || null;
  const specialtyBadge = specialtyLabel
    ? `<div class="pin-card__specialty-badge">${esc(specialtyLabel)}</div>` : "";

  // Book cover: coloured block with title + author overlaid
  const coverDescId = `cover-desc-${esc(book._id)}`;
  const coverDesc = book.description
    ? `<div class="pin-card__cover-desc" id="${coverDescId}">${esc(book.description)}</div>`
    : `<div class="pin-card__cover-desc pin-card__cover-desc--loading" id="${coverDescId}" data-book-id="${esc(book._id)}"></div>`;
  const thumbCover = `
    ${coverDesc}
    <div class="pin-card__cover-title">${esc(book.title)}</div>
    <div class="pin-card__cover-author">${esc(book.author)}</div>`;

  // Description — show if present, otherwise lazy-load via API
  const descId  = `desc-${esc(book._id)}`;
  const descHtml = book.description
    ? `<p class="pin-card__desc" id="${descId}">${esc(book.description)}</p>`
    : `<p class="pin-card__desc pin-card__desc--loading" id="${descId}" data-book-id="${esc(book._id)}" data-title="${esc(book.title)}" data-author="${esc(book.author)}">Loading description…</p>`;

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
        ${descHtml}
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
        ${specialtyBadge}
      </div>
    </article>`;
}

// Lazy-load descriptions for cards that don't have one yet.
// Uses IntersectionObserver so we only fetch when the card scrolls into view.
(function setupDescriptionLazyLoader() {
  const pending = new Map(); // bookId -> {el, title, author}
  const fetching = new Set();

  function fetchDesc(bookId, el) {
    if (fetching.has(bookId)) return;
    fetching.add(bookId);
    fetch("/api/book-description", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ book_id: bookId }),
    })
      .then((r) => r.json())
      .then((d) => {
        const text = d.description || "";
        document.querySelectorAll(`[data-book-id="${bookId}"]`).forEach((e) => {
          e.textContent = text;
          e.classList.remove("pin-card__desc--loading", "pin-card__cover-desc--loading");
        });
      })
      .catch(() => {
        document.querySelectorAll(`[data-book-id="${bookId}"]`).forEach((e) => {
          e.textContent = "";
          e.classList.remove("pin-card__desc--loading", "pin-card__cover-desc--loading");
        });
      });
  }

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      const el = entry.target;
      const bookId = el.dataset.bookId;
      if (bookId) {
        fetchDesc(bookId, el);
        observer.unobserve(el);
      }
    });
  }, { rootMargin: "100px" });

  // Called after any grid renders to start observing new lazy desc elements.
  window._observeDescriptions = (container = document) => {
    container.querySelectorAll(".pin-card__desc--loading, .pin-card__cover-desc--loading").forEach((el) => observer.observe(el));
  };
})();

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
  modalTitle.textContent    = available ? "Issue this book" : "Join the waitlist";
  modalSubtitle.textContent = `"${title}" by ${author}`;
  modalBody.innerHTML = available
    ? `<p>You are about to issue a copy for student <strong>${esc(sid)}</strong>.</p>
       <p style="margin-top:8px;color:var(--color-mute);font-size:14px">Held for up to 14 days — IBM Robo will auto-release after that.</p>`
    : `<p>All copies are currently issued or unavailable.</p>
       <p style="margin-top:8px;color:var(--color-mute);font-size:14px">Join the waitlist and IBM Robo will promote you automatically when a copy is returned.</p>`;
  modalConfirm.textContent = available ? "Confirm Issue" : "Join Waitlist";
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
      issuedAt:   data.issued_at  || null,
      dueDate:    data.due_date   || null,
      message:    data.ai_message || "",
    });

    const msg = data.status === "active" ? "Book issued successfully!" : "Added to waitlist.";
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

/** Compute days/hours remaining until dueDate string (ISO). Returns display text. */
function formatDueCountdown(dueDateStr) {
  if (!dueDateStr) return null;
  const due  = new Date(dueDateStr);
  const now  = new Date();
  const msLeft = due - now;
  if (msLeft <= 0) return "⚠ Overdue";
  const daysLeft  = Math.floor(msLeft / 86400000);
  const hoursLeft = Math.floor((msLeft % 86400000) / 3600000);
  if (daysLeft > 0) return `Due in ${daysLeft}d ${hoursLeft}h`;
  return `Due in ${hoursLeft}h`;
}

// ── Fetch active reservations from API (called on panel open) ──────────────
async function fetchAndRenderReservations() {
  reservationsList.innerHTML = `
    <div class="state-card">
      <div class="lib-spinner" aria-hidden="true"><div class="lib-spinner__ring"></div></div>
      <p class="state-card__sub">Loading your holds…</p>
    </div>`;
  historyList.innerHTML = "";

  try {
    const sid = state.studentId;
    const resRes = await fetch(`/api/reading-log/${encodeURIComponent(sid)}`);
    if (resRes.ok) {
      const resData = await resRes.json();
      const all = resData.log || [];

      // Active/waitlisted → merge into state.reservations
      const activeOnes = all.filter((r) => r.status === "active" || r.status === "waitlisted");
      const sessionIds = new Set(state.reservations.map((x) => x.id));
      activeOnes.forEach((r) => {
        if (!sessionIds.has(r._id)) {
          state.reservations.push({
            id:         r._id,
            bookId:     r.book_id,
            bookTitle:  r.book_title,
            bookAuthor: r.book_author,
            status:     r.status,
            issuedAt:   r.issued_at,
            dueDate:    r.due_date,
            message:    "",
          });
        } else {
          // Update status in case it changed
          const existing = state.reservations.find((x) => x.id === r._id);
          if (existing) {
            existing.status   = r.status;
            existing.dueDate  = r.due_date;
            existing.issuedAt = r.issued_at;
          }
        }
      });

      // History (returned + cancelled)
      const history = all.filter((r) => r.status === "returned" || r.status === "cancelled");
      renderHistory(history);
    }
  } catch {
    // Fall through to render what we have in session
  }
  renderReservations();
}

function renderReservations() {
  const visible = state.reservations.filter((r) => r.status === "active" || r.status === "waitlisted");
  if (!visible.length) {
    reservationsList.innerHTML = `
      <div class="state-card">
        <svg width="48" height="48" viewBox="0 0 48 48" fill="none" aria-hidden="true">
          <rect x="8" y="12" width="32" height="28" rx="3" fill="var(--color-surface-card)" stroke="var(--color-hairline)" stroke-width="1.5"/>
          <path d="M24 20v12M18 26h12" stroke="var(--color-ash)" stroke-width="1.5" stroke-linecap="round"/>
        </svg>
        <p class="state-card__title">No active holds</p>
        <p class="state-card__sub">Search for a book and tap Issue or Waitlist to add your first hold</p>
        <div class="lib-quote">${esc(randomQuote())}</div>
      </div>`;
    return;
  }

  reservationsList.innerHTML = visible.map((r) => {
    const chipClass = `status-chip status-chip--${r.status}`;
    const countdown = r.status === "active" ? formatDueCountdown(r.dueDate) : null;
    const countdownHtml = countdown
      ? `<div class="due-countdown ${countdown.startsWith("⚠") ? "due-countdown--overdue" : ""}">${esc(countdown)}</div>`
      : "";
    const issuedHtml = r.issuedAt
      ? `<div class="res-card__meta-small">Issued: ${new Date(r.issuedAt).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" })}</div>`
      : "";
    return `
      <div class="res-card" data-res-id="${esc(r.id)}">
        <div class="res-card__info">
          <div class="res-card__title">${esc(r.bookTitle || "Unknown Book")}</div>
          <div class="res-card__meta">${esc(r.bookAuthor || "")} · Student: ${esc(state.studentId)}</div>
          ${issuedHtml}
          ${countdownHtml}
          ${r.message ? `<div class="res-card__message">${esc(r.message)}</div>` : ""}
        </div>
        <div class="res-card__actions">
          <span class="${chipClass}">${r.status}</span>
          ${r.status === "active"
            ? `<button class="btn-return" data-id="${esc(r.id)}" aria-label="Return book">Return</button>`
            : ""}
          <button class="btn-cancel" data-id="${esc(r.id)}" aria-label="Cancel reservation">Cancel</button>
        </div>
      </div>`;
  }).join("");

  reservationsList.querySelectorAll(".btn-cancel").forEach((btn) => {
    btn.addEventListener("click", () => cancelReservation(btn.dataset.id));
  });
  reservationsList.querySelectorAll(".btn-return").forEach((btn) => {
    btn.addEventListener("click", () => returnBook(btn.dataset.id));
  });
}

function renderHistory(history) {
  if (!history || !history.length) {
    historyList.innerHTML = `
      <div class="state-card" style="padding:var(--space-xl) 0">
        <p class="state-card__sub">No returned books yet</p>
      </div>`;
    return;
  }
  historyList.innerHTML = history.map((r) => {
    const statusLabel = r.status === "returned" ? "Returned" : "Cancelled";
    const chipCls = r.status === "returned" ? "status-chip--returned" : "status-chip--cancelled";
    const duration = r.read_duration_days != null
      ? `Read in ${r.read_duration_days} day${r.read_duration_days !== 1 ? "s" : ""}`
      : "";
    const returnedDate = r.returned_at
      ? new Date(r.returned_at).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" })
      : "";
    const issuedDate = r.issued_at
      ? new Date(r.issued_at).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" })
      : "";
    return `
      <div class="res-card res-card--history">
        <div class="res-card__info">
          <div class="res-card__title">${esc(r.book_title || "Unknown Book")}</div>
          <div class="res-card__meta">${esc(r.book_author || "")}</div>
          <div class="res-card__history-meta">
            ${issuedDate ? `<span>Issued: ${esc(issuedDate)}</span>` : ""}
            ${returnedDate ? `<span>Returned: ${esc(returnedDate)}</span>` : ""}
            ${duration ? `<span class="history-duration">${esc(duration)}</span>` : ""}
          </div>
        </div>
        <div class="res-card__actions">
          <span class="status-chip ${chipCls}">${statusLabel}</span>
        </div>
      </div>`;
  }).join("");
}

async function cancelReservation(resId) {
  try {
    const res  = await fetch(`/api/reserve/${resId}`, { method: "DELETE" });
    const data = await res.json();
    if (data.error) { showToast(data.error, true); return; }
    const r = state.reservations.find((x) => x.id === resId);
    if (r) r.status = "cancelled";
    renderReservations();
    showToast("Issue cancelled.");
    // Reload history to show newly cancelled entry
    fetchAndRenderReservations();
  } catch {
    showToast("Cancel failed.", true);
  }
}

async function returnBook(resId) {
  const btn = reservationsList.querySelector(`.btn-return[data-id="${resId}"]`);
  if (btn) { btn.disabled = true; btn.textContent = "Returning…"; }
  try {
    const res  = await fetch(`/api/reserve/${resId}/return`, { method: "POST" });
    const data = await res.json();
    if (data.error) { showToast(data.error, true); if (btn) { btn.disabled = false; btn.textContent = "Return"; } return; }
    // Remove from active state
    state.reservations = state.reservations.filter((x) => x.id !== resId);
    showToast(
      data.read_duration_days != null
        ? `Book returned! You read it in ${data.read_duration_days} day(s).`
        : "Book returned successfully!"
    );
    // Refresh the full panel to show history
    fetchAndRenderReservations();
  } catch {
    showToast("Return failed. Try again.", true);
    if (btn) { btn.disabled = false; btn.textContent = "Return"; }
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Dashboard panel (lazy — only fetches when first opened)
// ─────────────────────────────────────────────────────────────────────────────
async function loadDashboard() {
  loadOrchStatus();
  loadExplain();

  highDemandList.innerHTML   = `<p style="color:var(--color-ash);font-size:13px">Loading…</p>`;
  automationAlerts.innerHTML = `<p style="color:var(--color-ash);font-size:13px">Loading…</p>`;

  // Render catalogue stat cards
  const statsEl = $("dashboardStats");
  if (statsEl) {
    statsEl.innerHTML = `<p class="dash-stat-loading">Loading stats…</p>`;
    try {
      const booksRes = await fetch("/api/books?count=1");
      const booksData = await booksRes.json();
      const totalBooks = booksData.total || 0;

      const hdRes = await fetch("/api/books/high-demand?threshold=5&limit=100");
      const hdData = await hdRes.json();
      const hdCount = hdData.total || 0;

      statsEl.innerHTML = `
        <div class="dash-stat-card">
          <div class="dash-stat-card__value">${totalBooks}</div>
          <div class="dash-stat-card__label">Books in Catalogue</div>
        </div>
        <div class="dash-stat-card">
          <div class="dash-stat-card__value">${hdCount}</div>
          <div class="dash-stat-card__label">High-Demand Titles</div>
        </div>
        <div class="dash-stat-card">
          <div class="dash-stat-card__value">${Math.ceil(totalBooks / 30)}</div>
          <div class="dash-stat-card__label">Pages at 30/page</div>
        </div>`;
    } catch {
      statsEl.innerHTML = "";
    }
  }

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
    loadDashboard();
  } catch {
    showToast("Automation run failed.", true);
  } finally {
    runRoboBtn.disabled = false;
    runRoboBtn.textContent = "Run Robo Rules";
  }
});

// Reset book availability button
const resetBooksBtn = $("resetBooksBtn");
const resetBooksMsg = $("resetBooksMsg");
if (resetBooksBtn) {
  resetBooksBtn.addEventListener("click", async () => {
    resetBooksBtn.disabled = true;
    resetBooksBtn.textContent = "Resetting…";
    try {
      const res  = await fetch("/api/admin/reset-books", { method: "POST" });
      const data = await res.json();
      if (data.ok) {
        resetBooksMsg.textContent = `✅ ${data.message}`;
        resetBooksMsg.style.color = "var(--color-success, #166534)";
        showToast(data.message);
        // Reload home books so availability badges update immediately
        _homeBooksGenreLoaded = "";
        loadHomeBooks(state.homeGenre, true);
      } else {
        showToast("Reset failed.", true);
      }
    } catch {
      showToast("Reset request failed. Check server connection.", true);
    } finally {
      resetBooksBtn.disabled = false;
      resetBooksBtn.textContent = "🔄 Reset Book Availability";
    }
  });
}

// Seed full catalogue button
const seedBooksBtn = $("seedBooksBtn");
const seedBooksMsg = $("seedBooksMsg");
if (seedBooksBtn) {
  seedBooksBtn.addEventListener("click", async () => {
    seedBooksBtn.disabled = true;
    seedBooksBtn.textContent = "Seeding…";
    try {
      const res  = await fetch("/api/admin/seed-books", { method: "POST" });
      const data = await res.json();
      if (data.ok) {
        seedBooksMsg.textContent = `✅ ${data.message}`;
        seedBooksMsg.style.color = "var(--color-success, #166534)";
        showToast(data.message);
        // Reload home books so newly seeded titles appear immediately
        _homeBooksGenreLoaded = "";
        loadHomeBooks(state.homeGenre, true);
      } else {
        showToast("Seeding failed.", true);
      }
    } catch {
      showToast("Seed request failed. Check server connection.", true);
    } finally {
      seedBooksBtn.disabled = false;
      seedBooksBtn.textContent = "📚 Seed Full Catalogue";
    }
  });
}

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
  // Load homepage books, WRTD banner, suggested books and AI picks after sign-in
  loadHomeBooks("all");
  loadWRTD();
  loadSuggestedBooks();
  loadAIPicks(aiPicksSection, aiPicksGrid, aiPicksLoading);
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
  loadSuggestedBooks();
  loadAIPicks(aiPicksSection, aiPicksGrid, aiPicksLoading);
}

// Populate all quote placeholders on load
setQuoteEl("emptyQuote");
setQuoteEl("recsEmptyQuote");

// =============================================================================
// SUGGESTED BOOKS SECTION  — real books students suggested, not yet in catalogue
// =============================================================================
const suggestedSection = $("suggestedBooksSection");
const suggestedGrid    = $("suggestedBooksGrid");
const suggestedCount   = $("suggestedBooksCount");

async function loadSuggestedBooks() {
  if (!suggestedSection || !suggestedGrid) return;
  try {
    const res  = await fetch("/api/suggestions");
    const data = await res.json();
    if (!data.suggestions || data.suggestions.length === 0) {
      suggestedSection.classList.add("hidden");
      return;
    }
    suggestedCount.textContent = `${data.total} book${data.total !== 1 ? "s" : ""} suggested by students`;
    suggestedGrid.innerHTML = data.suggestions.map((s, i) => {
      const thumbClass = `pin-thumb--${i % 18}`;
      return `
        <article class="suggest-item" role="listitem">
          <div class="suggest-item__thumb ${thumbClass}">
            <div class="pin-card__cover-title">${esc(s.title)}</div>
            <div class="pin-card__cover-author">${esc(s.author)}</div>
          </div>
          <div class="suggest-item__body">
            <div class="suggest-item__title">${esc(s.title)}</div>
            <div class="suggest-item__author">by ${esc(s.author)}</div>
            ${s.description ? `<p class="suggest-item__desc">${esc(s.description)}</p>` : ""}
            ${s.reason ? `<p class="suggest-item__reason">💬 "${esc(s.reason)}"</p>` : ""}
          </div>
          <button class="btn-secondary suggest-item__btn"
                  onclick="openSuggestTab('${esc(s.title).replace(/'/g, "&#39;")}')">
            Also Suggest
          </button>
        </article>`;
    }).join("");
    suggestedSection.classList.remove("hidden");
  } catch {
    // Non-critical — hide section silently
    if (suggestedSection) suggestedSection.classList.add("hidden");
  }
}

// =============================================================================
// SUGGEST A BOOK BAR  — standalone button in clear space
// =============================================================================
function openSuggestTab(prefillTitle = "") {
  // Open chatbot panel on Suggest Book tab
  const panel = $("chatbotPanel");
  panel.classList.remove("hidden");
  // Activate the suggest tab
  panel.querySelectorAll(".chatbot-mode-btn").forEach((b) => {
    b.classList.remove("chatbot-mode-btn--active");
    b.setAttribute("aria-selected", "false");
  });
  const suggestTab = panel.querySelector('.chatbot-mode-btn[data-mode="suggest"]');
  if (suggestTab) {
    suggestTab.classList.add("chatbot-mode-btn--active");
    suggestTab.setAttribute("aria-selected", "true");
  }
  $("chatbotSuggestForm").classList.remove("hidden");
  $("chatbotInputRow").classList.add("hidden");
  // Pre-fill title if provided (e.g. from a failed search)
  if (prefillTitle) {
    const titleInput = $("suggestTitle");
    if (titleInput) titleInput.value = prefillTitle;
  }
}

const suggestBookBarBtn = $("suggestBookBarBtn");
if (suggestBookBarBtn) suggestBookBarBtn.addEventListener("click", () => openSuggestTab());

const emptyStateSuggestBtn = $("emptyStateSuggestBtn");
if (emptyStateSuggestBtn) {
  emptyStateSuggestBtn.addEventListener("click", () => {
    // Pre-fill with the last searched query if available
    const aiSuggestMsg = $("emptyAiSuggestMsg");
    const prefill = aiSuggestMsg ? (aiSuggestMsg.dataset.query || "") : "";
    openSuggestTab(prefill);
  });
}

function hideResults() {
  nluInsights.classList.add("hidden");
  aiMessage.classList.add("hidden");
  resultsSection.classList.add("hidden");
  emptyState.classList.add("hidden");
  loadingState.classList.add("hidden");
  homeBooksSection.classList.remove("hidden");
  // Reset AI suggest message between searches
  const aiSuggestMsg = $("emptyAiSuggestMsg");
  if (aiSuggestMsg) {
    aiSuggestMsg.classList.add("hidden");
    delete aiSuggestMsg.dataset.query;
  }
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
    window._observeDescriptions?.(histGrid);
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
// AI PICKS  (WatsonX AI — random catalogue books with blurbs)
// =============================================================================

const aiPicksSection   = $("aiPicksSection");
const aiPicksGrid      = $("aiPicksGrid");
const aiPicksLoading   = $("aiPicksLoading");
const aiPicksRefresh   = $("aiPicksRefresh");
const recsAiPicksSect  = $("recsAiPicksSection");
const recsAiPicksGrid  = $("recsAiPicksGrid");
const recsAiPicksLoad  = $("recsAiPicksLoading");
const recsAiPicksRefr  = $("recsAiPicksRefresh");

const THUMB_CLASSES = Array.from({length: 18}, (_, i) => `pin-thumb--${i}`);

function renderAiPickCard(book, index) {
  const avail      = book.available_copies > 0;
  const thumbClass = THUMB_CLASSES[index % THUMB_CLASSES.length];
  return `
    <article class="ai-pick-card" role="listitem">
      <div class="ai-pick-card__thumb ${thumbClass}">
        <span class="ai-pick-card__badge">✦ AI Pick</span>
        <div class="ai-pick-card__cover-title">${esc(book.title)}</div>
        <div class="ai-pick-card__cover-author">${esc(book.author)}</div>
      </div>
      <div class="ai-pick-card__body">
        <p class="ai-pick-card__blurb">${esc(book.ai_blurb || book.description || "")}</p>
        <div class="ai-pick-card__footer">
          <span class="ai-pick-card__avail ai-pick-card__avail--${avail ? "yes" : "no"}">
            ${avail ? `${book.available_copies} available` : "Waitlist"}
          </span>
          <button class="btn-pin-action ai-pick-card__btn${avail ? "" : " btn-pin-action--waitlist"}"
                  data-id="${esc(book._id)}"
                  data-title="${esc(book.title)}"
                  data-author="${esc(book.author)}"
                  data-avail="${avail}">
            ${avail ? "Issue" : "Waitlist"}
          </button>
        </div>
      </div>
    </article>`;
}

async function loadAIPicks(targetSection, targetGrid, targetLoading, count = 6) {
  if (!targetSection || !targetGrid) return;
  targetSection.classList.add("hidden");
  targetLoading.classList.remove("hidden");
  try {
    const res  = await fetch(`/api/ai-picks?count=${count}`);
    const data = await res.json();
    targetLoading.classList.add("hidden");
    if (!data.picks || data.picks.length === 0) return;
    targetGrid.innerHTML = data.picks.map((b, i) => renderAiPickCard(b, i)).join("");
    attachReserveListeners(targetGrid);
    targetSection.classList.remove("hidden");
  } catch {
    targetLoading.classList.add("hidden");
  }
}

// Refresh buttons
if (aiPicksRefresh) {
  aiPicksRefresh.addEventListener("click", () =>
    loadAIPicks(aiPicksSection, aiPicksGrid, aiPicksLoading));
}
if (recsAiPicksRefr) {
  recsAiPicksRefr.addEventListener("click", () =>
    loadAIPicks(recsAiPicksSect, recsAiPicksGrid, recsAiPicksLoad));
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
      <div class="shelf-card__hot">🔥 Hot Pick</div>
      <div class="shelf-card__title">${esc(book.title)}</div>
      <div class="shelf-card__author">${esc(book.author)}</div>
      <button class="shelf-card__btn btn-pin-action${avail ? "" : " btn-pin-action--waitlist"}"
              data-id="${esc(book._id)}"
              data-title="${esc(book.title)}"
              data-author="${esc(book.author)}"
              data-avail="${avail}">
        ${avail ? "Issue" : "Waitlist"}
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

    let books = [];
    if (data.history && data.history.length) {
      const popularRes = await fetch("/api/books/high-demand?threshold=1&limit=10");
      const popularData = await popularRes.json();
      books = (popularData.books || []).slice(0, 5);
      const summary = (data.recommendations || "").split("\n")[0] || "Today's top picks curated just for you.";
      wrtdText.textContent = summary.replace(/^\u2022\s*/, "").slice(0, 120);
    } else {
      const popularRes = await fetch("/api/books/high-demand?threshold=0&limit=5");
      const popularData = await popularRes.json();
      books = (popularData.books || []).slice(0, 5);
      wrtdText.textContent = "🔥 5 hot picks from your library — issue one to start your reading history.";
    }

    if (books.length) {
      wrtdShelf.innerHTML = books.slice(0, 5).map((b, i) => renderShelfCard(b, i)).join("");
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
  loadAIPicks(recsAiPicksSect, recsAiPicksGrid, recsAiPicksLoad);
});


// =============================================================================
// CHATBOT WIDGET
// =============================================================================

(function () {
  const fab             = $("chatbotFab")
  const panel           = $("chatbotPanel")
  const closeBtn        = $("chatbotClose")
  const messagesEl      = $("chatbotMessages")
  const inputEl         = $("chatbotInput")
  const sendBtn         = $("chatbotSend")
  const suggestForm     = $("chatbotSuggestForm")
  const inputRow        = $("chatbotInputRow")
  const suggestSubmit   = $("suggestSubmitBtn")

  let currentMode = "mood"

  // ── Placeholders per mode ────────────────────────────────────────────────
  const PLACEHOLDERS = {
    mood:     "How are you feeling today?",
    interest: "What topic or genre interests you?",
    query:    "Any library question — hours, fines, policies…",
    suggest:  "",
  }

  // ── Open / Close ─────────────────────────────────────────────────────────
  fab.addEventListener("click", () => {
    panel.classList.toggle("hidden")
    if (!panel.classList.contains("hidden") && messagesEl.childElementCount === 0) {
      addBotBubble("Hi! I'm your Library AI assistant powered by WatsonX.\n\nPick a mode above:\n• Mood / Feel — get book suggestions based on how you feel\n• Interests — books by topic or genre\n• Ask Library — general library questions\n• Suggest Book — recommend a book for us to acquire")
    }
    if (!panel.classList.contains("hidden")) inputEl.focus()
  })
  closeBtn.addEventListener("click", () => panel.classList.add("hidden"))

  // Close on Escape
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && !panel.classList.contains("hidden")) panel.classList.add("hidden")
  })

  // ── Mode tabs ─────────────────────────────────────────────────────────────
  panel.querySelectorAll(".chatbot-mode-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      panel.querySelectorAll(".chatbot-mode-btn").forEach((b) => {
        b.classList.remove("chatbot-mode-btn--active")
        b.setAttribute("aria-selected", "false")
      })
      btn.classList.add("chatbot-mode-btn--active")
      btn.setAttribute("aria-selected", "true")
      currentMode = btn.dataset.mode

      if (currentMode === "suggest") {
        suggestForm.classList.remove("hidden")
        inputRow.classList.add("hidden")
      } else {
        suggestForm.classList.add("hidden")
        inputRow.classList.remove("hidden")
        inputEl.placeholder = PLACEHOLDERS[currentMode] || "Type a message…"
        inputEl.focus()
      }
    })
  })

  // ── Utilities ─────────────────────────────────────────────────────────────
  function addUserBubble(text) {
    const d = document.createElement("div")
    d.className = "chatbot-bubble chatbot-bubble--user"
    d.textContent = text
    messagesEl.appendChild(d)
    messagesEl.scrollTop = messagesEl.scrollHeight
  }

  function addBotBubble(text) {
    const d = document.createElement("div")
    d.className = "chatbot-bubble chatbot-bubble--bot"
    d.textContent = text
    messagesEl.appendChild(d)
    messagesEl.scrollTop = messagesEl.scrollHeight
    return d
  }

  function addTypingIndicator() {
    const d = document.createElement("div")
    d.className = "chatbot-bubble chatbot-bubble--typing"
    d.id = "chatbotTyping"
    d.textContent = "WatsonX AI is thinking…"
    messagesEl.appendChild(d)
    messagesEl.scrollTop = messagesEl.scrollHeight
    return d
  }

  function removeTyping() {
    const t = document.getElementById("chatbotTyping")
    if (t) t.remove()
  }

  // ── Send a chat message ───────────────────────────────────────────────────
  async function sendMessage() {
    const msg = inputEl.value.trim()
    if (!msg) return
    inputEl.value = ""
    addUserBubble(msg)
    const typing = addTypingIndicator()

    try {
      const res = await fetch("/api/chatbot", {
        method:  "POST",
        headers: { "Content-Type": "application/json" },
        body:    JSON.stringify({
          message:    msg,
          mode:       currentMode,
          student_id: window._getStudentId ? window._getStudentId() : "anonymous",
        }),
      })
      removeTyping()
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data = await res.json()
      addBotBubble(data.reply || "Sorry, I couldn't generate a response.")
    } catch (err) {
      removeTyping()
      addBotBubble("Sorry, something went wrong. Please try again.")
    }
  }

  sendBtn.addEventListener("click", sendMessage)
  inputEl.addEventListener("keydown", (e) => { if (e.key === "Enter") sendMessage() })

  // ── Suggest-book form submission ──────────────────────────────────────────
  suggestSubmit.addEventListener("click", async () => {
    const title  = ($("suggestTitle").value  || "").trim()
    const author = ($("suggestAuthor").value || "").trim()
    const reason = ($("suggestReason").value || "").trim()

    if (!title) {
      showToast("Please enter a book title.", true)
      return
    }

    suggestSubmit.disabled = true
    suggestSubmit.textContent = "Submitting…"

    try {
      const res = await fetch("/api/suggest-book", {
        method:  "POST",
        headers: { "Content-Type": "application/json" },
        body:    JSON.stringify({
          student_id: window._getStudentId ? window._getStudentId() : "anonymous",
          title, author, reason,
        }),
      })
      const data = await res.json()

      // Switch to message thread and show AI reply
      suggestForm.classList.add("hidden")
      inputRow.classList.remove("hidden")
      addUserBubble(`Suggest: "${title}"${author ? " by " + author : ""}`)
      addBotBubble(data.reply || "Your suggestion has been submitted. Thank you!")

      $("suggestTitle").value  = ""
      $("suggestAuthor").value = ""
      $("suggestReason").value = ""
    } catch {
      showToast("Failed to submit suggestion. Please try again.", true)
    } finally {
      suggestSubmit.disabled = false
      suggestSubmit.textContent = "Submit Suggestion"
    }
  })
})()
