# database.py - Professional Database Layer for Campus Lost & Found
# ONLY this file talks to SQLite. app.py NEVER does DB work directly.
# Used by: app.py, charts.py (via DataFrame)
# Functions app.py needs: init_db, save_report, get_all_reports, search_reports, update_status

import sqlite3
import os
import pandas as pd
from datetime import datetime

# --- Config ---
DB_PATH = os.path.join(os.path.dirname(__file__), "lost_found.db")

# Exact columns app.py + charts.py expect - DO NOT RENAME
COLUMNS = [
    "report_id",      # e.g. LF-001 - Primary Key
    "reporter_name",  # e.g. Ahmad Ali
    "roll_no",        # e.g. CS-2023-045
    "item_name",      # e.g. Black Wallet
    "category",       # Wallet, Phone, ID Card, Keys, Bag, Laptop, Book, Other
    "type",           # Lost or Found
    "location",       # e.g. Library, Canteen
    "date",           # YYYY-MM-DD
    "description",    # Color, Brand, etc.
    "contact",        # Phone / WhatsApp
    "status",         # Open or Claimed
    "created_at",     # Auto timestamp
]

def _get_connection():
    """Create connection. check_same_thread=False is required for Streamlit."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """
    Called once at start of app.py: init_db()
    Creates table if not exists. Safe to call every run.
    """
    conn = _get_connection()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                report_id TEXT PRIMARY KEY,
                reporter_name TEXT NOT NULL,
                roll_no TEXT NOT NULL,
                item_name TEXT NOT NULL,
                category TEXT NOT NULL DEFAULT 'Other',
                type TEXT NOT NULL CHECK(type IN ('Lost', 'Found')),
                location TEXT NOT NULL,
                date TEXT NOT NULL,
                description TEXT DEFAULT '',
                contact TEXT DEFAULT '',
                status TEXT NOT NULL DEFAULT 'Open' CHECK(status IN ('Open', 'Claimed')),
                created_at TEXT NOT NULL
            )
        """)
        # Indexes for fast search - professional touch
        conn.execute("CREATE INDEX IF NOT EXISTS idx_item_name ON reports(item_name)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_location ON reports(location)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_category ON reports(category)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_type ON reports(type)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_status ON reports(status)")
        conn.commit()
    finally:
        conn.close()

def save_report(report_id, reporter_name, roll_no, item_name, category, type,
                location, date, description="", contact="", status="Open"):
    """
    Called by app.py when user submits Lost / Found form.
    Returns True if saved, False if duplicate ID or error.
    """
    # Safety: ensure table exists
    init_db()
    conn = _get_connection()
    try:
        # Clean data - professional validation
        report_id = str(report_id).strip().upper()
        reporter_name = str(reporter_name).strip()
        roll_no = str(roll_no).strip().upper()
        item_name = str(item_name).strip()
        category = str(category).strip() if category else "Other"
        type = str(type).strip().capitalize()
        location = str(location).strip()
        date = str(date).strip()
        description = str(description).strip() if description else ""
        contact = str(contact).strip() if contact else ""
        status = str(status).strip().capitalize() if status else "Open"

        # Validate type/status
        if type not in ("Lost", "Found"):
            type = "Lost"
        if status not in ("Open", "Claimed"):
            status = "Open"

        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn.execute("""
            INSERT INTO reports
            (report_id, reporter_name, roll_no, item_name, category, type, location, date, description, contact, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (report_id, reporter_name, roll_no, item_name, category, type, location, date, description, contact, status, created_at))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # Duplicate report_id - app.py generates new one next time
        print(f"[DB] Duplicate Report ID: {report_id}")
        return False
    except Exception as e:
        print(f"[DB] Save Error: {e}")
        return False
    finally:
        conn.close()

def get_all_reports():
    """
    Called by app.py Dashboard + Search page: df = get_all_reports()
    Returns: pandas DataFrame with COLUMNS, sorted by newest first.
    Returns empty DataFrame if no data - so charts.py never crashes.
    """
    init_db()
    conn = _get_connection()
    try:
        query = "SELECT * FROM reports ORDER BY created_at DESC, report_id DESC"
        df = pd.read_sql_query(query, conn)
        # Guarantee all columns exist even if DB is old
        for col in COLUMNS:
            if col not in df.columns:
                df[col] = ""
        # Keep column order same as app.py expects
        df = df[COLUMNS]
        return df
    except Exception as e:
        print(f"[DB] Get All Error: {e}")
        return pd.DataFrame(columns=COLUMNS)
    finally:
        conn.close()

def search_reports(keyword):
    """
    Called by app.py Search page: search_reports(keyword)
    Searches in item_name, location, category, description, report_id
    Case-insensitive, safe from SQL injection (uses ? placeholders)
    """
    init_db()
    if not keyword or not str(keyword).strip():
        return get_all_reports()

    keyword = f"%{str(keyword).strip()}%"
    conn = _get_connection()
    try:
        query = """
            SELECT * FROM reports
            WHERE item_name LIKE ? COLLATE NOCASE
               OR location LIKE ? COLLATE NOCASE
               OR category LIKE ? COLLATE NOCASE
               OR description LIKE ? COLLATE NOCASE
               OR report_id LIKE ? COLLATE NOCASE
               OR reporter_name LIKE ? COLLATE NOCASE
            ORDER BY created_at DESC
        """
        df = pd.read_sql_query(query, conn, params=(keyword, keyword, keyword, keyword, keyword, keyword))
        for col in COLUMNS:
            if col not in df.columns:
                df[col] = ""
        df = df[COLUMNS]
        return df
    except Exception as e:
        print(f"[DB] Search Error: {e}")
        return pd.DataFrame(columns=COLUMNS)
    finally:
        conn.close()

def update_status(report_id, new_status):
    """
    Called by app.py Claim button: update_status("LF-001", "Claimed")
    Returns True if found and updated, False if not found.
    """
    init_db()
    conn = _get_connection()
    try:
        report_id = str(report_id).strip().upper()
        new_status = str(new_status).strip().capitalize()
        if new_status not in ("Open", "Claimed"):
            new_status = "Claimed"

        cursor = conn.execute(
            "UPDATE reports SET status = ? WHERE report_id = ?",
            (new_status, report_id)
        )
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"[DB] Update Error: {e}")
        return False
    finally:
        conn.close()

# --- Extra Professional Helpers (not required, but useful) ---

def get_report_by_id(report_id):
    """Get single report by ID. Returns dict or None."""
    init_db()
    conn = _get_connection()
    try:
        cur = conn.execute("SELECT * FROM reports WHERE report_id = ?", (str(report_id).strip().upper(),))
        row = cur.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

def get_stats():
    """Returns dict for dashboard if you ever need it."""
    df = get_all_reports()
    if len(df) == 0:
        return {"total": 0, "lost": 0, "found": 0, "claimed": 0, "open": 0}
    return {
        "total": len(df),
        "lost": len(df[df["type"] == "Lost"]),
        "found": len(df[df["type"] == "Found"]),
        "claimed": len(df[df["status"] == "Claimed"]),
        "open": len(df[df["status"] == "Open"]),
    }

def delete_report(report_id):
    """Admin only - delete a report. Returns True if deleted."""
    init_db()
    conn = _get_connection()
    try:
        cur = conn.execute("DELETE FROM reports WHERE report_id = ?", (str(report_id).strip().upper(),))
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()
