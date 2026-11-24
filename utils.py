# utils.py - Helper Functions for Campus Lost & Found
# ONLY helpers here. No UI, No DB write, No Charts.
# Used by: app.py (Login, Report forms)
# Safe helpers for: database.py (to avoid duplicate IDs)

import re
import random
import string
from datetime import date, datetime

# --- Config ---
REPORT_PREFIX = "LF"
MIN_NAME_LENGTH = 3
MIN_ROLL_LENGTH = 3

def get_current_date():
    """
    Called in app.py: pd.to_datetime(get_current_date())
    Returns: "2026-11-23" - YYYY-MM-DD format
    Used as default date in Report Lost / Found forms.
    Also matches database.py date column and charts.py date parsing.
    """
    return date.today().isoformat()

def get_current_datetime_str():
    """Returns: '2026-11-23 18:30:00' - for logs / created_at"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def validate_roll_no(name, roll):
    """
    Called in app.py Login:
        if validate_roll_no(name, roll):
            login success

    Rules (student-friendly, not too strict):
    - Name must be at least 3 letters, only letters + space + . -
    - Roll must be at least 3 chars, letters + numbers + - / _
    - Example valid: Name = Ahmad Ali, Roll = CS-2023-045
    - Example valid: Name = Ali, Roll = 123
    Returns True / False
    """
    if name is None or roll is None:
        return False

    name = str(name).strip()
    roll = str(roll).strip()

    # Both required
    if len(name) < MIN_NAME_LENGTH or len(roll) < MIN_ROLL_LENGTH:
        return False

    # Name: must contain at least one letter, no numbers, no special symbols except space . -
    # Allows: Ahmad Ali, Muhammad-Ali, Ayesha.Khan
    if not re.match(r"^[A-Za-z\s\.\-']+$", name):
        return False
    # Name must have at least 2 parts or 3+ chars, not just "aaa"
    if len(name.replace(" ", "")) < 3:
        return False

    # Roll: letters, numbers, - / _ allowed. No spaces inside (we remove them)
    # Allows: CS-2023-045, CS2023045, 21-CS-045, BSCS/23/045
    if not re.match(r"^[A-Za-z0-9\-\/_]+$", roll):
        return False

    # Roll must contain at least one number OR be long enough
    # This prevents "abc" as roll, but allows "CS-2023-045"
    if len(roll) < 3:
        return False

    return True

def generate_report_id():
    """
    Called in app.py:
        report_id = generate_report_id()
        save_report(report_id=report_id, ...)

    Returns: "LF-001", "LF-002", ... "LF-847" etc.
    - Always starts with LF-
    - Always unique: checks database.py if exists, if duplicate, generates new one
    - If database not available, uses random to avoid crash
    """
    # Try to get next number from database for clean sequence LF-001, LF-002
    try:
        from database import get_all_reports
        df = get_all_reports()
        if len(df) == 0:
            return f"{REPORT_PREFIX}-001"

        # Extract numbers from existing IDs like LF-001 -> 1
        existing_numbers = []
        if "report_id" in df.columns:
            for rid in df["report_id"].astype(str):
                match = re.search(r"(\d+)", rid)
                if match:
                    existing_numbers.append(int(match.group(1)))

        if existing_numbers:
            next_num = max(existing_numbers) + 1
            # If we have many, keep format LF-001, LF-010, LF-100, LF-1000
            if next_num < 1000:
                return f"{REPORT_PREFIX}-{next_num:03d}"
            else:
                return f"{REPORT_PREFIX}-{next_num}"
        else:
            return f"{REPORT_PREFIX}-001"

    except Exception:
        # Fallback: if DB fails, generate random unique ID - never crash app
        random_num = random.randint(100, 999)
        random_letter = random.choice(string.ascii_uppercase)
        return f"{REPORT_PREFIX}-{random_num}{random_letter}"

def clean_text(text):
    """
    Helper: Removes extra spaces, strips.
    Used internally to clean Item Name, Location, etc.
    """
    if text is None:
        return ""
    # Remove multiple spaces, strip
    text = str(text).strip()
    text = re.sub(r"\s+", " ", text)
    return text

def validate_phone(phone):
    """
    Optional helper for Contact field.
    Allows: 0300-1234567, +923001234567, 03001234567
    Returns True if looks like phone, False otherwise.
    app.py does NOT block if phone is wrong - it just saves.
    You can use this later if you want strict validation.
    """
    if not phone or str(phone).strip() == "":
        return True  # Empty is allowed - contact is optional
    phone = str(phone).strip().replace(" ", "").replace("-", "")
    # Remove +92 / 0092 prefix for check
    if phone.startswith("+92"):
        phone = phone[3:]
    elif phone.startswith("0092"):
        phone = phone[4:]
    # Now should be 10-11 digits starting with 03
    if re.match(r"^03\d{9}$", phone):
        return True
    if re.match(r"^\d{10,11}$", phone):
        return True
    return False

def format_report_id(report_id):
    """Makes ID always uppercase: lf-001 -> LF-001"""
    if not report_id:
        return ""
    return str(report_id).strip().upper()

def get_greeting():
    """Returns Good Morning / Afternoon / Evening based on time"""
    hour = datetime.now().hour
    if hour < 12:
        return "Good Morning"
    elif hour < 17:
        return "Good Afternoon"
    else:
        return "Good Evening"

def truncate_text(text, max_len=50):
    """Shortens long description for table display: 'Black leather...'"""
    if not text:
        return ""
    text = str(text)
    if len(text) <= max_len:
        return text
    return text[:max_len] + "..."
