from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from erp_petshop.features.pet.enums import Especie


class PetCreate(BaseModel):
    nome: str = Field(min_length=1, max_length=60)
    especie: Especie
    raca: str | None = Field(default=None, max_length=80)
    observacoes: str | None = Field(default=None, max_length=1000)
    cliente_id: UUID


class PetUpdate(BaseModel):
    nome: str | None = Field(default=None, min_length=1, max_length=60)
    especie: Especie | None = None
    raca: str | None = Field(default=None, max_length=80)
    observacoes: str | None = Field(default=None, max_length=1000)


class PetRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    nome: str
    especie: Especie
    raca: str | None
    observacoes: str | None
    cliente_id: UUID
    created_at: datetime
    updated_at: datetime
