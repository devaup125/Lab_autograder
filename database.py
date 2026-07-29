"""
=========================================================
Lab Auto Grader
Database Manager
=========================================================
"""

import os
from datetime import datetime

from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

# ==========================================================
# DATABASE OBJECT
# ==========================================================

db = SQLAlchemy()

# ==========================================================
# INITIALIZATION
# ==========================================================

def init_db(app):
    """
    Initialize SQLAlchemy.
    """
    db.init_app(app)


# ==========================================================
# CREATE DATABASE
# ==========================================================

def create_database(app):

    with app.app_context():

        db.create_all()

        return True


# ==========================================================
# DROP DATABASE
# ==========================================================

def drop_database(app):

    with app.app_context():

        db.drop_all()

        return True


# ==========================================================
# RESET DATABASE
# ==========================================================

def reset_database(app):

    with app.app_context():

        db.drop_all()

        db.create_all()

        return True


# ==========================================================
# COMMIT
# ==========================================================

def commit():

    try:

        db.session.commit()

        return True

    except Exception:

        db.session.rollback()

        raise


# ==========================================================
# ROLLBACK
# ==========================================================

def rollback():

    db.session.rollback()


# ==========================================================
# CLOSE SESSION
# ==========================================================

def close():

    db.session.remove()


# ==========================================================
# EXECUTE RAW SQL
# ==========================================================

def execute(sql, params=None):

    if params is None:

        params = {}

    return db.session.execute(

        text(sql),

        params

    )


# ==========================================================
# DATABASE HEALTH
# ==========================================================

def health():

    try:

        execute("SELECT 1")

        return {

            "status": "Healthy",

            "database": True

        }

    except Exception as e:

        return {

            "status": "Failed",

            "database": False,

            "error": str(e)

        }


# ==========================================================
# TABLE INFORMATION
# ==========================================================

def tables():

    inspector = db.inspect(

        db.engine

    )

    return inspector.get_table_names()


# ==========================================================
# DATABASE INFORMATION
# ==========================================================

def database_information():

    return {

        "uri":

            current_app.config.get(

                "SQLALCHEMY_DATABASE_URI"

            ),

        "tables":

            tables(),

        "time":

            datetime.utcnow().isoformat()

    }


# ==========================================================
# BACKUP (SQLite)
# ==========================================================

def backup(destination):

    uri = current_app.config.get(

        "SQLALCHEMY_DATABASE_URI"

    )

    if not uri.startswith("sqlite:///"):

        raise RuntimeError(

            "Backup supported only for SQLite."

        )

    source = uri.replace(

        "sqlite:///",

        ""

    )

    import shutil

    shutil.copy2(

        source,

        destination

    )

    return destination


# ==========================================================
# RESTORE (SQLite)
# ==========================================================

def restore(source):

    uri = current_app.config.get(

        "SQLALCHEMY_DATABASE_URI"

    )

    if not uri.startswith("sqlite:///"):

        raise RuntimeError(

            "Restore supported only for SQLite."

        )

    target = uri.replace(

        "sqlite:///",

        ""

    )

    import shutil

    shutil.copy2(

        source,

        target

    )

    return True


# ==========================================================
# PUBLIC EXPORTS
# ==========================================================

__all__ = [

    "db",

    "init_db",

    "create_database",

    "drop_database",

    "reset_database",

    "commit",

    "rollback",

    "close",

    "execute",

    "health",

    "tables",

    "database_information",

    "backup",

    "restore"

]