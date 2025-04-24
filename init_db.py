import sqlite3
import os
from werkzeug.security import generate_password_hash
import datetime

def init_db():
    """Initialize the database with tables and default admin user."""
    # Connect to SQLite database (creates it if it doesn't exist)
    db_path = os.environ.get('DATABASE_PATH', 'database.db')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Enable foreign keys
    c.execute("PRAGMA foreign_keys = ON")

    # Create tables
    # ===================== CORE NAVIGATION & CONTACTS =====================
    c.execute('''
    CREATE TABLE IF NOT EXISTS menu (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        icon TEXT,
        is_deleted INTEGER DEFAULT 0
    )
    ''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS year_name (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        img TEXT,
        text TEXT NOT NULL,
        is_deleted INTEGER DEFAULT 0
    )
    ''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS contacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        address TEXT,
        phone_number TEXT,
        email TEXT,
        is_deleted INTEGER DEFAULT 0
    )
    ''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS social_networks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        icon TEXT,
        link TEXT NOT NULL,
        is_deleted INTEGER DEFAULT 0
    )
    ''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        phone_number TEXT,
        email TEXT,
        theme TEXT,
        text TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_deleted INTEGER DEFAULT 0
    )
    ''')

    # ===================== STAFF =====================
    c.execute('''
    CREATE TABLE IF NOT EXISTS staff (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        position TEXT NOT NULL,
        full_name TEXT NOT NULL,
        email TEXT,
        phone TEXT,
        photo TEXT,
        is_deleted INTEGER DEFAULT 0
    )
    ''')

    # ===================== BLOG =====================
    c.execute('''
    CREATE TABLE IF NOT EXISTS blog_categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        is_deleted INTEGER DEFAULT 0
    )
    ''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS blog_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_id INTEGER,
        title TEXT NOT NULL,
        img_or_video_link TEXT,
        date_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        views INTEGER DEFAULT 0,
        text TEXT NOT NULL,
        intro_text TEXT,
        is_deleted INTEGER DEFAULT 0,
        FOREIGN KEY (category_id) REFERENCES blog_categories(id)
    )
    ''')

    # ===================== ABOUT COMPANY =====================
    c.execute('''
    CREATE TABLE IF NOT EXISTS about_company (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        img TEXT,
        date_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        views INTEGER DEFAULT 0,
        text TEXT NOT NULL,
        is_deleted INTEGER DEFAULT 0
    )
    ''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS about_company_categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        is_deleted INTEGER DEFAULT 0
    )
    ''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS about_company_category_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_id INTEGER,
        title TEXT NOT NULL,
        text TEXT NOT NULL,
        views INTEGER DEFAULT 0,
        date_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        feedback_id INTEGER,
        is_deleted INTEGER DEFAULT 0,
        FOREIGN KEY (category_id) REFERENCES about_company_categories(id),
        FOREIGN KEY (feedback_id) REFERENCES feedback(id)
    )
    ''')

    # ===================== DOCUMENTS =====================
    c.execute('''
    CREATE TABLE IF NOT EXISTS documents_categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        is_deleted INTEGER DEFAULT 0
    )
    ''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS documents_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_id INTEGER,
        title TEXT NOT NULL,
        name TEXT NOT NULL,
        link TEXT NOT NULL,
        is_deleted INTEGER DEFAULT 0,
        FOREIGN KEY (category_id) REFERENCES documents_categories(id)
    )
    ''')

    # ===================== OPTIONAL: LINK MENU ITEMS TO CONTENT =====================
    c.execute('''
    CREATE TABLE IF NOT EXISTS menu_links (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        menu_id INTEGER,
        target_type TEXT NOT NULL,
        target_id INTEGER,
        label TEXT,
        position INTEGER DEFAULT 0,
        is_deleted INTEGER DEFAULT 0,
        FOREIGN KEY (menu_id) REFERENCES menu(id)
    )
    ''')

    # ===================== ADMIN USERS =====================
    c.execute('''
    CREATE TABLE IF NOT EXISTS admin_users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT DEFAULT 'admin',
        created_at TIMESTAMP,
        last_login TIMESTAMP,
        is_deleted INTEGER DEFAULT 0
    )
    ''')

    # Create default admin user
    now = datetime.datetime.now().isoformat()
    default_username = "admin"
    default_password = "admin123"  # In production, use a secure password!
    
    # Check if admin user already exists
    c.execute("SELECT id FROM admin_users WHERE username = ?", (default_username,))
    if not c.fetchone():
        c.execute(
            "INSERT INTO admin_users (username, password_hash, role, created_at) VALUES (?, ?, ?, ?)",
            (default_username, generate_password_hash(default_password), "admin", now)
        )
        print(f"Created default admin user: {default_username} / {default_password}")
        print("IMPORTANT: Change this password after first login!")

    conn.commit()
    conn.close()
    
    print("Database initialized successfully!")

if __name__ == "__main__":
    init_db()
