"""
Flask API routes for the Library AI Agent.

Endpoints:
  GET  /api/status              – Live health check for all services
  GET  /api/explain             – IBM Cloud + AI architecture explanation
  POST /api/search              – NLU-powered book search
  GET  /api/books/<id>          – Single book detail + availability
  GET  /api/books/high-demand   – Books above demand threshold
  POST /api/reserve             – Reserve a book / join waitlist
  DELETE /api/reserve/<id>      – Cancel a reservation
  GET  /api/automation/run      – Manually trigger Robo rules
  GET  /api/automation/alerts   – View current automation alerts
"""

import time
import os
from flask import Blueprint, request, jsonify

from backend.services.watson_nlu   import analyse_query, analyse_sentiment
from backend.services.watsonx_ai   import (
    generate_search_response, generate_reservation_message, recommend_books,
    generate_chatbot_response, generate_suggest_book_reply,
    generate_book_description, verify_book_is_real,
)
from backend.services.library_lms  import (
    search_books, check_availability,
    reserve_book, cancel_reservation, return_book,
    log_query, get_high_demand_books, get_all_books,
    validate_student_id, upsert_student,
    add_review, get_reviews, get_reading_history, get_reading_log,
)
from backend.automation.robo_rules import run_all_rules
from backend.models.db import get_db, get_client

api = Blueprint("api", __name__, url_prefix="/api")


# ---------------------------------------------------------------------------
# Health / orchestration status
# ---------------------------------------------------------------------------

@api.route("/status", methods=["GET"])
def status():
    """
    Live check of every external service.
    Returns per-service status, latency, and a top-level ok flag.
    """
    services = {}

    # 1. MongoDB Atlas
    t0 = time.monotonic()
    try:
        client = get_client()
        db = client["library"]
        book_count = db.books.count_documents({})
        client.close()
        services["mongodb"] = {
            "ok": True,
            "latency_ms": round((time.monotonic() - t0) * 1000),
            "detail": f"{book_count} books in catalogue",
            "label": "MongoDB Atlas",
            "description": "Document database storing books, reservations, queries and automation alerts.",
        }
    except Exception as exc:
        services["mongodb"] = {
            "ok": False,
            "latency_ms": round((time.monotonic() - t0) * 1000),
            "error": str(exc)[:200],
            "fix": "Go to MongoDB Atlas → Network Access → Add IP 0.0.0.0/0 (allow all) or your current IP",
            "label": "MongoDB Atlas",
            "description": "Document database storing books, reservations, queries and automation alerts.",
        }

    # 2. IBM Watson NLU
    t0 = time.monotonic()
    try:
        result = analyse_query("machine learning")
        terms = result.get("search_terms", [])
        services["watson_nlu"] = {
            "ok": True,
            "latency_ms": round((time.monotonic() - t0) * 1000),
            "detail": f"Extracted {len(terms)} terms: {', '.join(terms[:4])}",
            "label": "IBM Watson NLU",
            "description": "Natural Language Understanding — parses student queries into keywords, entities and concepts.",
            "region": os.getenv("WATSON_NLU_URL", "")[:50],
        }
    except Exception as exc:
        services["watson_nlu"] = {
            "ok": False,
            "latency_ms": round((time.monotonic() - t0) * 1000),
            "error": str(exc)[:200],
            "fix": "Check WATSON_NLU_API_KEY and WATSON_NLU_URL in .env / deployment env vars",
            "label": "IBM Watson NLU",
            "description": "Natural Language Understanding — parses student queries into keywords, entities and concepts.",
        }

    # 3. IBM WatsonX AI
    t0 = time.monotonic()
    try:
        reply = generate_search_response("machine learning", [
            {"title": "Deep Learning", "author": "Goodfellow", "available_copies": 1}
        ])
        services["watsonx_ai"] = {
            "ok": True,
            "latency_ms": round((time.monotonic() - t0) * 1000),
            "detail": f"Model responded ({len(str(reply))} chars)",
            "model": os.getenv("WATSONX_MODEL_ID", "meta-llama/llama-3-3-70b-instruct"),
            "label": "IBM WatsonX AI",
            "description": "Foundation model (Llama 3.3 70B via IBM WatsonX) — generates natural-language search summaries and reservation confirmations.",
            "region": os.getenv("WATSONX_URL", "")[:50],
        }
    except Exception as exc:
        services["watsonx_ai"] = {
            "ok": False,
            "latency_ms": round((time.monotonic() - t0) * 1000),
            "error": str(exc)[:200],
            "fix": "Check WATSONX_API_KEY, WATSONX_PROJECT_ID, WATSONX_MODEL_ID in .env",
            "label": "IBM WatsonX AI",
            "description": "Foundation model — generates natural-language search summaries and reservation confirmations.",
        }

    all_ok = all(s["ok"] for s in services.values())
    return jsonify({
        "ok": all_ok,
        "services": services,
        "checked_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }), 200 if all_ok else 207


# ---------------------------------------------------------------------------
# AI + IBM Cloud architecture explanation
# ---------------------------------------------------------------------------

_IBM_EXPLAIN = {
    "title": "How IBM AI Powers This Library",
    "pipeline": [
        {
            "step": 1,
            "service": "IBM Watson NLU",
            "role": "Query Understanding",
            "what_it_does": (
                "When you type a query like 'I need books on neural networks', Watson NLU "
                "analyses the text and extracts keywords, entities, categories and concepts. "
                "It understands that 'neural networks' is an AI concept and 'books' is the intent."
            ),
            "output": "Structured search terms: ['neural networks', 'deep learning', 'machine learning']",
            "ibm_cloud_path": "IBM Cloud → Watson NLU → Natural Language Understanding service",
        },
        {
            "step": 2,
            "service": "MongoDB Atlas",
            "role": "Catalogue Search",
            "what_it_does": (
                "The NLU-extracted terms drive a regex OR-query across book titles, authors "
                "and subject tags. Results are ranked by demand_score (how many students have "
                "reserved or searched this book before)."
            ),
            "output": "Ranked list of matching books with availability status",
            "ibm_cloud_path": "External — MongoDB Atlas (M0 free tier)",
        },
        {
            "step": 3,
            "service": "IBM WatsonX AI (Llama 3.3 70B)",
            "role": "Natural Language Response",
            "what_it_does": (
                "The matching books are passed as context to a foundation model on IBM WatsonX. "
                "The model generates a friendly, human-readable summary: confirming what was found, "
                "highlighting the most relevant title, and offering to help with reservations. "
                "WatsonX runs the model in IBM's cloud — no GPU needed locally."
            ),
            "output": "A conversational reply like: 'Great news! I found 3 books on neural networks...'",
            "ibm_cloud_path": "IBM Cloud → WatsonX → Foundation Models → meta-llama/llama-3-3-70b-instruct",
        },
        {
            "step": 4,
            "service": "IBM Robo Automation",
            "role": "Proactive Library Management",
            "what_it_does": (
                "IBM Robo is a rule engine that runs automatically (via APScheduler) or on demand. "
                "It scans the catalogue for: high-demand books (demand_score ≥ 10) to flag for reorder, "
                "waitlisted students to promote when a copy is returned, expired reservations to release, "
                "and zero-stock high-demand books to raise procurement alerts."
            ),
            "output": "Automation alerts stored in MongoDB, visible on the Dashboard panel",
            "ibm_cloud_path": "Custom rule engine — runs inside the Flask app (backend/automation/robo_rules.py)",
        },
    ],
    "architecture_summary": (
        "Student query → Watson NLU (extract intent) → MongoDB (search catalogue) "
        "→ WatsonX AI (generate response) → Student. "
        "In parallel: IBM Robo watches the catalogue and fires alerts proactively."
    ),
    "ibm_services_used": [
        {"name": "Watson Natural Language Understanding", "tier": "Lite (free)", "region": "au-syd"},
        {"name": "WatsonX AI (Llama 3.3 70B via IBM)", "tier": "Pay-as-you-go", "region": "au-syd"},
    ],
}


@api.route("/explain", methods=["GET"])
def explain():
    """Return a structured explanation of every AI/IBM service in the pipeline."""
    return jsonify(_IBM_EXPLAIN)


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------

@api.route("/search", methods=["POST"])
def search():
    """
    Body: { "student_id": "s001", "query": "I need a book on machine learning" }
    Returns: books list + AI-generated summary.
    """
    body = request.get_json(force=True)
    student_id = body.get("student_id", "anonymous")
    query_text = body.get("query", "").strip()

    if not query_text:
        return jsonify({"error": "query is required"}), 400

    # 1. Watson NLU analysis
    nlu_result = analyse_query(query_text)
    search_terms = nlu_result["search_terms"]

    # 2. MongoDB search
    books = search_books(search_terms, limit=10)

    # 3. Log query
    book_ids = [b["_id"] for b in books]
    log_query(student_id, query_text, book_ids)

    # 4. WatsonX AI natural language summary
    ai_message = generate_search_response(query_text, books)

    return jsonify({
        "query": query_text,
        "search_terms": search_terms,
        "books": books,
        "ai_message": ai_message,
        "total": len(books),
    })


# ---------------------------------------------------------------------------
# All books catalogue listing
# ---------------------------------------------------------------------------

@api.route("/mood-books/<mood>", methods=["GET"])
def mood_books(mood: str):
    """
    GET /api/mood-books/<mood>  — returns books tagged with mood:<mood>
    Supports: sad, happy, stressed, adventurous, motivated, curious, romantic, bored
    """
    tag = f"mood:{mood.lower()}"
    db = get_db()
    cursor = db.books.find({"subject_tags": {"$regex": tag, "$options": "i"}}).sort("title", 1).limit(50)
    results = []
    for doc in cursor:
        doc["_id"] = str(doc["_id"])
        results.append(doc)
    return jsonify({"books": results, "total": len(results), "mood": mood})


@api.route("/books", methods=["GET"])
def all_books():
    """
    GET /api/books?subject=fiction&skip=0&limit=200
    Returns all books, optionally filtered by subject tag.
    """
    subject = request.args.get("subject", None)
    skip    = int(request.args.get("skip",  0))
    limit   = min(int(request.args.get("limit", 50)), 200)
    books   = get_all_books(skip=skip, limit=limit, subject=subject)
    return jsonify({"books": books, "total": len(books), "skip": skip, "limit": limit})


# ---------------------------------------------------------------------------
# High-demand books listing  — must be registered BEFORE /books/<book_id>
# so Flask does not match "high-demand" as a book_id variable.
# ---------------------------------------------------------------------------

@api.route("/books/high-demand", methods=["GET"])
def high_demand():
    threshold = int(request.args.get("threshold", 5))
    limit     = int(request.args.get("limit", 20))
    books = get_high_demand_books(threshold=threshold, limit=limit)
    return jsonify({"books": books, "total": len(books)})


# ---------------------------------------------------------------------------
# Book detail
# ---------------------------------------------------------------------------

@api.route("/books/<book_id>", methods=["GET"])
def book_detail(book_id: str):
    availability = check_availability(book_id)
    if "error" in availability:
        return jsonify(availability), 404
    return jsonify(availability)


# ---------------------------------------------------------------------------
# Reservations
# ---------------------------------------------------------------------------

@api.route("/reserve", methods=["POST"])
def reserve():
    """
    Body: { "student_id": "s001", "book_id": "<mongo_id>" }
    """
    body = request.get_json(force=True)
    student_id = body.get("student_id", "").strip()
    book_id    = body.get("book_id", "").strip()

    if not book_id:
        return jsonify({"error": "book_id is required"}), 400

    id_error = validate_student_id(student_id)
    if id_error:
        return jsonify({"error": id_error}), 400

    reservation = reserve_book(student_id, book_id)
    if "error" in reservation:
        return jsonify(reservation), 400

    # WatsonX AI confirmation message
    book_info = {"title": reservation.get("book_title", ""), "author": reservation.get("book_author", "")}
    ai_message = generate_reservation_message(student_id, book_info, reservation["status"])
    reservation["ai_message"] = ai_message

    code = 201 if reservation["status"] == "active" else 202
    return jsonify(reservation), code


@api.route("/reserve/<reservation_id>", methods=["DELETE"])
def cancel(reservation_id: str):
    result = cancel_reservation(reservation_id)
    if "error" in result:
        return jsonify(result), 404
    return jsonify(result)


@api.route("/reserve/<reservation_id>/return", methods=["POST"])
def return_reservation(reservation_id: str):
    """POST /api/reserve/<id>/return — mark a book as returned."""
    result = return_book(reservation_id)
    if "error" in result:
        return jsonify(result), 400
    return jsonify(result)


# ---------------------------------------------------------------------------
# Student persistence
# ---------------------------------------------------------------------------

@api.route("/students", methods=["POST"])
def persist_student():
    """
    Body: { "student_id": "s001", "firebase_uid": "abc123", "email": "student@uni.edu" }
    Upserts the student document in MongoDB.  Called from auth.js on sign-in.
    firebase_uid is optional for demo/local accounts (falls back to "demo").
    """
    body       = request.get_json(force=True)
    student_id = body.get("student_id", "").strip()
    firebase_uid = body.get("firebase_uid", "demo").strip() or "demo"
    email      = body.get("email", "").strip() or None

    id_error = validate_student_id(student_id)
    if id_error:
        return jsonify({"error": id_error}), 400

    doc = upsert_student(student_id, firebase_uid, email)
    return jsonify(doc), 200


@api.route("/automation/run", methods=["GET"])
def automation_run():
    report = run_all_rules()
    return jsonify(report)


@api.route("/automation/alerts", methods=["GET"])
def automation_alerts():
    db = get_db()
    alerts = list(db.automation_alerts.find({}, {"_id": 0}))
    return jsonify({"alerts": alerts, "total": len(alerts)})


# ---------------------------------------------------------------------------
# Book reviews + sentiment  (Watson NLU)
# ---------------------------------------------------------------------------

@api.route("/reviews/<book_id>", methods=["GET"])
def reviews_get(book_id: str):
    """GET /api/reviews/<book_id>  — fetch all reviews for a book."""
    reviews = get_reviews(book_id)
    return jsonify({"reviews": reviews, "total": len(reviews)})


@api.route("/reviews", methods=["POST"])
def reviews_post():
    """
    POST /api/reviews
    Body: { "student_id": "s001", "book_id": "<id>", "review": "Great book!" }
    Watson NLU analyses sentiment before storing.
    """
    body        = request.get_json(force=True)
    student_id  = body.get("student_id", "anonymous").strip()
    book_id     = body.get("book_id", "").strip()
    review_text = body.get("review", "").strip()

    if not book_id:
        return jsonify({"error": "book_id is required"}), 400
    if not review_text:
        return jsonify({"error": "review text is required"}), 400

    # Watson NLU sentiment analysis
    try:
        sentiment = analyse_sentiment(review_text)
    except Exception as exc:
        sentiment = {"label": "neutral", "score": 0.0, "error": str(exc)[:120]}

    doc = add_review(
        student_id, book_id, review_text,
        sentiment["label"], sentiment.get("score", 0.0),
    )
    if "error" in doc:
        return jsonify(doc), 400
    doc["sentiment"] = sentiment
    return jsonify(doc), 201


# ---------------------------------------------------------------------------
# WatsonX AI recommendations  (reading history → personalised suggestions)
# ---------------------------------------------------------------------------

@api.route("/recommendations/<student_id>", methods=["GET"])
def recommendations(student_id: str):
    """
    GET /api/recommendations/<student_id>
    Returns an AI-generated reading recommendation based on reservation history.
    """
    history = get_reading_history(student_id)
    ai_text = recommend_books(history)
    return jsonify({
        "student_id": student_id,
        "history_count": len(history),
        "history": history,
        "recommendations": ai_text,
    })


# ---------------------------------------------------------------------------
# User profile  (reading history + review stats)
# ---------------------------------------------------------------------------

@api.route("/reservations/<student_id>", methods=["GET"])
def student_reservations(student_id: str):
    """
    GET /api/reservations/<student_id>
    Returns all reservations for this student, with book title/author joined in.
    """
    results = get_reading_log(student_id, limit=50)
    return jsonify({"reservations": results, "total": len(results)})


@api.route("/reading-log/<student_id>", methods=["GET"])
def reading_log(student_id: str):
    """
    GET /api/reading-log/<student_id>
    Full reading log: issued, returned (with read_duration), cancelled.
    """
    log = get_reading_log(student_id, limit=100)
    return jsonify({"log": log, "total": len(log)})


@api.route("/profile/<student_id>", methods=["GET"])
def user_profile(student_id: str):
    """
    GET /api/profile/<student_id>
    Returns the student's reading history and review count from MongoDB.
    """
    db      = get_db()
    history = get_reading_history(student_id, limit=20)
    review_count = db.reviews.count_documents({"student_id": student_id})
    student = db.students.find_one({"student_id": student_id}, {"_id": 0}) or {}
    return jsonify({
        "student_id": student_id,
        "student": student,
        "reading_history": history,
        "history_count": len(history),
        "review_count": review_count,
    })


# ---------------------------------------------------------------------------
# Chatbot  (mood/interest suggestions, student queries)
# ---------------------------------------------------------------------------

@api.route("/chatbot", methods=["POST"])
def chatbot():
    """
    POST /api/chatbot
    Body: { "message": "I feel adventurous", "mode": "mood", "student_id": "s001" }
    mode: "mood" | "interest" | "query" | "general"
    Returns: { "reply": "..." }
    """
    body    = request.get_json(force=True)
    message = body.get("message", "").strip()
    mode    = body.get("mode", "general").strip()

    if not message:
        return jsonify({"error": "message is required"}), 400

    student_id = body.get("student_id", "anonymous")
    log_query(student_id, f"[chatbot:{mode}] {message}", [])

    reply = generate_chatbot_response(message, mode)
    return jsonify({"reply": reply, "mode": mode})


# ---------------------------------------------------------------------------
# Suggest book for library acquisition
# ---------------------------------------------------------------------------

@api.route("/suggest-book", methods=["POST"])
def suggest_book():
    """
    POST /api/suggest-book
    Body: { "student_id": "s001", "title": "...", "author": "...", "reason": "..." }
    Verifies the book is real, stores the suggestion, and returns an AI acknowledgement.
    """
    body       = request.get_json(force=True)
    student_id = body.get("student_id", "anonymous").strip()
    title      = body.get("title", "").strip()
    author     = body.get("author", "").strip()
    reason     = body.get("reason", "").strip()

    if not title:
        return jsonify({"error": "title is required"}), 400

    # Check if the book already exists in our catalogue
    db = get_db()
    existing = db.books.find_one(
        {"title": {"$regex": f"^{title}$", "$options": "i"}},
        {"_id": 1},
    )
    if existing:
        return jsonify({
            "reply": f'"{title}" is already in our catalogue — search for it to issue a copy!',
            "title": title,
            "author": author,
            "already_exists": True,
        }), 200

    # Ask AI if the book is a real published title
    is_real = verify_book_is_real(title, author or "Unknown")
    if not is_real:
        return jsonify({
            "reply": f'We couldn\'t confirm "{title}" as a published book. Please double-check the title and author.',
            "title": title,
            "author": author,
            "not_real": True,
        }), 200

    # Persist suggestion (avoid duplicates)
    from datetime import datetime as _dt
    db.book_suggestions.update_one(
        {"title": {"$regex": f"^{title}$", "$options": "i"}},
        {"$setOnInsert": {
            "student_id": student_id,
            "title":      title,
            "author":     author or "Unknown",
            "reason":     reason,
            "status":     "pending",
            "created_at": _dt.utcnow(),
        }},
        upsert=True,
    )

    reply = generate_suggest_book_reply(title, author or "Unknown", reason or "No reason provided")
    return jsonify({"reply": reply, "title": title, "author": author}), 201


# ---------------------------------------------------------------------------
# Suggested books (real books students suggested, not yet in catalogue)
# ---------------------------------------------------------------------------

@api.route("/suggestions", methods=["GET"])
def get_suggestions():
    """
    GET /api/suggestions
    Returns pending book suggestions that are confirmed real and not yet in the catalogue.
    Each result includes an AI-generated one-sentence description.
    """
    db = get_db()
    cursor = db.book_suggestions.find(
        {"status": "pending"},
        {"_id": 0, "title": 1, "author": 1, "reason": 1, "created_at": 1},
    ).sort("created_at", -1).limit(20)

    suggestions = []
    for doc in cursor:
        title  = doc.get("title", "")
        author = doc.get("author", "Unknown")
        # Generate a short description (cached — skip if already done)
        try:
            desc = generate_book_description(title, author)
        except Exception:
            desc = ""
        suggestions.append({
            "title":       title,
            "author":      author,
            "reason":      doc.get("reason", ""),
            "description": desc,
        })

    return jsonify({"suggestions": suggestions, "total": len(suggestions)})


# ---------------------------------------------------------------------------
# On-demand book description (lazy, cached in DB)
# ---------------------------------------------------------------------------

@api.route("/book-description", methods=["POST"])
def book_description():
    """
    POST /api/book-description
    Body: { "book_id": "<id>" }
    Returns (and caches) a one-sentence AI description for the book.
    """
    body    = request.get_json(force=True)
    book_id = body.get("book_id", "").strip()
    if not book_id:
        return jsonify({"error": "book_id is required"}), 400

    from bson import ObjectId
    from bson.errors import InvalidId
    db = get_db()
    try:
        obj_id = ObjectId(book_id)
    except InvalidId:
        return jsonify({"error": "Invalid book ID"}), 400

    book = db.books.find_one({"_id": obj_id}, {"title": 1, "author": 1, "description": 1})
    if not book:
        return jsonify({"error": "Book not found"}), 404

    # Return cached description if already stored
    if book.get("description"):
        return jsonify({"book_id": book_id, "description": book["description"]})

    # Generate and cache
    try:
        desc = generate_book_description(book["title"], book.get("author", "Unknown"))
    except Exception as exc:
        return jsonify({"error": str(exc)[:120]}), 500

    db.books.update_one({"_id": obj_id}, {"$set": {"description": desc}})
    return jsonify({"book_id": book_id, "description": desc})
