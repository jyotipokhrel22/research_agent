from pydantic import BaseModel
from typing import List, Optional


class RawPaper(BaseModel):
    paper_id: str
    title: str
    abstract: Optional[str] = None
    authors: List[str] = []
    published: Optional[str] = None  # raw string from arXiv
    pdf_url: Optional[str] = None