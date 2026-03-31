"""
Local SQLite database for development fallback.
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "swasthalink.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.executescript('''
        CREATE TABLE IF NOT EXISTS profiles (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            email TEXT UNIQUE,
            full_name TEXT,
            role TEXT,
            phone TEXT,
            phone_verified BOOLEAN DEFAULT 0,
            password_hash TEXT
        );

        CREATE TABLE IF NOT EXISTS prescriptions (
            prescription_id TEXT PRIMARY KEY,
            status TEXT,
            doctor_id TEXT,
            patient_id TEXT,
            patient_name TEXT,
            patient_age TEXT,
            patient_gender TEXT,
            doctor_name TEXT,
            prescription_date TEXT,
            diagnosis TEXT,
            notes TEXT,
            medications TEXT,
            extraction_confidence REAL,
            s3_key TEXT,
            created_at TEXT,
            admin_id TEXT,
            reviewed_at TEXT,
            rejection_reason TEXT
        );

        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            created_at TEXT,
            role TEXT,
            language TEXT,
            quiz_score INTEGER,
            whatsapp_sent BOOLEAN DEFAULT 0,
            re_explained BOOLEAN DEFAULT 0,
            log_format TEXT DEFAULT 'text'
        );

        CREATE TABLE IF NOT EXISTS session_history (
            id TEXT PRIMARY KEY,
            session_id TEXT,
            created_at TEXT,
            role TEXT,
            language TEXT,
            discharge_text TEXT,
            simplified_english TEXT,
            simplified_bengali TEXT,
            medications TEXT,
            follow_up TEXT,
            warning_signs TEXT,
            comprehension_questions TEXT,
            whatsapp_message TEXT,
            re_explain BOOLEAN DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS session_events (
            id TEXT PRIMARY KEY,
            session_id TEXT,
            created_at TEXT,
            event_type TEXT,
            event_data TEXT
        );
    ''')
    conn.commit()
    conn.close()


init_db()
