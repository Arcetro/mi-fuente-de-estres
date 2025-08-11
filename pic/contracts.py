from enum import Enum
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, ConfigDict


class Intent(str, Enum):
    SALUDO = "SALUDO"
    DESPEDIDA = "DESPEDIDA"
    UBICACION = "UBICACION"
    POLITICAS = "POLITICAS"
    CONSULTA_PRECIO = "CONSULTA_PRECIO"
    DISPONIBILIDAD = "DISPONIBILIDAD"
    OTRO = "OTRO"


class MessageType(str, Enum):
    REQUEST = "REQUEST"
    RESPONSE = "RESPONSE"
    ERROR = "ERROR"


class PICContext(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sessionId: str
    locale: str = "es-AR"


class PICMessage(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    id: str
    version: Literal["pic.v1"] = "pic.v1"
    from_: str = Field(alias="from")
    to: str
    type: MessageType = MessageType.REQUEST
    context: PICContext
    payload: Dict[str, Any] = Field(default_factory=dict)
    trace: List[Dict[str, Any]] = Field(default_factory=list)


class T1Entities(BaseModel):
    model_config = ConfigDict(extra="forbid")

    checkin: Optional[str] = None
    noches: Optional[int] = None
    personas: Optional[int] = None
    tipo_unidad: Optional[str] = None


class T1Output(BaseModel):
    model_config = ConfigDict(extra="forbid")

    intent: Intent
    confidence: float
    entities: T1Entities = Field(default_factory=T1Entities)
    complexity_score: float = 0.0
    risk_flags: List[str] = Field(default_factory=list)
    reasons: str


class Brief(BaseModel):
    model_config = ConfigDict(extra="forbid")

    summary: str
    gaps: List[str] = Field(default_factory=list)


class T2Output(BaseModel):
    model_config = ConfigDict(extra="forbid")

    intent: Intent
    confidence: float
    entities: Dict[str, Any]
    brief: Brief
    next_action: Literal["respond", "reprompt", "escalate_t5"]


