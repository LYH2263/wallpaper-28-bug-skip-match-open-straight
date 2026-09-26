"""Wallpaper rolls: perimeter strips, pattern repeat on drop length, strips per roll."""

import math

from app.engines.helpers import ceil_units, floor_units

STRAIGHT = "straight"  # 直对
OFFSET = "offset"      # 跳对（错花）
MATCH_TYPES = (STRAIGHT, OFFSET)


def roll_count(
    perimeter: float,
    height: float,
    roll_width: float,
    roll_length: float,
    pattern_cm: float,
    match_type: str = STRAIGHT,
) -> dict:
    if match_type not in MATCH_TYPES:
        raise ValueError("invalid match type")
    if roll_width <= 0 or roll_length <= 0:
        raise ValueError("invalid roll size")
    pattern_m = float(pattern_cm) / 100.0
    if match_type == OFFSET:
        if pattern_m < 0:
            # 跳对且花高为负：参数无意义，拒绝测算
            raise ValueError("offset match requires a non-negative pattern height")
        # 跳对在层高基础上再加半个花高，半花高向上取到毫米后换算
        extra_m = math.ceil(pattern_m * 1000.0 / 2.0) / 1000.0
    else:
        # 直对在层高基础上加整个花高，与改造前同参一致
        extra_m = max(0.0, pattern_m)
    drop_len = float(height) + extra_m
    if drop_len <= 0:
        raise ValueError("invalid drop length")
    drops = ceil_units(float(perimeter) / float(roll_width))
    strips_per_roll = max(1, floor_units(float(roll_length) / drop_len))
    rolls = ceil_units(drops / strips_per_roll)
    return {
        "drops": drops,
        "drop_len_m": round(drop_len, 3),
        "pattern_m": round(max(0.0, pattern_m), 3),
        "match_type": match_type,
        "strips_per_roll": strips_per_roll,
        "rolls": rolls,
    }
