"""SQLite DDL for support tables (auth, tasks, chat, assets)."""

USERS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    display_name TEXT NOT NULL,
    role TEXT NOT NULL,
    password_hash TEXT,
    active INTEGER DEFAULT 1,
    must_change_password INTEGER DEFAULT 1,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
)
"""

TASKS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    assigned_by TEXT,
    assigned_to TEXT,
    priority TEXT DEFAULT 'Medium',
    status TEXT DEFAULT 'Open',
    progress INTEGER DEFAULT 0,
    due_date TEXT,
    vendor_flag INTEGER DEFAULT 0,
    vendor_status TEXT,
    vendor_remark TEXT,
    reminder_date TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
)
"""

COMMENTS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS task_comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    comment TEXT NOT NULL,
    commented_by TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
"""

NOTIFICATIONS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    message TEXT NOT NULL,
    is_read INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
"""

VENDOR_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS vendor_followups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticket_id INTEGER NOT NULL,
    vendor_name TEXT,
    followup_status TEXT DEFAULT 'Pending from Vendor',
    vendor_remark TEXT,
    due_date TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
"""

CHAT_THREADS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS chat_threads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    created_by TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
"""

CHAT_MESSAGES_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS chat_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    thread_id INTEGER NOT NULL,
    sender TEXT NOT NULL,
    message TEXT NOT NULL,
    linked_ticket_id INTEGER,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
"""

USER_STATUS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS user_status (
    username TEXT PRIMARY KEY,
    display_name TEXT,
    status TEXT DEFAULT 'Available',
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
)
"""

ASSET_REGISTRY_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS asset_registry (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_id TEXT,
    asset_type TEXT,
    location TEXT,
    vendor TEXT,
    purchase_date TEXT,
    warranty_end TEXT,
    status TEXT DEFAULT 'Active'
)
"""

# Reserved for Phase 2+ persistent login
AUTH_SESSIONS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS auth_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    token TEXT UNIQUE NOT NULL,
    expires_at TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
"""
