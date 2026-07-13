"""
Library AI Agent – Flask application entry point.

Startup sequence:
  1. Load environment variables (.env via python-dotenv)
  2. Create Flask app and register blueprints
  3. Ensure MongoDB indexes
  4. (Optional) Start APScheduler for periodic Robo rule execution
  5. Serve the single-page frontend via a catch-all route
"""

import os
import logging
import json
from flask import Flask, send_from_directory, render_template
from dotenv import load_dotenv

load_dotenv()  # Read .env before anything else

from backend.routes.api import api
from backend.models.db  import ensure_indexes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s – %(message)s",
)
logger = logging.getLogger(__name__)


def create_app() -> Flask:
    app = Flask(
        __name__,
        static_folder="frontend/static",
        template_folder="frontend/templates",
    )

    # ── Register blueprints ──────────────────────────────────────────────────
    app.register_blueprint(api)

    # ── Database indexes ─────────────────────────────────────────────────────
    try:
        ensure_indexes()
    except Exception as exc:
        logger.warning("Could not ensure DB indexes: %s", exc)

    # ── Restore book availability on every startup ────────────────────────────
    # Resets available_copies = total_copies so books never appear permanently
    # "Unavailable" after testing or after a server restart.
    try:
        from backend.services.library_lms import reset_book_availability
        reset_count = reset_book_availability()
        if reset_count:
            logger.info("[startup] Reset available_copies for %d book(s).", reset_count)
    except Exception as exc:
        logger.warning("Could not reset book availability on startup: %s", exc)

    # ── Optional: APScheduler for periodic Robo rule runs ───────────────────
    if os.getenv("ENABLE_SCHEDULER", "false").lower() == "true":
        from apscheduler.schedulers.background import BackgroundScheduler
        from backend.automation.robo_rules import run_all_rules

        scheduler = BackgroundScheduler()
        interval_minutes = int(os.getenv("SCHEDULER_INTERVAL_MINUTES", "30"))
        scheduler.add_job(run_all_rules, "interval", minutes=interval_minutes)
        scheduler.start()
        logger.info("[Scheduler] Robo rules scheduled every %d minutes.", interval_minutes)

    # ── Serve frontend ───────────────────────────────────────────────────────
    templates_dir = os.path.join(app.root_path, "frontend", "templates")
    static_dir    = os.path.join(app.root_path, "frontend", "static")

    # Build a <script> that sets window.FIREBASE_CONFIG once from env
    _raw = os.getenv("FIREBASE_CONFIG", "")
    try:
        _cfg = json.loads(_raw) if _raw else {}
    except Exception:
        _cfg = {}
    _firebase_script = (
        f"<script>window.FIREBASE_CONFIG={json.dumps(_cfg)};</script>"
        if _cfg else ""
    )

    @app.route("/login")
    def serve_login():
        return render_template("login.html", firebase_config_script=_firebase_script)

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_frontend(path):
        if path and os.path.exists(os.path.join(static_dir, path)):
            return send_from_directory(static_dir, path)
        return render_template("index.html", firebase_config_script=_firebase_script)

    return app


if __name__ == "__main__":
    flask_app = create_app()
    port = int(os.getenv("PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    flask_app.run(host="0.0.0.0", port=port, debug=debug)
