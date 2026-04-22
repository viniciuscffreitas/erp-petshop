# ERP Pet Shop — MVP Design (Banho e Tosa)

**Data:** 2026-04-22
**Status:** aprovado, Milestone 1 em execução
**Autoria:** Claude (L4 interactive) sob governança devflow em bridge mode (shadow_run.sh + paperweight_bridge.py via bash)

## Contexto

Vision (`PRODUCT_VISION.md`): digitalizar o fluxo de banho e tosa de um pet shop pequeno. Operadora principal = mãe do user. UX mobile-first (tablet/celular). Regra de ouro: simplicidade total.

## Decisões de escopo (Q&A do brainstorming)

| # | Pergunta | Resposta |
|---|---|---|
| 1 | Modelo de acesso | Single-tenant multi-user (2-3 operadores com login) |
| 2 | Escopo financeiro | Preço por serviço + registro de pagamento (método + data). Sem pagamento parcial. |
| 3 | Regra de concorrência | Slot fixo de 30min, 1 agendamento por slot |
| 4 | Máquina de estados | `AGENDADO → EM_BANHO → PRONTO → ENTREGUE` + `CANCELADO` terminal. `NAO_COMPARECEU` vira TD-001 (v2). |
| 5 | Surface v1 | API-only (FastAPI + OpenAPI + pytest). UI em ciclo separado. |

## Arquitetura — Vertical Slices

**Racional:** Context Engineering. Locality of Behavior. Token budget por feature > DRY tradicional. Tudo sobre um contexto de negócio (ex: agendamento) vive em uma pasta.

```
src/erp_petshop/
├── core/                       # infra cross-cutting mínima
│   ├── db.py                   # Base, engine async, sessionmaker
│   ├── config.py               # Settings (pydantic-settings)
│   └── errors.py               # BusinessError, NotFoundError, ConflictError
└── features/
    ├── cliente/
    ├── pet/
    ├── servico/                # milestone 3
    ├── agendamento/            # milestone 4 (coração)
    ├── pagamento/              # milestone 3
    └── auth/                   # milestone 2
```

Cada slice tem: `models.py`, `schemas.py`, `repo.py`, `service.py`, `router.py`, `enums.py` (quando aplicável), `__init__.py` re-exportando service como API pública.

### Regras duras (enforced)

| Regra | Implementação |
|---|---|
| Import inter-feature só via `__init__.py` público | `import-linter` contract (Milestone 2) |
| Schemas nunca compartilhados | Duplicação literal entre slices |
| Models nunca atravessam em Python | FK SQL permitida (string nome de tabela); import de classe Model de outra feature proibido |
| `core/` só infra, sem regra de negócio | Revisão manual. Teste: remover `features/*` deixa `core/` sem sentido de negócio. |
| Testes dentro do slice | `tests/features/<slice>/` espelha `src/features/<slice>/` |

### Comunicação entre features

Síncrona via chamada de service público — `agendamento.service::criar_agendamento` chama `pet.service::get_pet_or_404`. Eventos ficam para quando notificações/webhooks entrarem (v2).

### FK cross-feature

Permitida no SQL (`ForeignKey("cliente.id")` por string de nome de tabela). Proibido importar classe Model de outra feature em Python. Invariante referencial garantida pelo DB.

## Dados por slice

### Cliente

| Campo | Tipo | Constraint |
|---|---|---|
| id | UUID | pk, default uuid4 |
| nome | str | 1..100 |
| telefone | str? | regex `^\+?\d{8,20}$` |
| email | EmailStr? | — |
| observacoes | str? | 0..1000 |
| created_at, updated_at | datetime tz | server_default now |

**Invariante:** `telefone OR email` obrigatório (Pydantic `model_validator`).

### Pet (lean v1)

| Campo | Tipo | Constraint |
|---|---|---|
| id | UUID | pk |
| nome | str | 1..60 |
| especie | Enum {CAO, GATO} | — |
| raca | str? | 0..80 |
| observacoes | str? | 0..1000 |
| cliente_id | UUID | FK `cliente.id` ON DELETE RESTRICT |
| created_at, updated_at | datetime tz | server_default now |

**Invariantes:**
- `cliente_id` NOT NULL, FK RESTRICT → cliente com pets não pode ser deletado (409).
- Criar pet com `cliente_id` inexistente → 404 (via `pet.service` chamando `cliente.service.get_cliente_or_404`).
- Campos removidos de v1: `peso_kg`, `porte`, `data_nascimento`. Motivo: YAGNI. devflow cuida da migração quando v2 precisar.

### Servico (Milestone 3)

| Campo | Tipo | Constraint |
|---|---|---|
| id | UUID | pk |
| nome | str | unique, 1..80 |
| preco_cents | int | >= 0 |
| ativo | bool | default true |

Seed inicial: `Banho`, `Tosa`, `Banho+Tosa`.

### Agendamento (Milestone 4 — coração)

| Campo | Tipo | Constraint |
|---|---|---|
| id | UUID | pk |
| pet_id | UUID | FK RESTRICT |
| cliente_id | UUID | FK RESTRICT |
| servico_id | UUID | FK RESTRICT |
| slot_inicio | datetime tz | alinhado 30min |
| status | Enum (5) | `AGENDADO, EM_BANHO, PRONTO, ENTREGUE, CANCELADO` |
| preco_cents | int | snapshot do Servico |
| observacoes | str? | 0..1000 |

**Index:** partial unique `(slot_inicio) WHERE status != 'cancelado'` — libera slot ao cancelar.

**Regras puras em `agendamento/`:**
- `scheduler.normaliza_slot(dt)`: rejeita se `tzinfo is None`, minuto não múltiplo de 30, segundos ou microssegundos não-zero.
- `scheduler.valida_nao_retroativo(slot, agora)`: rejeita se `slot < agora - 5min`.
- `state_machine.TRANSICOES`: dict `{AGENDADO: {EM_BANHO, CANCELADO}, EM_BANHO: {PRONTO}, PRONTO: {ENTREGUE}, ENTREGUE: {}, CANCELADO: {}}`.
- `state_machine.proxima(origem, destino)`: enforcement.

### Pagamento (Milestone 3)

| Campo | Tipo | Constraint |
|---|---|---|
| id | UUID | pk |
| agendamento_id | UUID | FK RESTRICT, **unique** (1:1) |
| valor_cents | int | > 0 |
| metodo | Enum | `PIX, DINHEIRO, CARTAO_DEBITO, CARTAO_CREDITO, LINK` |
| pago_em | datetime tz | obrigatório |
| observacoes | str? | 0..500 |

**Regra:** só agendamentos em `PRONTO` ou `ENTREGUE` aceitam pagamento. `PRONTO → ENTREGUE` exige Pagamento existir.

## Concorrência — defense in depth (3 camadas)

1. **Normalização pura** (`scheduler.normaliza_slot`): rejeita slot desalinhado antes de qualquer I/O.
2. **Check pré-insert** (`repo.slot_ocupado(session, slot)` filtra `status != CANCELADO`): rejeita slot já ocupado.
3. **Partial unique index no DB**: última defesa contra race — duas requests concorrentes que passam do step 2; a perdedora levanta `IntegrityError` traduzido para `SlotOcupadoError`.

Golden Example `judge/calibration/agendamento_concurrency_pass_001.json` valida esse padrão. Futuro `agendamento_concurrency_fail_001.json` calibra o Juiz para detectar implementação sem partial index (não libera CANCELADO).

## Gate operacional (devflow L4 bridge)

- **Shadow Runner:** `bash ~/Developer/devflow/scripts/shadow_run.sh /Users/vini/Developer/erp-petshop <SESSION_ID>`. Env `SHADOW_TEST_CMD="uv run pytest -x -q"`.
- **Paperweight Bridge:** `cd ~/Developer/devflow && echo '{"state_dir":"~/.claude/devflow/state/<sess>","session_id":"<sess>","project_root":"/Users/vini/Developer/erp-petshop"}' | python3 -m hooks.paperweight_bridge`.
- **Regra de ouro:** nenhum commit tratado como "pronto" até `apply_devflow_governance` retornar `ready_to_push: true`.

## Milestones

1. **Milestone 1** (este commit): scaffold + `core/` + slices `cliente` e `pet` com schemas e models. Testes 100% do domínio (validators Pydantic).
2. **Milestone 2:** slice `auth` (JWT + bcrypt + router). Alembic `0001_initial` com tabelas Cliente e Pet. Import-linter contract ativo.
3. **Milestone 3:** slices `servico` + `pagamento`. Alembic `0002`.
4. **Milestone 4 (coração):** slice `agendamento`. Scheduler + state machine + partial unique index + Golden Example validado pelo Juiz. Alembic `0003`.
5. **Milestone 5:** router tests com httpx + integration tests contra SQLite temp. Shadow rodando suite completa. `ready_to_push: true` consolidado.

## Débito aceito

Ver `docs/tech_debt.md` — TD-001 a TD-004.
