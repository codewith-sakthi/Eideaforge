"""
app.py – Flask REST API application factory for Eideaforge.
"""
import os
import pymysql
from flask import Flask, g
from flask_cors import CORS

from config import Config
from routes import register_blueprints


def get_db() -> pymysql.connections.Connection:
    """Open a per-request DB connection stored on flask.g."""
    if "db" not in g:
        g.db = pymysql.connect(
            host=Config.MYSQL_HOST,
            port=Config.MYSQL_PORT,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB,
            cursorclass=pymysql.cursors.DictCursor,
            charset="utf8mb4",
            autocommit=False,
        )
    return g.db


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    # ── Upload directories ────────────────────────────────────────────────
    for folder in [
        Config.UPLOAD_FOLDER,
        Config.CREDENTIALS_FOLDER,
        os.path.join(os.path.dirname(__file__), "uploads", "documents"),
        os.path.join(os.path.dirname(__file__), "uploads", "abstracts"),
        os.path.join(os.path.dirname(__file__), "logs"),
    ]:
        os.makedirs(folder, exist_ok=True)

    # ── CORS ─────────────────────────────────────────────────────────────
    CORS(
        app,
        resources={r"/api/*": {"origins": Config.ALLOWED_ORIGINS}},
        supports_credentials=True,
    )

    # ── DB lifecycle ──────────────────────────────────────────────────────
    app.get_db = get_db  # expose for models

    @app.teardown_appcontext
    def close_db(exc=None):
        db = g.pop("db", None)
        if db is not None:
            if exc is None:
                try:
                    db.commit()
                except Exception:
                    db.rollback()
            else:
                db.rollback()
            db.close()

    # ── Blueprints ────────────────────────────────────────────────────────
    register_blueprints(app)

    # ── Error Handlers ───────────────────────────────────────────────────
    from flask import request, jsonify

    @app.errorhandler(400)
    def handle_400(e):
        if request.path.startswith("/api/"):
            return jsonify({"success": False, "error": getattr(e, "description", "Bad Request")}), 400
        return e

    @app.errorhandler(404)
    def handle_404(e):
        if request.path.startswith("/api/"):
            return jsonify({"success": False, "error": "API endpoint not found"}), 404
        return e

    @app.errorhandler(405)
    def handle_405(e):
        if request.path.startswith("/api/"):
            return jsonify({"success": False, "error": "Method Not Allowed"}), 405
        return e

    @app.errorhandler(pymysql.err.MySQLError)
    def handle_mysql_error(e):
        return jsonify({
            "success": False,
            "error": f"Database Error: {str(e)}. Please ensure MySQL is running and credentials in backend/.env are configured correctly."
        }), 500

    @app.errorhandler(Exception)
    def handle_generic_exception(e):
        if request.path.startswith("/api/"):
            return jsonify({
                "success": False,
                "error": f"Internal Server Error: {str(e)}"
            }), 500
        raise e

    # ── Health check ──────────────────────────────────────────────────────
    @app.get("/api/health")
    def health():
        return {"status": "ok", "service": "Eideaforge API"}

    # ── Frontend & Static Serving ─────────────────────────────────────────
    frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
    uploads_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "uploads"))

    from flask import send_from_directory

    @app.route("/uploads/<path:filename>")
    def serve_upload(filename):
        return send_from_directory(uploads_dir, filename)

    @app.route("/", defaults={"path": "index.html"})
    @app.route("/<path:path>")
    def serve_frontend(path):
        if path.startswith("api/"):
            return {"error": "API endpoint not found", "success": False}, 404
        
        file_path = os.path.join(frontend_dir, path)
        if os.path.isfile(file_path):
            return send_from_directory(frontend_dir, path)
        elif os.path.isfile(os.path.join(file_path, "index.html")):
            return send_from_directory(file_path, "index.html")
        else:
            return send_from_directory(frontend_dir, "index.html")

    return app


if __name__ == "__main__":
    application = create_app()
    application.run(
        host="0.0.0.0",
        port=Config.PORT,
        debug=Config.DEBUG,
    )

