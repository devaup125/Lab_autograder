"""
=========================================================
Lab Auto Grader
Application Entry Point
=========================================================
"""

import os

from flask import Flask
from flask_migrate import Migrate
from flask_login import LoginManager

from config import Config
from extensions import db

# ==========================================================
# ROUTES
# ==========================================================

from routes.auth import auth_bp
from routes.student import student_bp
from routes.teacher import teacher_bp
from routes.admin import admin_bp

# ==========================================================
# LOGIN MANAGER
# ==========================================================

login_manager = LoginManager()

login_manager.login_view = "auth.login"

login_manager.login_message = "Please login first."

login_manager.login_message_category = "warning"

# ==========================================================
# MIGRATE
# ==========================================================

migrate = Migrate()

# ==========================================================
# APPLICATION FACTORY
# ==========================================================

def create_app():

    app = Flask(__name__)

    app.config.from_object(Config)

    # ------------------------------------------------------
    # Secret Key
    # ------------------------------------------------------

    app.secret_key = Config.SECRET_KEY

    # ------------------------------------------------------
    # Initialize Extensions
    # ------------------------------------------------------

    db.init_app(app)

    migrate.init_app(

        app,

        db

    )

    login_manager.init_app(

        app

    )

    # ------------------------------------------------------
    # Upload Folder
    # ------------------------------------------------------

    os.makedirs(

        app.config.get(

            "UPLOAD_FOLDER",

            "uploads"

        ),

        exist_ok=True

    )

    return app
# ==========================================================
# REGISTER BLUEPRINTS
# ==========================================================

def register_blueprints(app):

    app.register_blueprint(

        auth_bp

    )

    app.register_blueprint(

        student_bp

    )

    app.register_blueprint(

        teacher_bp

    )

    app.register_blueprint(

        admin_bp

    )


# ==========================================================
# LOGIN MANAGER
# ==========================================================

from models.user import User


@login_manager.user_loader
def load_user(user_id):

    return User.query.get(

        int(user_id)

    )


# ==========================================================
# JINJA FILTERS
# ==========================================================

def register_filters(app):

    @app.template_filter("datetime")

    def datetime_filter(value):

        if value is None:

            return ""

        return value.strftime(

            "%d %b %Y %I:%M %p"

        )

    @app.template_filter("yesno")

    def yesno(value):

        return "Yes" if value else "No"


# ==========================================================
# CONTEXT PROCESSORS
# ==========================================================

def register_context_processors(app):

    @app.context_processor
    def inject_globals():

        return {

            "APP_NAME":

                "Lab Auto Grader",

            "APP_VERSION":

                "1.0.0"

        }


# ==========================================================
# BEFORE REQUEST
# ==========================================================

def register_before_request(app):

    from flask import session

    @app.before_request
    def update_last_activity():

        session["last_activity"] = True


# ==========================================================
# AFTER REQUEST
# ==========================================================

def register_after_request(app):

    @app.after_request
    def add_headers(response):

        response.headers[

            "X-App-Name"

        ] = "Lab Auto Grader"

        response.headers[

            "X-Frame-Options"

        ] = "SAMEORIGIN"

        response.headers[

            "X-Content-Type-Options"

        ] = "nosniff"

        return response


# ==========================================================
# DATABASE INITIALIZATION
# ==========================================================

def initialize_database(app):

    with app.app_context():

        db.create_all()


# ==========================================================
# CONFIGURE APPLICATION
# ==========================================================

def configure_application(app):

    register_blueprints(app)

    register_filters(app)

    register_context_processors(app)

    register_before_request(app)

    register_after_request(app)

    initialize_database(app)

    return app


# ==========================================================
# UPDATE create_app()
# ==========================================================

# Replace the last line of create_app():

# return app

# with:

    configure_application(app)

    return app
# ==========================================================
# ERROR HANDLERS
# ==========================================================

def register_error_handlers(app):

    from flask import render_template

    @app.errorhandler(400)
    def bad_request(error):

        return render_template(

            "errors/400.html"

        ), 400

    @app.errorhandler(401)
    def unauthorized(error):

        return render_template(

            "errors/401.html"

        ), 401

    @app.errorhandler(403)
    def forbidden(error):

        return render_template(

            "errors/403.html"

        ), 403

    @app.errorhandler(404)
    def page_not_found(error):

        return render_template(

            "errors/404.html"

        ), 404

    @app.errorhandler(500)
    def internal_server_error(error):

        db.session.rollback()

        return render_template(

            "errors/500.html"

        ), 500


# ==========================================================
# HOME PAGE
# ==========================================================

def register_routes(app):

    from flask import redirect
    from flask import url_for
    from flask import jsonify

    @app.route("/")
    def index():

        return redirect(

            url_for(

                "auth.login"

            )

        )

    @app.route("/health")
    def health():

        return jsonify({

            "status": "OK",

            "application": "Lab Auto Grader",

            "version": "1.0.0"

        })

    @app.route("/version")
    def version():

        return jsonify({

            "application":

                "Lab Auto Grader",

            "version":

                "1.0.0"

        })


# ==========================================================
# SHELL CONTEXT
# ==========================================================

def register_shell_context(app):

    from models.user import User
    from models.problem import Problem
    from models.submission import Submission
    from models.assignment import Assignment
    from models.testcase import TestCase

    @app.shell_context_processor
    def shell_context():

        return {

            "db": db,

            "User": User,

            "Problem": Problem,

            "Submission": Submission,

            "Assignment": Assignment,

            "TestCase": TestCase

        }


# ==========================================================
# CLI COMMANDS
# ==========================================================

def register_cli(app):

    import click

    @app.cli.command("init-db")
    def init_db():

        db.create_all()

        click.echo(

            "Database initialized."

        )

    @app.cli.command("drop-db")
    def drop_db():

        db.drop_all()

        click.echo(

            "Database dropped."

        )

    @app.cli.command("reset-db")
    def reset_db():

        db.drop_all()

        db.create_all()

        click.echo(

            "Database reset successfully."

        )


# ==========================================================
# DEBUG ROUTES
# ==========================================================

def register_debug_routes(app):

    @app.route("/debug/config")
    def debug_config():

        return {

            "debug":

                app.debug,

            "testing":

                app.testing,

            "database":

                app.config.get(

                    "SQLALCHEMY_DATABASE_URI"

                ),

            "upload_folder":

                app.config.get(

                    "UPLOAD_FOLDER"

                )

        }


# ==========================================================
# UPDATE CONFIGURE APPLICATION
# ==========================================================

# Add these inside configure_application(app):

# register_error_handlers(app)
# register_routes(app)
# register_shell_context(app)
# register_cli(app)
# register_debug_routes(app)
# ==========================================================
# LOGGING
# ==========================================================

import logging


def configure_logging(app):
    """
    Configure application logging.
    """

    logging.basicConfig(

        level=logging.INFO,

        format="%(asctime)s | %(levelname)s | %(message)s"

    )

    app.logger.info(

        "Lab Auto Grader started."

    )


# ==========================================================
# APPLICATION STARTUP
# ==========================================================

app = create_app()

configure_logging(app)


# ==========================================================
# MAIN
# ==========================================================

def main():
    """
    Application entry point.
    """

    debug = app.config.get(

        "DEBUG",

        False

    )

    host = app.config.get(

        "HOST",

        "0.0.0.0"

    )

    port = app.config.get(

        "PORT",

        5000

    )

    app.run(

        host=host,

        port=port,

        debug=debug

    )


# ==========================================================
# PUBLIC EXPORTS
# ==========================================================

__all__ = [

    "app",

    "db",

    "create_app",

    "configure_application",

    "configure_logging",

    "register_blueprints",

    "register_filters",

    "register_context_processors",

    "register_before_request",

    "register_after_request",

    "register_error_handlers",

    "register_routes",

    "register_shell_context",

    "register_cli",

    "register_debug_routes",

    "initialize_database",

    "login_manager",

    "migrate",

    "main"

]


# ==========================================================
# ENTRY POINT
# ==========================================================

if __name__ == "__main__":

    main()