"""
models/__init__.py – DB connection helper shared by all models.
"""
from flask import g
import pymysql
from config import Config


def get_db() -> pymysql.connections.Connection:
    """Return or open the per-request PyMySQL connection stored on flask.g."""
    if "db" not in g:
        g.db = pymysql.connect(
            host=Config.MYSQL_HOST,
            port=Config.MYSQL_PORT,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB,
            cursorclass=pymysql.cursors.DictCursor,
            charset="utf8mb4",
            autocommit=False,
        )
    return g.db


def query_one(sql: str, params: tuple = ()) -> dict | None:
    db = get_db()
    with db.cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchone()


def query_all(sql: str, params: tuple = ()) -> list[dict]:
    db = get_db()
    with db.cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchall()


def execute(sql: str, params: tuple = ()) -> int:
    """Execute INSERT/UPDATE/DELETE; returns lastrowid."""
    db = get_db()
    with db.cursor() as cur:
        cur.execute(sql, params)
    return cur.lastrowid

