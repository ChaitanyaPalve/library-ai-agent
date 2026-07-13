"""
MongoDB connection and collection models for the Library AI Agent.
Collections: books, students, queries, reservations
"""

import os
import logging
from datetime import datetime, timedelta

import certifi
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

MONGO_URI = os.environ["MONGO_URI"]  # Required — set in .env or deployment env vars


def get_client() -> MongoClient:
    """
    Return a connected MongoClient pointed at MongoDB Atlas.
    Uses certifi CA bundle — required on Windows/Python 3.12 where the system
    CA bundle may not include the Atlas root cert.
    """
    client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=10_000,
        connectTimeoutMS=10_000,
        socketTimeoutMS=30_000,
        tls=True,
        tlsCAFile=certifi.where(),   # explicit CA bundle — fixes SSL handshake on Python 3.12
    )
    try:
        client.admin.command("ping")
    except (ConnectionFailure, ServerSelectionTimeoutError) as exc:
        client.close()
        raise ConnectionFailure(
            f"Cannot reach MongoDB Atlas. "
            f"Check credentials, IP-whitelist (Atlas -> Network Access -> Add 0.0.0.0/0), "
            f"and network. Original error: {exc}"
        ) from exc
    return client


_client: MongoClient | None = None


def get_db():
    """Return the *library* database, reusing a module-level singleton client."""
    global _client
    if _client is None:
        _client = get_client()
    return _client["library"]


# ---------------------------------------------------------------------------
# Index bootstrapping
# ---------------------------------------------------------------------------

def ensure_indexes():
    db = get_db()
    # Books
    db.books.create_index([("title", ASCENDING)])
    db.books.create_index([("isbn", ASCENDING)], unique=True)
    db.books.create_index([("subject_tags", ASCENDING)])
    db.books.create_index([("demand_score", DESCENDING)])
    # Queries
    db.queries.create_index([("student_id", ASCENDING)])
    db.queries.create_index([("created_at", DESCENDING)])
    # Reservations
    db.reservations.create_index([("book_id", ASCENDING)])
    db.reservations.create_index([("student_id", ASCENDING)])
    # Students
    db.students.create_index([("student_id", ASCENDING)], unique=True)
    db.students.create_index([("firebase_uid", ASCENDING)])
    # Reviews
    db.reviews.create_index([("book_id", ASCENDING)])
    db.reviews.create_index([("student_id", ASCENDING)])
    db.reviews.create_index([("created_at", DESCENDING)])
    logging.getLogger(__name__).info("[db] Indexes ensured.")


# ---------------------------------------------------------------------------
# Helper factories – keep field contracts in one place
# ---------------------------------------------------------------------------

def make_book(title: str, author: str, isbn: str, subject_tags: list[str],
              total_copies: int = 1, description: str = "") -> dict:
    return {
        "title": title,
        "author": author,
        "isbn": isbn,
        "subject_tags": subject_tags,
        "total_copies": total_copies,
        "available_copies": total_copies,
        "demand_score": 0,          # incremented on each reservation/search hit
        "description": description, # short blurb shown on the book card
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }


def make_query(student_id: str, raw_text: str, matched_book_ids: list) -> dict:
    return {
        "student_id": student_id,
        "raw_text": raw_text,
        "matched_book_ids": matched_book_ids,
        "created_at": datetime.utcnow(),
    }


def make_reservation(student_id: str, book_id, status: str = "active") -> dict:
    now = datetime.utcnow()
    doc = {
        "student_id": student_id,
        "book_id": book_id,
        "status": status,           # active | waitlisted | returned | cancelled
        "created_at": now,
        "updated_at": now,
    }
    # Only active reservations get an issued_at and due_date (7 days)
    if status == "active":
        doc["issued_at"] = now
        doc["due_date"]  = now + timedelta(days=7)
    return doc
