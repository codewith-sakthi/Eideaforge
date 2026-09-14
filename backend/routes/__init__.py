"""
routes/__init__.py – Blueprint registration entry point.
"""
from flask import Flask


def register_blueprints(app: Flask) -> None:
    """Register all API route blueprints with proper URL prefixes."""
    from routes.auth_routes import auth_bp
    from routes.public_routes import public_bp
    from routes.student_routes import student_bp
    from routes.admin_routes import admin_bp
    from routes.evaluator_routes import evaluator_bp
    from routes.idea_routes import idea_bp
    from routes.team_routes import team_bp
    from routes.competition_routes import competition_bp
    from routes.submission_routes import submission_bp
    from routes.evaluation_routes import evaluation_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(public_bp, url_prefix="/api/public")
    app.register_blueprint(student_bp, url_prefix="/api/student")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(evaluator_bp, url_prefix="/api/evaluator")
    app.register_blueprint(idea_bp, url_prefix="/api/ideas")
    app.register_blueprint(team_bp, url_prefix="/api/teams")
    app.register_blueprint(competition_bp, url_prefix="/api/competitions")
    app.register_blueprint(submission_bp, url_prefix="/api/submissions")
    app.register_blueprint(evaluation_bp, url_prefix="/api/evaluations")
