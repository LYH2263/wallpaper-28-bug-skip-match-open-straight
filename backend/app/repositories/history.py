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


def _row_to_dict(row):
    # 原样还原写入时钉住的 match_type/drop_len/每卷条数/卷数，
    # 绝不按卷材当前默认匹配方式重算
    d = dict(row)
    d["result"] = json.loads(d.pop("result_json"))
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
