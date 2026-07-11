# Library AI Agent

A full-stack AI-powered library assistant that helps students find relevant learning materials using **IBM Watson Natural Language Understanding**, **IBM WatsonX AI (Llama 3.3 70B)**, **IBM Robo automation rules**, and **MongoDB Atlas**.

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
                          MongoDB Atlas
                      (books · queries · reservations
                       reviews · automation_alerts)
```

---

## IBM Cloud Services

| Service | Purpose | SDK |
|---|---|---|
| **Watson Natural Language Understanding** | Parse student queries → extract keywords, entities, concepts | `ibm-watson` |
| **WatsonX AI (Llama 3.3 70B)** | Generate natural-language responses, reservation confirmations, recommendations | `ibm-watsonx-ai` |
| **IBM Robo (Automation Rules Engine)** | High-demand alerts, waitlist promotion, expiry, reorder alerts | Custom rule engine (`robo_rules.py`) |

---

## Quick Start

### 1. Prerequisites

- Python 3.11+
- IBM Cloud account with Watson NLU and WatsonX instances
- MongoDB Atlas (free tier at [mongodb.com/atlas](https://www.mongodb.com/atlas))

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

Copy `.env.example` to `.env` and fill in your credentials. **Never commit `.env` to git.**

```bash
cp .env.example .env
# then edit .env with your keys
```

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
├── .env.example                    # Safe template — copy to .env and fill in values
├── render.yaml                     # Render.com deployment config
│
├── backend/
│   ├── models/
│   │   └── db.py                   # MongoDB client, index bootstrap, document factories
│   ├── services/
│   │   ├── watson_nlu.py           # IBM Watson NLU wrapper
│   │   ├── watsonx_ai.py           # IBM WatsonX AI (Llama 3.3 70B) wrapper
│   │   └── library_lms.py          # Library management — search, reserve, return, log
│   ├── automation/
│   │   └── robo_rules.py           # IBM Robo automation rules (4 rules)
│   └── routes/
│       └── api.py                  # Flask blueprint — all REST endpoints
│
├── frontend/
│   ├── templates/
│   │   ├── index.html              # Main SPA shell
│   │   └── login.html              # Sign-in page
│   └── static/
│       ├── css/style.css           # Full UI design system
│       └── js/
│           ├── app.js              # Main frontend logic
│           ├── auth.js             # Firebase auth (main app)
│           └── login-auth.js       # Firebase auth (login page)
│
└── scripts/
    ├── seed_db.py                  # Seed 130+ books across 14 genres
    └── test_connections.py         # Verify all service connections
```

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/search` | NLU-powered book search + WatsonX AI summary |
| `GET`  | `/api/books` | Full catalogue (`?subject=fiction&limit=50`) |
| `GET`  | `/api/books/<id>` | Single book availability |
| `GET`  | `/api/books/high-demand` | Books above demand threshold |
| `POST` | `/api/reserve` | Reserve a book or join waitlist |
| `DELETE` | `/api/reserve/<id>` | Cancel a reservation |
| `POST` | `/api/reserve/<id>/return` | Return a book (records read duration, promotes waitlist) |
| `GET`  | `/api/reservations/<student_id>` | All reservations for a student |
| `GET`  | `/api/reading-log/<student_id>` | Full reading history (issued, returned, cancelled + duration) |
| `GET`  | `/api/recommendations/<student_id>` | WatsonX AI personalised recommendations |
| `GET`  | `/api/reviews/<book_id>` | Fetch reviews for a book |
| `POST` | `/api/reviews` | Submit review (Watson NLU sentiment analysis) |
| `GET`  | `/api/automation/run` | Manually trigger IBM Robo rules |
| `GET`  | `/api/automation/alerts` | View automation alerts |
| `GET`  | `/api/status` | Live health check for all services |
| `GET`  | `/api/explain` | AI pipeline explanation |

---

## IBM Robo Automation Rules

| Rule | Trigger | Action |
|---|---|---|
| `HIGH_DEMAND_ALERT` | `demand_score ≥ 10` | Create alert for librarian to order more copies |
| `AUTO_WAITLIST_PROMOTE` | Book returned | Promote oldest waitlisted student to active |
| `RESERVATION_EXPIRY` | `due_date` passed (7-day hold) | Cancel + restore copy + promote waitlist |
| `LOW_STOCK_REORDER` | 0 copies + `demand_score ≥ 15` | Create procurement alert |

Rules run automatically via APScheduler (`ENABLE_SCHEDULER=true`) or manually via `GET /api/automation/run`.

---

## IBM Cloud Setup Guide

### Watson NLU
1. Log into [IBM Cloud](https://cloud.ibm.com)
2. Create a **Natural Language Understanding** service (Lite tier is free)
3. Go to **Manage → Credentials** and copy the API Key and URL
4. Add to `.env`: `WATSON_NLU_API_KEY` and `WATSON_NLU_URL`

### WatsonX AI
1. Open [watsonx.ai](https://dataplatform.cloud.ibm.com/wx/home)
2. Create a **Project** and copy the **Project ID**
3. In IBM Cloud, create an **API Key** under **Manage → Access (IAM) → API Keys**
4. Add to `.env`: `WATSONX_API_KEY`, `WATSONX_PROJECT_ID`, `WATSONX_URL`

### MongoDB Atlas
1. Create a free cluster at [mongodb.com/atlas](https://www.mongodb.com/atlas)
2. Go to **Database Access** → add a user
3. Go to **Network Access** → allow `0.0.0.0/0`
4. Click **Connect → Drivers** and copy the connection string into `MONGO_URI`

---

## License

MIT
