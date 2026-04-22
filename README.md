# ERP Pet Shop

MVP de ERP para banho e tosa — arquitetura Vertical Slices, FastAPI async, SQLite, governança via devflow L4 (bridge mode).

## Como rodar

```bash
uv sync
uv run pytest
```

## Estrutura

- `src/erp_petshop/core/` — infra cross-cutting (db, config, security, errors)
- `src/erp_petshop/features/<slice>/` — um slice por contexto de negócio
- `tests/features/<slice>/` — testes espelhando slice
- `docs/knowledge_graph.md` — grafo de dependências entre features
- `docs/tech_debt.md` — débito técnico aceito
- `docs/superpowers/specs/` — design docs versionados
- `judge/calibration/` — golden examples para o Juiz do devflow

## Gates

Shadow Runner + Paperweight Bridge do devflow. Ver `PRODUCT_VISION.md` para o fluxo alvo.
