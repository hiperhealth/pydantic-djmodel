"""A downstream app that generates a model during Django startup."""

from typing import Optional

from pydantic import BaseModel, Field
from pydantic_djmodel.core import pydantic_to_django


class RecordSchema(BaseModel):
    """Exercise the supported mappings in one Django app."""

    displayName: str
    count: int
    score: float | None = None
    reference: Optional[int] = None
    active: bool = True
    show: bool
    tags: list[str] = Field(default_factory=list)
    payload: dict[str, str] = {'state': 'new'}
    variant: int | str
    optionalVariant: int | str | None = None


Record = pydantic_to_django(RecordSchema, 'Record', __name__)
