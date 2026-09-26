from app.db import connect
from app.engines.wallpaper_math import MATCH_TYPES


def list_rolls():
    conn = connect()
    try:
        return [dict(r) for r in conn.execute("SELECT * FROM rolls ORDER BY id").fetchall()]
    finally:
        conn.close()


def get_roll(rid: int):
    conn = connect()
    try:
        row = conn.execute("SELECT * FROM rolls WHERE id=?", (rid,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def update_match_type(rid: int, match_type: str):
    if match_type not in MATCH_TYPES:
        raise ValueError("invalid match type")
    conn = connect()
    try:
        cur = conn.execute("UPDATE rolls SET match_type=? WHERE id=?", (match_type, rid))
        conn.commit()
        if cur.rowcount == 0:
            return None
        return dict(conn.execute("SELECT * FROM rolls WHERE id=?", (rid,)).fetchone())
    finally:
        conn.close()
