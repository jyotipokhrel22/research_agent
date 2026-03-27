from pydantic import BaseModel
from typing import Optional


class Chunk(BaseModel):
    chunk_id: str
    paper_id: str

    section: Optional[str] = None  # e.g. "method", "experiments"
    content: str

    # retrieval metadata
    score: Optional[float] = None