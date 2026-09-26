from fastapi import APIRouter, HTTPException
from app.repositories import history as repo

router = APIRouter()


@router.get("/runs")
def list_runs(limit: int = 50):
    return {"items": repo.list_runs(limit)}


@router.get("/runs/{run_id}")
def get_run(run_id: int):
    # 回看只从 result_json 还原写入时钉住的匹配方式/drop_len/卷数，
    # 不读取卷材当前默认值
    run = repo.get_run(run_id)
    if not run:
        raise HTTPException(404)
    return run
