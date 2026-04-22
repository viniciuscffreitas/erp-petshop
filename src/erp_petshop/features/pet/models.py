from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from erp_petshop.core.db import Base
from erp_petshop.features.pet.enums import Especie


class Pet(Base):
    __tablename__ = "pet"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    nome: Mapped[str] = mapped_column(String(60))
    especie: Mapped[Especie] = mapped_column(
        SAEnum(Especie, name="especie", values_callable=lambda e: [m.value for m in e])
    )
    raca: Mapped[str | None] = mapped_column(String(80))
    observacoes: Mapped[str | None] = mapped_column(String(1000))
    cliente_id: Mapped[UUID] = mapped_column(
        ForeignKey("cliente.id", ondelete="RESTRICT"), index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
