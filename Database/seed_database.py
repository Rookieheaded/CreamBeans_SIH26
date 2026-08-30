"""
database/seed_database.py
Seed Database Script for Cream Beans SIH 2026 Campus Lost & Found System
Person 6: Database & Data-Integration Engineer

Executes database/seed.sql against target SQLite/PostgreSQL database to seed
5 users, 20 found items, and 10 lost items deterministically.
"""

import os
import sqlite3
import re
from typing import Optional


def run_seed(db_path: str = "database/lost_and_found.db", seed_sql_path: str = "database/seed.sql"):
    """
    Applies seed.sql onto SQLite database file.
    """
    print(f"[Seed] Seeding database at '{db_path}' using '{seed_sql_path}'...")
    
    if not os.path.exists(seed_sql_path):
        raise FileNotFoundError(f"Seed SQL file not found at: {seed_sql_path}")

    # Ensure parent directory exists for DB file
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)

    with open(seed_sql_path, "r", encoding="utf-8") as f:
        sql_script = f.read()

    # Create tables first using repo logic
    from database.repository import DatabaseRepository
    conn = sqlite3.connect(db_path)
    repo = DatabaseRepository(connection=conn)

    # Strip PostgreSQL PL/pgSQL 'DO $$ ... END $$;' block for SQLite compatibility
    sqlite_script = re.sub(r"DO\s*\$\$[\s\S]*?END\s*\$\$;", "", sql_script, flags=re.IGNORECASE)

    # Clear existing tables for SQLite
    cursor = conn.cursor()
    cursor.execute("DELETE FROM matches;")
    cursor.execute("DELETE FROM items;")
    cursor.execute("DELETE FROM users;")

    cursor.executescript(sqlite_script)
    conn.commit()

    # Verification
    cursor.execute("SELECT COUNT(*) FROM users;")
    user_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM items WHERE type = 'found';")
    found_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM items WHERE type = 'lost';")
    lost_count = cursor.fetchone()[0]

    conn.close()

    print(f"[Seed] Successfully seeded {user_count} users, {found_count} found items, and {lost_count} lost items.")
    return user_count, found_count, lost_count


if __name__ == "__main__":
    run_seed()
