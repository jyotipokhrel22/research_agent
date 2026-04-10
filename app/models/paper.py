from pydantic import BaseModel, field_validator
from typing import List

class Paper(BaseModel):
    title: str
    authors: List[str]
    abstract: str
    year: int

    @field_validator("title")
    def title_valid(cls, v):
        v = v.strip()
        if len(v) < 3:
            raise ValueError("Title must be at least 3 characters")
        return v

    @field_validator("authors")
    def authors_valid(cls, v):
        if len(v) < 1:
            raise ValueError("At least one author is required")
        return v

    @field_validator("year")
    def year_valid(cls, v):
        if v < 1900 or v > 2100:
            raise ValueError("Year must be between 1900 and 2100")
        return v

    @field_validator("abstract")
    def abstract_valid(cls, v):
        v = v.strip()
        if len(v) < 10:
            raise ValueError("Abstract must be at least 10 characters")
        return v