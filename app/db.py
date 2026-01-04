import os
import sqlite3
from flask import g

DB_PATH = os.getenv("DB_PATH", "logs.db")


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH, check_same_thread=False)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_db():
    db = sqlite3.connect(DB_PATH, check_same_thread=False)
    db.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            level TEXT NOT NULL,
            service TEXT NOT NULL,
            message TEXT NOT NULL
        )
    """)
    db.commit()
    db.close()
