import pytest
from fastapi import HTTPException

from app import seed
from app.db import connect
from app.repositories import history, rolls
from app.services import estimate_service

seed.init_db()

_conn = connect()
_conn.execute(
    "INSERT INTO walls(name,perimeter,height,data_quality,note) VALUES (?,?,?,?,?)",
    ("负花高房", 20.0, 2.8, "clean", ""),
)
_conn.execute(
    "INSERT INTO rolls(name,width,length,pattern_cm,match_type,data_quality,note) VALUES (?,?,?,?,?,?,?)",
    ("负花卷", 0.53, 10.0, -64, "offset", "clean", ""),
)
_conn.commit()
NEG_WALL_ID = _conn.execute("SELECT id FROM walls WHERE name='负花高房'").fetchone()["id"]
NEG_ROLL_ID = _conn.execute("SELECT id FROM rolls WHERE name='负花卷'").fetchone()["id"]
_conn.close()


def test_offset_negative_pattern_rejected_and_no_row():
    before = len(history.list_runs(1000))
    with pytest.raises(HTTPException) as ei:
        estimate_service.run_estimate(NEG_WALL_ID, NEG_ROLL_ID, True, "不应落库", "offset")
    assert ei.value.status_code == 422
    after = len(history.list_runs(1000))
    assert after == before, "跳对负花高被拒绝时不得新增 run"


def test_saved_run_pins_match_type_independent_of_roll_default():
    # 用跳对试算并保存
    saved = estimate_service.run_estimate(2, 2, True, "跳对留档", "offset")
    run_id = saved["run_id"]
    assert saved["match_type"] == "offset"
    assert saved["drop_len_m"] == 3.76
    assert saved["strips_per_roll"] == 2
    assert saved["rolls"] == 19

    # 事后只改卷材默认匹配方式为直对
    rolls.update_match_type(2, "straight")
    run = history.get_run(run_id)
    assert run["result"]["match_type"] == "offset"
    assert run["result"]["drop_len_m"] == 3.76
    assert run["result"]["strips_per_roll"] == 2
    assert run["result"]["rolls"] == 19

    # 回看接口同样返回写入时的值
    # （重置回直对，保持种子语义）
    rolls.update_match_type(2, "straight")
    again = history.get_run(run_id)["result"]
    assert again["match_type"] == "offset"
    assert again["drop_len_m"] == 3.76
    assert again["rolls"] == 19


def test_saved_straight_run_not_recomputed_with_roll_default_offset():
    # 对称情形：直对落库后把卷材默认改成跳对，回看不得跟着重算
    saved = estimate_service.run_estimate(2, 2, True, "直对留档", "straight")
    run_id = saved["run_id"]
    assert saved["drop_len_m"] == 3.44
    assert saved["rolls"] == 19
    rolls.update_match_type(2, "offset")
    try:
        run = history.get_run(run_id)
        assert run["result"]["match_type"] == "straight"
        assert run["result"]["drop_len_m"] == 3.44
        assert run["result"]["strips_per_roll"] == 2
        assert run["result"]["rolls"] == 19
    finally:
        rolls.update_match_type(2, "straight")


def test_list_runs_summary_pins_saved_values():
    # 列表摘要与按号回看一致，均为落库时钉住的值
    saved = estimate_service.run_estimate(2, 2, True, "跳对列表钉住", "offset")
    run_id = saved["run_id"]
    item = next(r for r in history.list_runs(1000) if r["id"] == run_id)
    assert item["result"]["match_type"] == "offset"
    assert item["result"]["drop_len_m"] == 3.76
    assert item["result"]["strips_per_roll"] == 2
    assert item["result"]["rolls"] == 19


def test_default_match_type_falls_back_to_roll_default():
    # 不显式传 match_type 时沿用卷材当前默认（此时 roll 2 默认已是 straight）
    r = estimate_service.run_estimate(2, 2, False, "", None)
    assert r["match_type"] == "straight"
    assert r["drop_len_m"] == 3.44
