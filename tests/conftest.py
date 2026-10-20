"""
conftest.py - Pytest fixtures providing isolated test database and client.
"""

import os
import tempfile
import pytest
from app import create_app
from database import init_db


@pytest.fixture
def app():
    """
    Creates and configures an isolated Flask test application instance.
    Uses an independent temporary SQLite database and upload folder for each test run.
    """
    db_fd, db_path = tempfile.mkstemp(suffix=".sqlite")
    upload_dir = tempfile.mkdtemp()

    test_app = create_app({
        "TESTING": True,
        "DATABASE": db_path,
        "UPLOAD_FOLDER": upload_dir,
        "WTF_CSRF_ENABLED": False,
        "SECRET_KEY": "test-secret-key-findit",
    })

    with test_app.app_context():
        init_db(db_path)

    yield test_app

    # Teardown: close and remove temporary files and directory
    os.close(db_fd)
    if os.path.exists(db_path):
        os.remove(db_path)
    if os.path.exists(upload_dir):
        for root, dirs, files in os.walk(upload_dir, topdown=False):
            for f in files:
                os.remove(os.path.join(root, f))
            for d in dirs:
                os.rmdir(os.path.join(root, d))
        os.rmdir(upload_dir)


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()
