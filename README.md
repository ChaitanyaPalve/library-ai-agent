# Library AI Agent

A full-stack AI-powered library assistant that helps students find relevant learning materials using **IBM Watson Natural Language Understanding**, **IBM WatsonX AI (Granite)**, **IBM Robo automation rules**, and **MongoDB**.

---

## Architecture

```
┌────────────────────────────────────────────────────────────┐
│                     Student Browser                        │
│              (HTML + CSS + Vanilla JS SPA)                 │
└───────────────────────┬────────────────────────────────────┘
                        │ HTTP/JSON
┌───────────────────────▼────────────────────────────────────┐
│              Flask REST API  (app.py)                      │
│  /api/search  /api/books  /api/reserve  /api/automation    │
└──┬────────────┬───────────────┬──────────────┬─────────────┘
   │            │               │              │
   ▼            ▼               ▼              ▼
Watson NLU  WatsonX AI    Library LMS      IBM Robo
(NLU query  (AI message   (MongoDB CRUD    (Automation
 analysis)   generation)   + availability) rules engine)
                               │
                               ▼
                          MongoDB Atlas / local
                      (books · queries · reservations
                       automation_alerts)
```

---

## IBM Cloud Services

| Service | Purpose | SDK |
|---|---|---|
| **Watson Natural Language Understanding** | Parse student queries → extract keywords, entities, concepts | `ibm-watson` |
| **WatsonX AI (Granite 13B Chat v2)** | Generate natural-language responses, reservation confirmations | `ibm-watsonx-ai` |
| **IBM Robo (Automation Rules Engine)** | High-demand alerts, waitlist promotion, expiry, reorder alerts | Custom rule engine (`robo_rules.py`) |

---

## Quick Start

### 1. Prerequisites

- Python 3.11+
- IBM Cloud account with Watson NLU and WatsonX instances
- MongoDB Atlas (free tier at [mongodb.com/atlas](https://www.mongodb.com/atlas))

### 2. Install dependencies

```bash
cd library-ai-agent
pip install -r requirements.txt
```

### 3. Configure environment

`.env` is already populated with working credentials. To rotate keys or switch accounts, edit `.env` directly.
For reference, `.env.example` shows the required variable names with placeholder values.

### 4. Seed the database

```bash
python scripts/seed_db.py
```

### 5. Test connections

```bash
python scripts/test_connections.py
```

### 6. Run locally

```bash
python app.py
```

Open **http://localhost:5000** in your browser.

---

## Project Structure

```
library-ai-agent/
├── app.py                          # Flask app factory + entry point
├── requirements.txt
├── .env                            # Real secrets — gitignored, never commit
├── .env.example                    # Safe template with placeholder values
├── .gitignore                      # Blocks .env from git
├── render.yaml                     # Render deployment config
├── vercel.json                     # Vercel deployment config
│
├── backend/
│   ├── models/
│   │   └── db.py                   # MongoDB client, index bootstrap, document factories
│   ├── services/
│   │   ├── watson_nlu.py           # IBM Watson NLU wrapper
│   │   ├── watsonx_ai.py           # IBM WatsonX AI (Granite) wrapper
│   │   └── library_lms.py          # Library management system – search, reserve, log
│   ├── automation/
│   │   └── robo_rules.py           # IBM Robo automation rules (4 rules)
│   └── routes/
│       └── api.py                  # Flask blueprint – all REST endpoints
│
├── frontend/
│   ├── templates/
│   │   └── index.html              # Single-page app shell
│   └── static/
│       ├── css/style.css           # Full UI stylesheet
│       └── js/app.js               # Frontend logic
│
└── scripts/
    ├── seed_db.py                  # Seed 18 sample academic books
    └── test_connections.py         # Verify all service connections
```

---

## API Reference

### `POST /api/search`
Analyse a student query with Watson NLU and return matching books + WatsonX AI summary.

**Request body:**
```json
{ "student_id": "s001", "query": "I need books on machine learning" }
```

**Response:**
```json
{
  "query": "...",
  "search_terms": ["machine learning", "neural network"],
  "books": [...],
  "ai_message": "Great news! I found 3 books...",
  "total": 3
}
```

---

### `GET /api/books/<book_id>`
Returns availability info for a single book.

---

### `GET /api/books/high-demand?threshold=5`
Returns books with demand score above the threshold.

---

### `POST /api/reserve`
Reserve a book or join the waitlist.

**Request body:**
```json
{ "student_id": "s001", "book_id": "<mongo_object_id>" }
```

**Response (201 active / 202 waitlisted):**
```json
{
  "status": "active",
  "book_title": "Deep Learning",
  "ai_message": "Your reservation is confirmed...",
  ...
}
```

---

### `DELETE /api/reserve/<reservation_id>`
Cancel a reservation (returns copy to pool + promotes waitlist).

---

### `GET /api/automation/run`
Manually trigger all IBM Robo automation rules.

---

### `GET /api/automation/alerts`
View current automation alerts (high-demand, low-stock).

---

## IBM Robo Automation Rules

| Rule | Trigger | Action |
|---|---|---|
| `HIGH_DEMAND_ALERT` | demand_score ≥ 10 | Flag book, create alert for librarian |
| `AUTO_WAITLIST_PROMOTE` | Book returned (copy available) | Promote oldest waitlisted reservation to active |
| `RESERVATION_EXPIRY` | Active reservation > 14 days | Cancel + promote next in waitlist |
| `LOW_STOCK_REORDER` | 0 copies + demand ≥ 15 | Create procurement alert |

Rules run automatically via APScheduler (set `ENABLE_SCHEDULER=true` in `.env`) or manually via `GET /api/automation/run`.

---

## IBM Cloud Setup Guide

### Watson NLU
1. Log into [IBM Cloud](https://cloud.ibm.com)
2. Create a **Natural Language Understanding** service (Lite tier is free)
3. Go to **Manage → Credentials** and copy the API Key and URL
4. Paste into `.env`: `WATSON_NLU_API_KEY` and `WATSON_NLU_URL`

### WatsonX AI
1. Open [watsonx.ai](https://dataplatform.cloud.ibm.com/wx/home)
2. Create a **Project**
3. Under **Manage → General**, copy the **Project ID**
4. In IBM Cloud, create an **API Key** under **Manage → Access (IAM) → API Keys**
5. Paste into `.env`: `WATSONX_API_KEY`, `WATSONX_PROJECT_ID`, `WATSONX_URL`

### MongoDB
- **Local**: Start MongoDB on `localhost:27017` (default)
- **Atlas**: Create a free cluster at [mongodb.com/atlas](https://www.mongodb.com/atlas), copy the connection string into `MONGO_URI`

---

## License

MIT

///only for the editor///
check for reservation and waitlist same person can't issue and hold the book 
add fiction section 
add more books 
make it more user friendly 
