from fastapi import HTTPException

from app.engines.wallpaper_math import MATCH_TYPES, STRAIGHT, roll_count
from app.repositories import history, rolls, walls


def run_estimate(wall_id: int, roll_id: int, save: bool, note: str, match_type: str | None = None):
    wall = walls.get_wall(wall_id)
    if not wall:
        raise HTTPException(404, "wall not found")
    roll = rolls.get_roll(roll_id)
    if not roll:
        raise HTTPException(404, "roll not found")
    if wall.get("data_quality") == "dirty" or roll.get("data_quality") == "dirty":
        raise HTTPException(422, "dirty seed entity")

    # 未显式指定时沿用卷材默认匹配方式；旧库列可能为 NULL，按直对待
    if match_type is None:
        match_type = roll.get("match_type") or STRAIGHT
    if match_type not in MATCH_TYPES:
        raise HTTPException(422, "invalid match type")

    try:
        # 花高为负的跳对等非法组合在此抛错：拒绝测算，且因在写库之前，不增行
        calc = roll_count(
            wall["perimeter"], wall["height"], roll["width"], roll["length"],
            roll["pattern_cm"], match_type,
        )
    except ValueError as exc:
        raise HTTPException(422, str(exc))

    run_id = None
    if save:
        # 钉住当次匹配方式、drop_len 与卷数，全部写进 result_json
        run_id = history.insert_run(wall_id, roll_id, {**calc, "wall_id": wall_id, "roll_id": roll_id}, note)
    return {"wall": wall, "roll": roll, "run_id": run_id, **calc}
