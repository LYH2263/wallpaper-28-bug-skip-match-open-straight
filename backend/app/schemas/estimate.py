from typing import Literal, Optional

from pydantic import BaseModel

MatchType = Literal["straight", "offset"]


class EstimateRequest(BaseModel):
    wall_id: int
    roll_id: int
    # 当次测算匹配方式；缺省取卷材默认匹配方式
    match_type: Optional[MatchType] = None
    save: bool = False
    note: str = ""


class RollMatchTypeUpdate(BaseModel):
    match_type: MatchType
