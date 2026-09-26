import pytest

from app.engines.wallpaper_math import OFFSET, STRAIGHT, roll_count


def test_plain_master_bed():
    r = roll_count(16.0, 2.7, 0.53, 10.0, 0)
    assert r["drops"] == 31
    assert r["drop_len_m"] == 2.7
    assert r["strips_per_roll"] == 3
    assert r["rolls"] == 11


def test_pattern_wall():
    r = roll_count(20.0, 2.8, 0.53, 10.0, 64)
    assert r["drops"] == 38
    assert r["drop_len_m"] == 3.44
    assert r["strips_per_roll"] == 2
    assert r["rolls"] == 19
    assert r["match_type"] == STRAIGHT


def test_straight_explicit_matches_legacy():
    # 直对显式传参与改造前同参结果一致
    assert roll_count(20.0, 2.8, 0.53, 10.0, 64, STRAIGHT) == roll_count(
        20.0, 2.8, 0.53, 10.0, 64
    )


def test_offset_pattern_64():
    # 跳对：层高 2.8 + 花高 0.64 + 半花高 0.32 = 3.76m，10m 卷可裁 2 条，38 条需 19 卷
    r = roll_count(20.0, 2.8, 0.53, 10.0, 64, OFFSET)
    assert r["drop_len_m"] == 3.76
    assert r["strips_per_roll"] == 2
    assert r["rolls"] == 19
    assert r["match_type"] == OFFSET


def test_offset_drop_len_longer_than_same_param_straight():
    # 同参下跳对条长必须严格长于直对，rolls 按加长后的条长计算
    s = roll_count(20.0, 2.8, 0.53, 10.0, 64, STRAIGHT)
    o = roll_count(20.0, 2.8, 0.53, 10.0, 64, OFFSET)
    assert o["drop_len_m"] > s["drop_len_m"]


def test_offset_rolls_use_lengthened_drop():
    # 层高 2.6 + 0.64 + 0.32 = 3.56m：每卷 2 条（直对 3.24m 可裁 3 条），卷数随之变多
    o = roll_count(20.0, 2.6, 0.53, 10.0, 64, OFFSET)
    assert o["drop_len_m"] == 3.56
    assert o["strips_per_roll"] == 2
    assert o["rolls"] == 19
    s = roll_count(20.0, 2.6, 0.53, 10.0, 64, STRAIGHT)
    assert s["strips_per_roll"] == 3
    assert s["rolls"] == 13


def test_offset_half_pattern_rounds_up_to_mm():
    # 花高 65cm：半花高 325mm 整 -> 2.8+0.65+0.325；64.1cm：320.5mm 向上取到 321mm -> 2.8+0.641+0.321
    r_even = roll_count(20.0, 2.8, 0.53, 10.0, 65, OFFSET)
    assert r_even["drop_len_m"] == 3.775
    r_odd = roll_count(20.0, 2.8, 0.53, 10.0, 64.1, OFFSET)
    assert r_odd["drop_len_m"] == 3.762


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
    # 直对负花高沿用改造前行为：花高按 0 截断
    r = roll_count(16.0, 2.7, 0.53, 10.0, -5, STRAIGHT)
    assert r["drop_len_m"] == 2.7
