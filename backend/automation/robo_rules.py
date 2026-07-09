"""
IBM Robo Automation Engine for the Library AI Agent.

IBM Robo is used to define and execute automation rules that drive
proactive library management behaviour:

  Rule 1 – HIGH_DEMAND_ALERT
    Trigger : A book's demand_score crosses a configurable threshold.
    Action  : Flag the book, notify library admin, suggest purchasing extra copies.

  Rule 2 – AUTO_WAITLIST_PROMOTE
    Trigger : A reserved copy is returned (available_copies incremented).
    Action  : Find the oldest waitlisted reservation for that book,
              promote it to "active", decrement available_copies.

  Rule 3 – RESERVATION_EXPIRY
    Trigger : An active reservation is older than MAX_HOLD_DAYS days.
    Action  : Cancel it and promote the next person on the waitlist.

  Rule 4 – LOW_STOCK_REORDER
    Trigger : available_copies == 0 and demand_score >= REORDER_THRESHOLD.
    Action  : Create a procurement alert document in the db.procurement_alerts collection.

All rules are idempotent and can be scheduled (e.g. via APScheduler or cron).
"""

import os
import logging
from datetime import datetime, timedelta
from bson import ObjectId
from pymongo import ReturnDocument

from backend.models.db import get_db

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

HIGH_DEMAND_THRESHOLD = int(os.getenv("ROBO_HIGH_DEMAND_THRESHOLD", "10"))
REORDER_THRESHOLD     = int(os.getenv("ROBO_REORDER_THRESHOLD", "15"))
MAX_HOLD_DAYS         = int(os.getenv("ROBO_MAX_HOLD_DAYS", "14"))


# ---------------------------------------------------------------------------
# Rule 1 – High-Demand Alert
# ---------------------------------------------------------------------------

def rule_high_demand_alert() -> list[dict]:
    """
    Scan books with demand_score >= HIGH_DEMAND_THRESHOLD.
    Upsert an alert document for each; return the list of alerts raised.
    """
    db = get_db()
    alerts = []
    for book in db.books.find({"demand_score": {"$gte": HIGH_DEMAND_THRESHOLD}}):
        alert = {
            "type": "HIGH_DEMAND",
            "book_id": str(book["_id"]),
            "title": book["title"],
            "demand_score": book["demand_score"],
            "available_copies": book["available_copies"],
            "recommendation": "Consider acquiring additional copies.",
            "raised_at": datetime.utcnow(),
        }
        db.automation_alerts.update_one(
            {"type": "HIGH_DEMAND", "book_id": str(book["_id"])},
            {"$set": alert},
            upsert=True,
        )
        alerts.append(alert)
        logger.info("[Robo] HIGH_DEMAND alert for '%s' (score=%d)", book["title"], book["demand_score"])
    return alerts


# ---------------------------------------------------------------------------
# Rule 2 – Waitlist Promotion (call after a book is returned)
# ---------------------------------------------------------------------------

def rule_promote_waitlist(book_id: str) -> dict | None:
    """
    Promote the oldest waitlisted reservation for *book_id* to "active".
    Decrements available_copies atomically.
    Returns the promoted reservation or None if no waitlist entry exists.
    """
    db = get_db()
    try:
        obj_id = ObjectId(book_id)
    except Exception:
        return None

    # Atomically grab an available copy
    book = db.books.find_one_and_update(
        {"_id": obj_id, "available_copies": {"$gt": 0}},
        {"$inc": {"available_copies": -1}, "$set": {"updated_at": datetime.utcnow()}},
        return_document=ReturnDocument.AFTER,
    )
    if not book:
        return None  # No copies or book not found

    # Find the oldest waitlisted reservation
    reservation = db.reservations.find_one_and_update(
        {"book_id": obj_id, "status": "waitlisted"},
        {"$set": {"status": "active", "updated_at": datetime.utcnow()}},
        sort=[("created_at", 1)],
        return_document=ReturnDocument.AFTER,
    )
    if reservation:
        reservation["_id"] = str(reservation["_id"])
        reservation["book_id"] = book_id
        logger.info("[Robo] Promoted reservation %s to active.", reservation["_id"])
    else:
        # Nobody on waitlist – return the copy
        db.books.update_one({"_id": obj_id}, {"$inc": {"available_copies": 1}})

    return reservation


# ---------------------------------------------------------------------------
# Rule 3 – Reservation Expiry
# ---------------------------------------------------------------------------

def rule_expire_reservations() -> list[str]:
    """
    Cancel active reservations older than MAX_HOLD_DAYS days.
    Returns a list of cancelled reservation IDs.
    """
    db = get_db()
    cutoff = datetime.utcnow() - timedelta(days=MAX_HOLD_DAYS)
    expired = db.reservations.find({"status": "active", "created_at": {"$lt": cutoff}})
    cancelled_ids = []

    for res in expired:
        # Return copy to pool
        db.books.update_one(
            {"_id": res["book_id"]},
            {"$inc": {"available_copies": 1}, "$set": {"updated_at": datetime.utcnow()}},
        )
        db.reservations.update_one(
            {"_id": res["_id"]},
            {"$set": {"status": "cancelled", "updated_at": datetime.utcnow()}},
        )
        cancelled_ids.append(str(res["_id"]))
        logger.info("[Robo] Expired reservation %s.", res["_id"])
        # Try to promote next on waitlist
        rule_promote_waitlist(str(res["book_id"]))

    return cancelled_ids


# ---------------------------------------------------------------------------
# Rule 4 – Low-Stock Reorder Alert
# ---------------------------------------------------------------------------

def rule_low_stock_reorder() -> list[dict]:
    """
    Create procurement alert for books with 0 available copies and high demand.
    """
    db = get_db()
    alerts = []
    for book in db.books.find({"available_copies": 0, "demand_score": {"$gte": REORDER_THRESHOLD}}):
        alert = {
            "type": "LOW_STOCK_REORDER",
            "book_id": str(book["_id"]),
            "title": book["title"],
            "demand_score": book["demand_score"],
            "raised_at": datetime.utcnow(),
        }
        db.automation_alerts.update_one(
            {"type": "LOW_STOCK_REORDER", "book_id": str(book["_id"])},
            {"$set": alert},
            upsert=True,
        )
        alerts.append(alert)
        logger.info("[Robo] LOW_STOCK_REORDER alert for '%s'.", book["title"])
    return alerts


# ---------------------------------------------------------------------------
# Run all rules (entry point for scheduler)
# ---------------------------------------------------------------------------

def run_all_rules() -> dict:
    """Execute every automation rule and return a combined report."""
    return {
        "high_demand_alerts":    rule_high_demand_alert(),
        "expired_reservations":  rule_expire_reservations(),
        "low_stock_reorders":    rule_low_stock_reorder(),
        "ran_at":                datetime.utcnow().isoformat(),
    }
