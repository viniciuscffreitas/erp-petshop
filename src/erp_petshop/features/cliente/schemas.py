from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator


class ClienteCreate(BaseModel):
    nome: str = Field(min_length=1, max_length=100)
    telefone: str | None = Field(default=None, pattern=r"^\+?\d{8,20}$")
    email: EmailStr | None = None
    observacoes: str | None = Field(default=None, max_length=1000)

    @model_validator(mode="after")
    def _pelo_menos_um_canal(self) -> ClienteCreate:
        if not self.telefone and not self.email:
            raise ValueError("cliente precisa de telefone ou email")
        return self


class ClienteUpdate(BaseModel):
    nome: str | None = Field(default=None, min_length=1, max_length=100)
    telefone: str | None = Field(default=None, pattern=r"^\+?\d{8,20}$")
    email: EmailStr | None = None
    observacoes: str | None = Field(default=None, max_length=1000)


class ClienteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    nome: str
    telefone: str | None
    email: str | None
    observacoes: str | None
    created_at: datetime
    updated_at: datetime
