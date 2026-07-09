"""
Library Management System (LMS) Integration Layer.

Provides functions to:
  - Search books by NLU-derived search terms
  - Check real-time availability
  - Reserve a book (or place on waitlist)
  - Cancel / complete a reservation
  - Record student queries for analytics

All persistence is via MongoDB (models.db).
"""

from datetime import datetime
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

def reserve_book(student_id: str, book_id: str) -> dict:
    """
    Reserve a book for a student.

    - If copies are available  → status = "active",  decrement available_copies
    - If no copies available   → status = "waitlisted"
    Returns the reservation document with an "ai_message" placeholder.
    """
    db = get_db()
    try:
        obj_id = ObjectId(book_id)
    except InvalidId:
        return {"error": "Invalid book ID"}

    # Atomically decrement if available
    book = db.books.find_one_and_update(
        {"_id": obj_id, "available_copies": {"$gt": 0}},
        {
            "$inc": {"available_copies": -1, "demand_score": 1},
            "$set": {"updated_at": datetime.utcnow()},
        },
        return_document=ReturnDocument.AFTER,
    )

    if book:
        status = "active"
    else:
        # No copies – still bump demand_score for prioritisation
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


# ---------------------------------------------------------------------------
# Query logging
# ---------------------------------------------------------------------------

def log_query(student_id: str, raw_text: str, matched_book_ids: list) -> str:
    """Persist a student query and return the inserted document ID."""
    db = get_db()
    doc = make_query(student_id, raw_text, matched_book_ids)
    result = db.queries.insert_one(doc)
    return str(result.inserted_id)


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
