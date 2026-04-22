# Knowledge Graph — ERP Pet Shop

**Modelo:** Vertical Slices. Nodes = features. Edges = chamadas de service público entre slices.
**Regra:** acíclico. Edge só existe se `features/X/service.py` importa `features/Y` (package root, nunca submódulo).

## Grafo atual (Milestone 1 — Cliente + Pet)

```
cliente ◄──── pet
```

Service layer ainda não implementado neste milestone; este slice entregou schemas + models apenas. Edge real aparece no Milestone 2.

## Grafo alvo (v1 completo)

```
auth ────────────┐
                 ▼
cliente ◄──── pet
   ▲            │
   │            ▼
   └────── agendamento ──► servico
               │
               ▼
           pagamento
```

## Edges planejadas

| De | Para | Via | Motivo |
|---|---|---|---|
| pet | cliente | `cliente.service.get_cliente_or_404` | validar tutor existe |
| agendamento | pet | `pet.service.get_pet_or_404` | validar pet existe |
| agendamento | cliente | `cliente.service.get_cliente_or_404` | validar cliente existe |
| agendamento | servico | `servico.service.get_servico_or_404` | snapshot de preço + ativo |
| pagamento | agendamento | `agendamento.service.get_agendamento_or_404` | validar status ∈ {PRONTO, ENTREGUE} |
| agendamento | pagamento | `pagamento.service.existe_para(agendamento_id)` | bloquear `PRONTO → ENTREGUE` sem pagamento |

## Regras de validação

- Imports inter-feature: `from erp_petshop.features.<y> import service` (package root). Import de `features.<y>.models` por outra feature = violação.
- Contrato `import-linter` em `pyproject.toml` (milestone 2).
- Script `scripts/check_graph.py` (milestone 2) parseia imports de `service.py` e falha em ciclo.
