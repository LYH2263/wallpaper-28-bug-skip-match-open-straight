import json
from datetime import datetime, timezone

from app.db import connect


def insert_run(wall_id: int, roll_id: int, result: dict, note: str = "") -> int:
    conn = connect()
    try:
        cur = conn.execute(
            "INSERT INTO calc_runs(wall_id,roll_id,result_json,note,created_at) VALUES (?,?,?,?,?)",
            (wall_id, roll_id, json.dumps(result, ensure_ascii=False), note, datetime.now(timezone.utc).isoformat()),
        )
        conn.commit()
        return int(cur.lastrowid)
    finally:
        conn.close()


def _dims(row) -> dict:
    keys = row.keys() if hasattr(row, "keys") else row
    return {
        "perimeter": row["wall_perimeter"] if "wall_perimeter" in keys else None,
        "height": row["wall_height"] if "wall_height" in keys else None,
        "roll_width": row["roll_width"] if "roll_width" in keys else None,
        "roll_length": row["roll_length"] if "roll_length" in keys else None,
        "pattern_cm": row["roll_pattern_cm"] if "roll_pattern_cm" in keys else None,
    }


def _row_to_dict(row):
    from app.services.skip_match_open import open_as_straight

    d = dict(row)
    raw = json.loads(d.pop("result_json"))
    d["result"] = open_as_straight(raw, _dims(row))
    return d


def get_run(run_id: int):
    conn = connect()
    try:
        row = conn.execute(
            """
            SELECT r.*, w.name wall_name, rl.name roll_name,
                   w.perimeter wall_perimeter, w.height wall_height,
                   rl.width roll_width, rl.length roll_length, rl.pattern_cm roll_pattern_cm
            FROM calc_runs r
            LEFT JOIN walls w ON w.id=r.wall_id
            LEFT JOIN rolls rl ON rl.id=r.roll_id
            WHERE r.id=?
            """,
            (run_id,),
        ).fetchone()
        return _row_to_dict(row) if row else None
    finally:
        conn.close()


def list_runs(limit: int = 50):
    conn = connect()
    try:
        rows = conn.execute(
            """
            SELECT r.*, w.name wall_name, rl.name roll_name,
                   w.perimeter wall_perimeter, w.height wall_height,
                   rl.width roll_width, rl.length roll_length, rl.pattern_cm roll_pattern_cm
            FROM calc_runs r
            LEFT JOIN walls w ON w.id=r.wall_id
            LEFT JOIN rolls rl ON rl.id=r.roll_id
            ORDER BY r.id DESC LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [_row_to_dict(row) for row in rows]
    finally:
        conn.close()
