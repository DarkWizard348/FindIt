"""
database.py - Database operations and SQLite schema management for FindIt.
Uses parameterized queries to safeguard against SQL injection.
"""

import sqlite3
from flask import g, current_app

CATEGORIES = [
    "Electronics",
    "Books and Stationery",
    "Bags",
    "Water Bottles",
    "ID Cards",
    "Keys",
    "Clothing",
    "Other",
]

CAMPUS_LOCATIONS = [
    "Central Library",
    "Main Canteen / Cafeteria",
    "Science & Engineering Block",
    "Arts & Humanities Block",
    "Computer Labs",
    "Sports Complex & Gym",
    "Student Activity Center (SAC)",
    "Campus Ground & Parking",
    "Administrative Block",
    "Auditorium",
    "Other / Unspecified",
]

REPORT_TYPES = ["Lost", "Found"]
STATUSES = ["Lost", "Found", "Recovered"]


def get_db(db_path=None):
    """
    Returns an active SQLite database connection.
    If called within a Flask application context, the connection is cached on `g`.
    """
    if db_path is not None:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn

    if "db" not in g:
        path = current_app.config.get("DATABASE")
        g.db = sqlite3.connect(path)
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    """Closes the database connection at the end of the request."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(db_path=None):
    """
    Initializes the SQLite database tables and indices if they do not exist.
    """
    conn = get_db(db_path)
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT NOT NULL,
            category TEXT NOT NULL,
            report_type TEXT NOT NULL CHECK(report_type IN ('Lost', 'Found')),
            location TEXT NOT NULL,
            item_date TEXT NOT NULL,
            description TEXT NOT NULL,
            image_filename TEXT,
            status TEXT NOT NULL CHECK(status IN ('Lost', 'Found', 'Recovered')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )

    # Useful indices for fast filtering and sorting
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_items_status ON items(status);"
    )
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_items_category ON items(category);"
    )
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_items_created_at ON items(created_at DESC);"
    )

    conn.commit()
    if db_path is not None:
        conn.close()


def get_dashboard_counts(db_path=None):
    """
    Returns aggregated counts for lost, found, and recovered items.
    """
    conn = get_db(db_path)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            COUNT(CASE WHEN status = 'Lost' THEN 1 END) AS lost_count,
            COUNT(CASE WHEN status = 'Found' THEN 1 END) AS found_count,
            COUNT(CASE WHEN status = 'Recovered' THEN 1 END) AS recovered_count,
            COUNT(*) AS total_count
        FROM items;
        """
    )
    row = cursor.fetchone()

    stats = {
        "lost": row["lost_count"] if row else 0,
        "found": row["found_count"] if row else 0,
        "recovered": row["recovered_count"] if row else 0,
        "total": row["total_count"] if row else 0,
    }

    if db_path is not None:
        conn.close()
    return stats


def get_recent_reports(limit=6, db_path=None):
    """
    Fetches the most recent item reports ordered by newest first.
    """
    conn = get_db(db_path)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, item_name, category, report_type, location, item_date,
               description, image_filename, status, created_at
        FROM items
        ORDER BY created_at DESC, id DESC
        LIMIT ?;
        """,
        (limit,),
    )
    rows = cursor.fetchall()
    items = [dict(row) for row in rows]

    if db_path is not None:
        conn.close()
    return items


def insert_item(item_dict, db_path=None):
    """
    Inserts a new item report using parameterized SQL.
    Returns the newly generated item id.
    """
    conn = get_db(db_path)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO items (
            item_name, category, report_type, location, item_date,
            description, image_filename, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """,
        (
            item_dict["item_name"].strip(),
            item_dict["category"].strip(),
            item_dict["report_type"].strip(),
            item_dict["location"].strip(),
            item_dict["item_date"].strip(),
            item_dict["description"].strip(),
            item_dict.get("image_filename"),
            item_dict.get("status", item_dict["report_type"]),
        ),
    )
    conn.commit()
    item_id = cursor.lastrowid

    if db_path is not None:
        conn.close()
    return item_id


def get_item_by_id(item_id, db_path=None):
    """
    Retrieves a single item report by its primary key ID.
    Returns None if not found.
    """
    conn = get_db(db_path)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, item_name, category, report_type, location, item_date,
               description, image_filename, status, created_at
        FROM items
        WHERE id = ?;
        """,
        (item_id,),
    )
    row = cursor.fetchone()
    item = dict(row) if row else None

    if db_path is not None:
        conn.close()
    return item


def search_and_filter_items(
    query=None,
    report_type=None,
    category=None,
    location=None,
    status=None,
    db_path=None,
):
    """
    Searches items by partial, case-insensitive keyword across item_name and description,
    and applies optional filters for report_type, category, location, and status.
    Uses parameterized SQL to prevent SQL injection.
    """
    conn = get_db(db_path)
    cursor = conn.cursor()

    sql = """
        SELECT id, item_name, category, report_type, location, item_date,
               description, image_filename, status, created_at
        FROM items
        WHERE 1=1
    """
    params = []

    if query and query.strip():
        term = f"%{query.strip()}%"
        sql += " AND (item_name LIKE ? OR description LIKE ?)"
        params.extend([term, term])

    if report_type and report_type.strip():
        sql += " AND report_type = ?"
        params.append(report_type.strip())

    if category and category.strip():
        sql += " AND category = ?"
        params.append(category.strip())

    if location and location.strip():
        sql += " AND location = ?"
        params.append(location.strip())

    if status and status.strip():
        sql += " AND status = ?"
        params.append(status.strip())

    sql += " ORDER BY created_at DESC, id DESC;"

    cursor.execute(sql, params)
    rows = cursor.fetchall()
    items = [dict(row) for row in rows]

    if db_path is not None:
        conn.close()
    return items


def update_item_status(item_id, new_status, db_path=None):
    """
    Updates the status of an item (e.g. to 'Recovered').
    Validates against the allowed STATUSES list.
    Returns True if an item row was updated, False otherwise.
    """
    if new_status not in STATUSES:
        raise ValueError(f"Invalid status: {new_status}")

    conn = get_db(db_path)
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE items
        SET status = ?
        WHERE id = ?;
        """,
        (new_status, item_id),
    )
    conn.commit()
    updated = cursor.rowcount > 0

    if db_path is not None:
        conn.close()
    return updated
