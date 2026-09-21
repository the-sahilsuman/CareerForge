from pydantic import BaseModel, Field


class ParsedDocument(BaseModel):
    text: str = Field(min_length=1)
    page_count: int = 0
    content_type: str
    source_key: str
    warnings: list[str] = Field(default_factory=list)