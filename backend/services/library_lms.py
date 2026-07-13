"""
Library Management System (LMS) Integration Layer.

Provides functions to:
  - Search books by NLU-derived search terms
  - Check real-time availability
  - Reserve a book (or place on waitlist)
  - Cancel / complete a reservation
  - Record student queries for analytics
  - Upsert student records (student_id + Firebase UID)

All persistence is via MongoDB (models.db).
"""

from datetime import datetime, timedelta
from bson import ObjectId
from bson.errors import InvalidId
from pymongo import ReturnDocument

from backend.models.db import get_db, make_query, make_reservation


# ---------------------------------------------------------------------------
# Book search
# ---------------------------------------------------------------------------

def search_books(search_terms: list[str], limit: int = 10) -> list[dict]:
    """
    Full-text + tag search using the NLU-extracted terms.
    Returns books sorted by relevance (demand_score desc).
    """
    if not search_terms:
        return []

    db = get_db()

    # Build an OR query across title, author and subject_tags
    or_clauses = []
    for term in search_terms:
        regex = {"$regex": term, "$options": "i"}
        or_clauses.append({"title": regex})
        or_clauses.append({"author": regex})
        or_clauses.append({"subject_tags": regex})

    cursor = (
        db.books.find({"$or": or_clauses})
        .sort("demand_score", -1)
        .limit(limit)
    )
    results = []
    for doc in cursor:
        doc["_id"] = str(doc["_id"])
        results.append(doc)
    return results


# ---------------------------------------------------------------------------
# Availability
# ---------------------------------------------------------------------------

def check_availability(book_id: str) -> dict:
    """Return availability info for a single book."""
    db = get_db()
    try:
        obj_id = ObjectId(book_id)
    except InvalidId:
        return {"error": "Invalid book ID"}

    book = db.books.find_one({"_id": obj_id}, {"title": 1, "available_copies": 1, "total_copies": 1})
    if not book:
        return {"error": "Book not found"}

    return {
        "book_id": book_id,
        "title": book["title"],
        "total_copies": book["total_copies"],
        "available_copies": book["available_copies"],
        "available": book["available_copies"] > 0,
    }


# ---------------------------------------------------------------------------
# Reservations
# ---------------------------------------------------------------------------

def validate_student_id(student_id: str) -> str | None:
    """
    Return an error string if *student_id* is invalid, else None.
    Rules: non-empty, 2–20 chars, alphanumeric + hyphens/underscores only.
    """
    import re
    if not student_id:
        return "student_id is required"
    if len(student_id) < 2 or len(student_id) > 20:
        return "student_id must be 2–20 characters"
    if not re.match(r"^[A-Za-z0-9_\-]+$", student_id):
        return "student_id may only contain letters, digits, hyphens and underscores"
    return None


def reserve_book(student_id: str, book_id: str) -> dict:
    """
    Issue a book to a student.

    - If copies are available and total active issues < 2 → status = "active", decrement available_copies
    - If no copies available or total active issues >= 2  → status = "waitlisted"
    - If the student already has an active OR waitlisted hold → error (duplicate guard)
    Returns the reservation document with an "ai_message" placeholder.
    """
    # Validate student ID before touching the database
    id_error = validate_student_id(student_id)
    if id_error:
        return {"error": id_error}

    db = get_db()
    try:
        obj_id = ObjectId(book_id)
    except InvalidId:
        return {"error": "Invalid book ID"}

    # ── Duplicate-hold guard ─────────────────────────────────────────────────
    existing = db.reservations.find_one({
        "student_id": student_id,
        "book_id": obj_id,
        "status": {"$in": ["active", "waitlisted"]},
    })
    if existing:
        label = "issue" if existing["status"] == "active" else "waitlist spot"
        return {
            "error": (
                f"You already have an active {label} for this book. "
                "Cancel it first if you want to change your hold type."
            )
        }

    # ── Check active-issue limit (max 2 per book) ────────────────────────────
    active_count = db.reservations.count_documents({
        "book_id": obj_id,
        "status": "active",
    })

    # Atomically decrement if available AND under the 2-issue limit
    if active_count < 2:
        book = db.books.find_one_and_update(
            {"_id": obj_id, "available_copies": {"$gt": 0}},
            {
                "$inc": {"available_copies": -1, "demand_score": 1},
                "$set": {"updated_at": datetime.utcnow()},
            },
            return_document=ReturnDocument.AFTER,
        )
    else:
        book = None

    if book:
        status = "active"
    else:
        # No copies or limit reached – still bump demand_score for prioritisation
        db.books.update_one(
            {"_id": obj_id},
            {"$inc": {"demand_score": 1}, "$set": {"updated_at": datetime.utcnow()}},
        )
        book = db.books.find_one({"_id": obj_id})
        status = "waitlisted"

    if not book:
        return {"error": "Book not found"}

    reservation = make_reservation(student_id, obj_id, status)
    result = db.reservations.insert_one(reservation)
    reservation["_id"] = str(result.inserted_id)
    reservation["book_id"] = book_id
    reservation["book_title"] = book.get("title")
    reservation["book_author"] = book.get("author")
    reservation["status"] = status
    # Serialize datetime fields for JSON
    reservation["issued_at"]  = reservation["issued_at"].isoformat()  if reservation.get("issued_at")  else None
    reservation["due_date"]   = reservation["due_date"].isoformat()   if reservation.get("due_date")   else None
    reservation["created_at"] = reservation["created_at"].isoformat() if reservation.get("created_at") else None
    reservation["updated_at"] = reservation["updated_at"].isoformat() if reservation.get("updated_at") else None
    reservation["book_id"]    = book_id  # ensure string (overwrite ObjectId)
    return reservation


def cancel_reservation(reservation_id: str) -> dict:
    """Cancel a reservation and return available copy if it was active."""
    db = get_db()
    try:
        res_obj = ObjectId(reservation_id)
    except InvalidId:
        return {"error": "Invalid reservation ID"}

    reservation = db.reservations.find_one({"_id": res_obj})
    if not reservation:
        return {"error": "Reservation not found"}

    if reservation["status"] == "active":
        # Return the copy
        db.books.update_one(
            {"_id": reservation["book_id"]},
            {"$inc": {"available_copies": 1}, "$set": {"updated_at": datetime.utcnow()}},
        )

    db.reservations.update_one(
        {"_id": res_obj},
        {"$set": {"status": "cancelled", "updated_at": datetime.utcnow()}},
    )
    return {"reservation_id": reservation_id, "status": "cancelled"}


def return_book(reservation_id: str) -> dict:
    """
    Mark a reservation as 'returned', restore the copy to inventory,
    and record how long the student held the book (read_duration_days).
    """
    db = get_db()
    try:
        res_obj = ObjectId(reservation_id)
    except InvalidId:
        return {"error": "Invalid reservation ID"}

    reservation = db.reservations.find_one({"_id": res_obj})
    if not reservation:
        return {"error": "Reservation not found"}

    if reservation["status"] != "active":
        return {"error": f"Cannot return — reservation is '{reservation['status']}'"}

    now = datetime.utcnow()
    issued_at = reservation.get("issued_at") or reservation.get("created_at")
    read_duration_days = None
    if issued_at:
        delta = now - issued_at
        read_duration_days = round(delta.total_seconds() / 86400, 1)

    # Restore the book copy
    db.books.update_one(
        {"_id": reservation["book_id"]},
        {"$inc": {"available_copies": 1}, "$set": {"updated_at": now}},
    )

    db.reservations.update_one(
        {"_id": res_obj},
        {"$set": {
            "status": "returned",
            "returned_at": now,
            "read_duration_days": read_duration_days,
            "updated_at": now,
        }},
    )

    # Try to promote the first waitlisted student for this book
    next_wait = db.reservations.find_one(
        {"book_id": reservation["book_id"], "status": "waitlisted"},
        sort=[("created_at", 1)],
    )
    promoted = None
    if next_wait:
        # Decrement the copy we just restored for the promoted student
        db.books.update_one(
            {"_id": reservation["book_id"]},
            {"$inc": {"available_copies": -1}, "$set": {"updated_at": now}},
        )
        db.reservations.update_one(
            {"_id": next_wait["_id"]},
            {"$set": {
                "status": "active",
                "issued_at": now,
                "due_date": now + timedelta(days=7),
                "updated_at": now,
            }},
        )
        promoted = next_wait["student_id"]

    return {
        "reservation_id": reservation_id,
        "status": "returned",
        "read_duration_days": read_duration_days,
        "promoted_student": promoted,
    }


def get_reading_log(student_id: str, limit: int = 50) -> list[dict]:
    """
    Return the student's complete book history:
      - issued (active)
      - returned (with read_duration_days)
      - cancelled (kept as record)
    Sorted newest first.
    """
    db = get_db()
    cursor = db.reservations.find(
        {"student_id": student_id},
    ).sort("created_at", -1).limit(limit)

    results = []
    for r in cursor:
        book_id = r.get("book_id")
        book = db.books.find_one({"_id": book_id}, {"title": 1, "author": 1}) if book_id else None
        issued_at   = r.get("issued_at") or r.get("created_at")
        returned_at = r.get("returned_at")
        due_date    = r.get("due_date")
        results.append({
            "_id":               str(r["_id"]),
            "book_id":           str(book_id) if book_id else "",
            "book_title":        book["title"]  if book else "",
            "book_author":       book["author"] if book else "",
            "status":            r.get("status", ""),
            "issued_at":         issued_at.isoformat()   if issued_at   else None,
            "due_date":          due_date.isoformat()    if due_date    else None,
            "returned_at":       returned_at.isoformat() if returned_at else None,
            "read_duration_days": r.get("read_duration_days"),
            "created_at":        r["created_at"].isoformat() if r.get("created_at") else None,
        })
    return results


# ---------------------------------------------------------------------------
# Query logging / Student persistence
# ---------------------------------------------------------------------------

def upsert_student(student_id: str, firebase_uid: str, email: str | None = None) -> dict:
    """
    Insert or update a student document keyed by *student_id*.
    Called on sign-in to persist the Firebase UID alongside the student ID.
    Returns the upserted document (without MongoDB _id).
    """
    db = get_db()
    now = datetime.utcnow()
    result = db.students.find_one_and_update(
        {"student_id": student_id},
        {
            "$set": {
                "firebase_uid": firebase_uid,
                "email": email,
                "updated_at": now,
            },
            "$setOnInsert": {"created_at": now},
        },
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )
    result.pop("_id", None)
    return result


def log_query(student_id: str, raw_text: str, matched_book_ids: list) -> str:
    """Persist a student query and return the inserted document ID."""
    db = get_db()
    doc = make_query(student_id, raw_text, matched_book_ids)
    result = db.queries.insert_one(doc)
    return str(result.inserted_id)


# ---------------------------------------------------------------------------
# Book reviews
# ---------------------------------------------------------------------------

def add_review(student_id: str, book_id: str, review_text: str,
               sentiment_label: str, sentiment_score: float) -> dict:
    """Insert a review and return the stored doc (with stringified _id)."""
    db = get_db()
    try:
        obj_id = ObjectId(book_id)
    except Exception:
        return {"error": "Invalid book ID"}
    doc = {
        "student_id": student_id,
        "book_id": obj_id,
        "book_id_str": book_id,
        "review_text": review_text,
        "sentiment_label": sentiment_label,
        "sentiment_score": sentiment_score,
        "created_at": datetime.utcnow(),
    }
    result = db.reviews.insert_one(doc)
    doc["_id"] = str(result.inserted_id)
    doc["book_id"] = book_id
    return doc


def get_reviews(book_id: str) -> list[dict]:
    """Return all reviews for a book, newest first."""
    db = get_db()
    try:
        obj_id = ObjectId(book_id)
    except Exception:
        return []
    cursor = db.reviews.find({"book_id": obj_id}).sort("created_at", -1)
    results = []
    for doc in cursor:
        doc["_id"] = str(doc["_id"])
        doc["book_id"] = book_id
        results.append(doc)
    return results


# ---------------------------------------------------------------------------
# User profile / reading history
# ---------------------------------------------------------------------------

def get_reading_history(student_id: str, limit: int = 20) -> list[dict]:
    """
    Return titles the student has reserved (active + completed), used as
    reading history for the WatsonX recommendation engine.
    """
    db = get_db()
    cursor = db.reservations.find(
        {"student_id": student_id, "status": {"$in": ["active", "returned"]}},
    ).sort("created_at", -1).limit(limit)

    book_ids = []
    for r in cursor:
        bid = r.get("book_id")
        if bid and bid not in book_ids:
            book_ids.append(bid)

    books = []
    for bid in book_ids:
        b = db.books.find_one({"_id": bid}, {"title": 1, "author": 1, "subject_tags": 1})
        if b:
            b["_id"] = str(b["_id"])
            books.append(b)
    return books


# ---------------------------------------------------------------------------
# High-demand prioritisation helper (used by automation layer)
# ---------------------------------------------------------------------------

def get_high_demand_books(threshold: int = 5, limit: int = 20) -> list[dict]:
    """Return books whose demand_score exceeds *threshold*, sorted desc."""
    db = get_db()
    cursor = (
        db.books.find({"demand_score": {"$gte": threshold}})
        .sort("demand_score", -1)
        .limit(limit)
    )
    results = []
    for doc in cursor:
        doc["_id"] = str(doc["_id"])
        results.append(doc)
    return results


def get_all_books(skip: int = 0, limit: int = 50, subject: str | None = None) -> list[dict]:
    """
    Return all books from the catalogue, optionally filtered by subject tag.
    Sorted by title ascending.
    """
    db = get_db()
    query: dict = {}
    if subject and subject.lower() != "all":
        query["subject_tags"] = {"$regex": subject, "$options": "i"}
    cursor = db.books.find(query).sort("title", 1).skip(skip).limit(limit)
    results = []
    for doc in cursor:
        doc["_id"] = str(doc["_id"])
        results.append(doc)
    return results


def reset_book_availability() -> int:
    """
    Reset available_copies = total_copies for every book.
    Returns the number of documents modified.
    Called from /api/admin/reset-books and seed_db.py --reset.
    """
    db = get_db()
    result = db.books.update_many(
        {},
        [{"$set": {"available_copies": "$total_copies"}}],
    )
    return result.modified_count
