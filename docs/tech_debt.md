# Technical Debt — ERP Pet Shop

Débito explicitamente aceito durante o MVP. Cada item tem estado, workaround e resolução esperada.

## TD-001 — `NAO_COMPARECEU` não modelado

**Estado:** aceito v1.
**Workaround:** operadora marca agendamento como `CANCELADO` quando cliente não aparece. Relatório perde granularidade (cancelado ≠ no-show).
**Resolução esperada:** v2 — adicionar `NAO_COMPARECEU` como transição terminal a partir de `AGENDADO` e `EM_BANHO`. Métrica separada no relatório financeiro.

## TD-002 — Auth ainda não implementado

**Estado:** scaffold inicial focou em domínio (Cliente + Pet). JWT/bcrypt listados em `pyproject.toml` e configuráveis via `.env`, mas router `/auth/login` e middleware protegendo demais routers ainda não existem.
**Resolução esperada:** Milestone 2, antes do slice `agendamento`.

## TD-003 — Golden Example referencia código não existente

**Estado:** `judge/calibration/agendamento_concurrency_pass_001.json` criado no formato do Juiz devflow, mas `features/agendamento/` ainda não foi implementado. Calibração é válida como target — Juiz só roda o verdict quando slice existir.
**Resolução esperada:** Milestone 4 (slice agendamento).

## TD-004 — `core/db.py` + Alembic ainda não validados em runtime

**Estado:** `core/db.py` cria engine e sessionmaker. Alembic ainda não foi inicializado. Nenhuma tabela foi criada em DB real neste milestone — tests cobrem apenas Pydantic schemas.
**Resolução esperada:** Milestone 2 — `alembic init` + primeira migration com tabelas `cliente` e `pet`.
