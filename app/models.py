from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class Layer(str, Enum):
    REAL = "real"
    INCOME = "income"
    FINANCIAL = "financial"
    FISCAL = "fiscal"
    POLITICAL = "political"
    SEMANTIC = "semantic"


class EvidenceStatus(str, Enum):
    REPORTED = "reported"
    INFERRED = "inferred"
    RESIDUAL = "residual"
    ILLUSTRATIVE = "illustrative"


class Source(BaseModel):
    id: str
    name: str
    publisher: str
    url: str
    note: str


class Entity(BaseModel):
    id: str
    name: str
    kind: str
    sector: str
    description: str
    parent_id: str | None = None
    tags: list[str] = Field(default_factory=list)


class Flow(BaseModel):
    id: str
    source: str
    target: str
    type: str
    layer: Layer
    amount: float | None = None
    unit: str = "USD billions / year"
    period: str = "prototype"
    status: EvidenceStatus
    source_ids: list[str] = Field(default_factory=list)
    confidence: float | None = Field(default=None, ge=0, le=1)
    note: str = ""
    direction: Literal["money", "real", "semantic"] = "money"


class GraphPayload(BaseModel):
    entities: list[Entity]
    flows: list[Flow]
    sources: list[Source]
    metadata: dict[str, str]
