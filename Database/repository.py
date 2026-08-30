"""
database/repository.py
Data Integration Repository for Cream Beans SIH 2026 Campus Lost & Found Intelligence System
Person 6: Database & Data-Integration Engineer

This repository provides database CRUD operations ensuring 100% adherence to the canonical
AI data structure and Supabase SQL schema contract without any field name conversions.
Supports both SQLite (in-memory/file for testing & local demo) and PostgreSQL / Supabase.
"""

import sqlite3
import json
import uuid
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any, Union

from database.models import User, Item, MatchResult, Claim, MatchDetails


class DatabaseRepository:
    def __init__(self, connection: Optional[Any] = None, db_path: str = ":memory:"):
        """
        Initialize repository. Accepts an active connection or creates a SQLite connection.
        """
        if connection:
            self.conn = connection
        else:
            self.conn = sqlite3.connect(db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
        self._init_sqlite_tables()

    def _init_sqlite_tables(self):
        """Ensure standard schema exists for SQLite fallback."""
        cursor = self.conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            is_admin INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id TEXT PRIMARY KEY,
            reporter_id TEXT NOT NULL REFERENCES users(id),
            type TEXT NOT NULL CHECK (type IN ('lost', 'found')),
            category TEXT NOT NULL,
            description TEXT NOT NULL,
            image_url TEXT,
            location TEXT NOT NULL,
            latitude REAL,
            longitude REAL,
            timestamp TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'matched', 'returned')),
            embedding TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS matches (
            id TEXT PRIMARY KEY,
            lost_item_id TEXT NOT NULL REFERENCES items(id),
            found_item_id TEXT NOT NULL REFERENCES items(id),
            image_score REAL NOT NULL,
            text_score REAL NOT NULL,
            location_score REAL NOT NULL,
            time_score REAL NOT NULL,
            final_score REAL NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS claims (
            id TEXT PRIMARY KEY,
            claimant_id TEXT NOT NULL REFERENCES users(id),
            lost_item_id TEXT NOT NULL REFERENCES items(id),
            found_item_id TEXT NOT NULL REFERENCES items(id),
            match_id TEXT REFERENCES matches(id),
            status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected')),
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        """)
        self.conn.commit()

    # =========================================================================
    # 1. USER OPERATIONS
    # =========================================================================
    def insert_user(self, user: User) -> User:
        """Insert user into database."""
        cursor = self.conn.cursor()
        now_str = datetime.now(timezone.utc).isoformat()
        if not user.created_at:
            user.created_at = now_str
        is_admin_int = 1 if user.is_admin else 0
        cursor.execute(
            """
            INSERT INTO users (id, name, email, phone, is_admin, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (user.id, user.name, user.email, user.phone, is_admin_int, user.created_at)
        )
        self.conn.commit()
        return user

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by primary key id."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, name, email, phone, is_admin, created_at FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return User.from_dict(dict(row))

    def get_reporter_info(self, reporter_id: str) -> Optional[User]:
        """
        Retrieve reporter information (name, email, phone) given reporter_id.
        Contract rule: AI engine does NOT receive contact info, backend looks up user via reporter_id.
        """
        return self.get_user_by_id(reporter_id)

    # =========================================================================
    # 2. ITEM OPERATIONS
    # =========================================================================
    def insert_item(self, item: Item) -> Item:
        """
        Insert item into database (lost or found).
        Enforces type in ('lost', 'found') and status in ('active', 'matched', 'returned').
        """
        if item.type not in ('lost', 'found'):
            raise ValueError(f"Invalid item type '{item.type}'. Must be 'lost' or 'found'.")
        if item.status not in ('active', 'matched', 'returned'):
            raise ValueError(f"Invalid status '{item.status}'. Must be 'active', 'matched', or 'returned'.")

        cursor = self.conn.cursor()
        now_str = datetime.now(timezone.utc).isoformat()
        if not item.created_at:
            item.created_at = now_str

        embedding_json = json.dumps(item.embedding) if item.embedding is not None else None

        cursor.execute(
            """
            INSERT INTO items (
                id, reporter_id, type, category, description, image_url,
                location, latitude, longitude, timestamp, status, embedding, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                item.id, item.reporter_id, item.type, item.category, item.description,
                item.image_url, item.location, item.latitude, item.longitude,
                item.timestamp, item.status, embedding_json, item.created_at
            )
        )
        self.conn.commit()
        return item

    def get_item_by_id(self, item_id: str) -> Optional[Item]:
        """Retrieve single item by id."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT id, reporter_id, type, category, description, image_url,
                   location, latitude, longitude, timestamp, status, embedding, created_at
            FROM items WHERE id = ?
            """,
            (item_id,)
        )
        row = cursor.fetchone()
        if not row:
            return None
        d = dict(row)
        if d.get("embedding") and isinstance(d["embedding"], str):
            try:
                d["embedding"] = json.loads(d["embedding"])
            except json.JSONDecodeError:
                d["embedding"] = None
        return Item.from_dict(d)

    def get_all_items(self) -> List[Item]:
        """Retrieve all items."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT id, reporter_id, type, category, description, image_url,
                   location, latitude, longitude, timestamp, status, embedding, created_at
            FROM items ORDER BY created_at DESC
            """
        )
        rows = cursor.fetchall()
        items = []
        for r in rows:
            d = dict(r)
            if d.get("embedding") and isinstance(d["embedding"], str):
                try:
                    d["embedding"] = json.loads(d["embedding"])
                except json.JSONDecodeError:
                    d["embedding"] = None
            items.append(Item.from_dict(d))
        return items

    def get_active_found_items(self) -> List[Item]:
        """
        Retrieve only active FOUND items for AI matching comparison against ONE lost item.
        CRITICAL RULE: Never return lost items or non-active items in found candidates!
        """
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT id, reporter_id, type, category, description, image_url,
                   location, latitude, longitude, timestamp, status, embedding, created_at
            FROM items
            WHERE type = 'found' AND status = 'active'
            ORDER BY created_at DESC
            """
        )
        rows = cursor.fetchall()
        items = []
        for r in rows:
            d = dict(r)
            if d.get("embedding") and isinstance(d["embedding"], str):
                try:
                    d["embedding"] = json.loads(d["embedding"])
                except json.JSONDecodeError:
                    d["embedding"] = None
            items.append(Item.from_dict(d))
        return items

    def update_item_status(self, item_id: str, new_status: str) -> Optional[Item]:
        """Update status of an item ('active' -> 'matched' -> 'returned')."""
        if new_status not in ('active', 'matched', 'returned'):
            raise ValueError(f"Invalid status '{new_status}'. Must be 'active', 'matched', or 'returned'.")

        cursor = self.conn.cursor()
        cursor.execute("UPDATE items SET status = ? WHERE id = ?", (new_status, item_id))
        self.conn.commit()
        return self.get_item_by_id(item_id)

    # =========================================================================
    # 3. MATCH OPERATIONS
    # =========================================================================
    def insert_match_result(
        self,
        lost_item_id: str,
        found_item_id: str,
        image_score: float,
        text_score: float,
        location_score: float,
        time_score: float,
        final_score: float,
        match_id: Optional[str] = None
    ) -> MatchResult:
        """
        Insert AI match result into 'matches' table.
        Backend maps AI candidates to matches.found_item_id and score metrics directly.
        """
        if not match_id:
            match_id = str(uuid.uuid4())
        now_str = datetime.now(timezone.utc).isoformat()

        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO matches (
                id, lost_item_id, found_item_id, image_score, text_score,
                location_score, time_score, final_score, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                match_id, lost_item_id, found_item_id, image_score, text_score,
                location_score, time_score, final_score, now_str
            )
        )
        self.conn.commit()

        return MatchResult(
            id=match_id,
            lost_item_id=lost_item_id,
            found_item_id=found_item_id,
            image_score=image_score,
            text_score=text_score,
            location_score=location_score,
            time_score=time_score,
            final_score=final_score,
            created_at=now_str
        )

    def get_matches_for_lost_item(self, lost_item_id: str) -> List[MatchResult]:
        """Get all stored matches for a lost item ordered by final score descending."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT id, lost_item_id, found_item_id, image_score, text_score,
                   location_score, time_score, final_score, created_at
            FROM matches
            WHERE lost_item_id = ?
            ORDER BY final_score DESC
            """,
            (lost_item_id,)
        )
        rows = cursor.fetchall()
        return [MatchResult.from_dict(dict(r)) for r in rows]

    def get_complete_match_info(self, match_id: str) -> Optional[MatchDetails]:
        """
        Retrieve complete match information including:
        - MatchResult (scores)
        - Lost Item
        - Found Item
        - Found Item Reporter Contact Details (User)
        """
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT id, lost_item_id, found_item_id, image_score, text_score,
                   location_score, time_score, final_score, created_at
            FROM matches WHERE id = ?
            """,
            (match_id,)
        )
        match_row = cursor.fetchone()
        if not match_row:
            return None

        match_res = MatchResult.from_dict(dict(match_row))
        lost_item = self.get_item_by_id(match_res.lost_item_id)
        found_item = self.get_item_by_id(match_res.found_item_id)

        if not lost_item or not found_item:
            return None

        found_reporter = self.get_reporter_info(found_item.reporter_id)

        return MatchDetails(
            match=match_res,
            lost_item=lost_item,
            found_item=found_item,
            found_reporter=found_reporter
        )

    # =========================================================================
    # 4. CLAIM OPERATIONS (Minimal SIH Claim System)
    # =========================================================================
    def insert_claim(self, claim: Claim) -> Claim:
        """
        Submit a new item ownership claim.
        Associates claimant_id, lost_item_id, found_item_id, match_id, and status ('pending').
        """
        cursor = self.conn.cursor()
        now_str = datetime.now(timezone.utc).isoformat()
        if not claim.created_at:
            claim.created_at = now_str

        cursor.execute(
            """
            INSERT INTO claims (id, claimant_id, lost_item_id, found_item_id, match_id, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (claim.id, claim.claimant_id, claim.lost_item_id, claim.found_item_id, claim.match_id, claim.status, claim.created_at)
        )
        self.conn.commit()
        return claim

    def get_claim_by_id(self, claim_id: str) -> Optional[Claim]:
        """Retrieve single claim by id."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id, claimant_id, lost_item_id, found_item_id, match_id, status, created_at FROM claims WHERE id = ?",
            (claim_id,)
        )
        row = cursor.fetchone()
        if not row:
            return None
        return Claim.from_dict(dict(row))

    def get_claims_for_user(self, user_id: str) -> List[Claim]:
        """Retrieve all claims submitted by a specific user (claimant)."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id, claimant_id, lost_item_id, found_item_id, match_id, status, created_at FROM claims WHERE claimant_id = ? ORDER BY created_at DESC",
            (user_id,)
        )
        rows = cursor.fetchall()
        return [Claim.from_dict(dict(r)) for r in rows]

    def get_all_claims(self) -> List[Claim]:
        """Retrieve all claims (for Admin/Security interface)."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id, claimant_id, lost_item_id, found_item_id, match_id, status, created_at FROM claims ORDER BY created_at DESC"
        )
        rows = cursor.fetchall()
        return [Claim.from_dict(dict(r)) for r in rows]

    def update_claim_status(self, claim_id: str, new_status: str) -> Optional[Claim]:
        """Update claim status ('pending' -> 'approved' -> 'rejected')."""
        if new_status not in ('pending', 'approved', 'rejected'):
            raise ValueError(f"Invalid claim status '{new_status}'. Must be 'pending', 'approved', or 'rejected'.")

        cursor = self.conn.cursor()
        cursor.execute("UPDATE claims SET status = ? WHERE id = ?", (new_status, claim_id))
        self.conn.commit()
        return self.get_claim_by_id(claim_id)
