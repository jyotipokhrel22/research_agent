from pydantic import BaseModel
from typing import List, Dict


class ComparisonResult(BaseModel):
    common_methods: List[str]
    distinct_methods: List[str]

    dataset_overlap: Dict[str, int]   # dataset → count
    metric_overlap: Dict[str, int]

    shared_limitations: List[str]
    unique_limitations: List[str]

    contradictions: List[str]