import pytest

from app.engines.wallpaper_math import OFFSET, STRAIGHT, roll_count


def test_plain_master_bed():
    r = roll_count(16.0, 2.7, 0.53, 10.0, 0)
    assert r["drops"] == 31
    assert r["drop_len_m"] == 2.7
    assert r["strips_per_roll"] == 3
    assert r["rolls"] == 11


def test_pattern_wall_straight():
    # 直对：层高 2.8 + 半个花高 0.32 = 3.12m，10m 卷可裁 3 条，38 条需 13 卷
    r = roll_count(20.0, 2.8, 0.53, 10.0, 64)
    assert r["drops"] == 38
    assert r["drop_len_m"] == 3.12
    assert r["strips_per_roll"] == 3
    assert r["rolls"] == 13
    assert r["match_type"] == STRAIGHT


def test_straight_explicit_matches_default():
    # 直对显式传参与缺省匹配方式结果一致
    assert roll_count(20.0, 2.8, 0.53, 10.0, 64, STRAIGHT) == roll_count(
        20.0, 2.8, 0.53, 10.0, 64
    )


def test_offset_pattern_64():
    # 跳对：层高 2.8 + 整个花高 0.64 = 3.44m，10m 卷可裁 2 条，38 条需 19 卷
    r = roll_count(20.0, 2.8, 0.53, 10.0, 64, OFFSET)
    assert r["drop_len_m"] == 3.44
    assert r["strips_per_roll"] == 2
    assert r["rolls"] == 19
    assert r["match_type"] == OFFSET


def test_offset_drop_longer_than_straight_same_params():
    # 同参下跳对条长必须长于直对，每卷条数不增加，卷数不少于直对
    s = roll_count(20.0, 2.8, 0.53, 10.0, 64, STRAIGHT)
    o = roll_count(20.0, 2.8, 0.53, 10.0, 64, OFFSET)
    assert o["drop_len_m"] > s["drop_len_m"]
    assert o["strips_per_roll"] <= s["strips_per_roll"]
    assert o["rolls"] >= s["rolls"]


def test_straight_half_pattern_rounds_up_to_mm():
    # 直对加半个花高：花高 65cm 半高 325mm 整；64.1cm 半高 320.5mm 向上取到 321mm -> 0.321m
    r_even = roll_count(20.0, 2.8, 0.53, 10.0, 65, STRAIGHT)
    assert r_even["drop_len_m"] == 3.125
    r_odd = roll_count(20.0, 2.8, 0.53, 10.0, 64.1, STRAIGHT)
    assert r_odd["drop_len_m"] == 3.121


def test_zero_pattern_same_for_both_match_types():
    s = roll_count(16.0, 2.7, 0.53, 10.0, 0, STRAIGHT)
    o = roll_count(16.0, 2.7, 0.53, 10.0, 0, OFFSET)
    assert o["drop_len_m"] == s["drop_len_m"]
    assert o["rolls"] == s["rolls"]
    assert o["strips_per_roll"] == s["strips_per_roll"]


def test_offset_negative_pattern_rejected():
    with pytest.raises(ValueError):
        roll_count(20.0, 2.8, 0.53, 10.0, -5, OFFSET)


def test_straight_negative_pattern_treated_as_zero():
    # 直对负花高沿用既有行为：花高按 0 截断
    r = roll_count(16.0, 2.7, 0.53, 10.0, -5, STRAIGHT)
    assert r["drop_len_m"] == 2.7
