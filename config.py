"""
=========================================================
Lab Auto Grader
Configuration
=========================================================
"""

import os
from pathlib import Path

# ==========================================================
# BASE DIRECTORY
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent


# ==========================================================
# CONFIGURATION
# ==========================================================

class Config:
    """
    Base configuration.
    """

    # ------------------------------------------------------
    # Flask
    # ------------------------------------------------------

    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "change-this-secret-key"
    )

    DEBUG = False

    TESTING = False

    HOST = "0.0.0.0"

    PORT = 5000

    # ------------------------------------------------------
    # Database
    # ------------------------------------------------------

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{BASE_DIR / 'lab_autograder.db'}"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True
    }

    # ------------------------------------------------------
    # Uploads
    # ------------------------------------------------------

    UPLOAD_FOLDER = str(
        BASE_DIR / "uploads"
    )

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB

    # ------------------------------------------------------
    # Sessions
    # ------------------------------------------------------

    SESSION_COOKIE_HTTPONLY = True

    SESSION_COOKIE_SAMESITE = "Lax"

    SESSION_COOKIE_SECURE = False

    PERMANENT_SESSION_LIFETIME = 60 * 60 * 24

    # ------------------------------------------------------
    # Compiler
    # ------------------------------------------------------

    DEFAULT_LANGUAGE = "Python"

    COMPILE_TIMEOUT = 30

    EXECUTION_TIMEOUT = 5

    MEMORY_LIMIT_MB = 256

    # ------------------------------------------------------
    # Docker
    # ------------------------------------------------------

    DOCKER_IMAGE_PYTHON = "python:3.11"

    DOCKER_IMAGE_CPP = "gcc:13"

    DOCKER_IMAGE_C = "gcc:13"

    DOCKER_IMAGE_JAVA = "openjdk:21"

    DOCKER_IMAGE_NODE = "node:20"

    DOCKER_NETWORK_DISABLED = True

    # ------------------------------------------------------
    # Judge
    # ------------------------------------------------------

    MAX_TEST_CASES = 100

    MAX_SOURCE_SIZE = 2 * 1024 * 1024

    MAX_OUTPUT_SIZE = 1024 * 1024

    # ------------------------------------------------------
    # Pagination
    # ------------------------------------------------------

    PROBLEMS_PER_PAGE = 20

    SUBMISSIONS_PER_PAGE = 20

    STUDENTS_PER_PAGE = 20

    # ------------------------------------------------------
    # Logging
    # ------------------------------------------------------

    LOG_LEVEL = "INFO"

    LOG_FILE = str(
        BASE_DIR / "logs" / "app.log"
    )


# ==========================================================
# DEVELOPMENT
# ==========================================================

class DevelopmentConfig(Config):

    DEBUG = True


# ==========================================================
# TESTING
# ==========================================================

class TestingConfig(Config):

    TESTING = True

    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


# ==========================================================
# PRODUCTION
# ==========================================================

class ProductionConfig(Config):

    DEBUG = False

    SESSION_COOKIE_SECURE = True


# ==========================================================
# CONFIG MAP
# ==========================================================

config = {

    "development": DevelopmentConfig,

    "testing": TestingConfig,

    "production": ProductionConfig,

    "default": DevelopmentConfig

}