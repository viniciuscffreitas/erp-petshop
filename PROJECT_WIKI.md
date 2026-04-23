# PROJECT_WIKI — ERP Pet Shop

## Motor oficial de validação: Shadow Runner V3 (Docker-Hermetic)

A partir de 2026-04-23, o **Shadow Runner V3** (repo
[`devflow-shadow-runner`](https://github.com/viniciuscffreitas/devflow-shadow-runner),
tag `main@9c2929e`) é o motor **oficial** de validação do ERP Pet Shop.
Ele substitui o shadow path V1 (`scripts/shadow_run.sh` + rsync + host
toolchain) sempre que `sandbox.yaml` + `sandbox.lock.yaml` estiverem
presentes na raiz do projeto.

### Contrato

- **Hermético**: runner executa em container Docker com `--internal`
  network. DNS e TCP externos bloqueados; apenas sidecars declarados
  são alcançáveis.
- **Imutável**: imagens pinadas por `sha256:<digest>` no
  `sandbox.lock.yaml`, resolvido por arch via `devflow_sandbox lock`.
- **Auto-curativo**: `devflow_sandbox heal` invoca `claude -p` para
  propor patches em cópia de workspace isolada — arquivos originais
  permanecem intocados.
- **Forense**: runs curados emitem `shadow_audit` signals (log-only).
  `post_task_judge` drena para `state/<session>/shadow_audit.jsonl`
  sem afetar o rubric de scoring (Lean Juan Model).

### Bridge DevFlow → V3

Implementada em [`devflow`](https://github.com/viniciuscffreitas/devflow)
(`main@ab6675f`) via `hooks/shadow_runner.py`. Detecta manifesto V3 e
despacha via `DEVFLOW_SANDBOX_CMD` → `shutil.which("devflow_sandbox")`
→ `python -m devflow_sandbox`. Fallback V1 emite aviso explícito
("Model Empathy") quando o CLI V3 não é resolvível.

### Comandos principais

```bash
# Pinar digests (execute uma vez, commit o .lock.yaml)
devflow_sandbox lock \
  --config sandbox.yaml \
  --output sandbox.lock.yaml \
  --image runner=python:3.12-slim

# Rodar validação hermética
devflow_sandbox test \
  --config sandbox.yaml \
  --lock sandbox.lock.yaml \
  --source src --source tests \
  --wiki docs/wiki \
  --artifacts out
```

### Prova de fogo (2026-04-23)

| Gate | Resultado |
|------|-----------|
| M4 lock real (Docker) | `alpine@sha256:6baf4358…` pinado |
| Docker-marked tests | 7/7 PASS |
| Claude `claude -p` E2E heal | PASS (13s, healed=True) |
| Bridge end-to-end (real digest em signal) | PASS |
| Forensic `shadow_audit.jsonl` schema + idempotência | PASS |
| Lint (ruff) + types (mypy) | ✓ |
| Pytest suite shadow-runner | 206 passed, 1 skipped |
| Pytest bridge + audit consumer devflow | 17/17 passed |

### Observações

- Pet Shop ainda não possui `sandbox.yaml`. Enquanto estiver ausente,
  o bridge usa o path V1 por compatibilidade. Pipe de migração para
  V3 é trabalho separado.
- `docs/knowledge_graph.md` e `docs/tech_debt.md` continuam fontes de
  verdade para dependências e débito. Este wiki documenta apenas o
  contrato de validação.
