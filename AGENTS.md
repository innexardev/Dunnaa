# AGENTS.md — Instruções para Agentes AI

> Sistema de agendamento e assinaturas para barbearias e salões.

## Marca

| Item | Valor |
|------|-------|
| App cliente | **DUNNAA** |
| App profissional | **DUNNAA Pro** |
| Domínio | **dunnaa.com.br** |
| API produção | `https://api.dunnaa.com.br/api/v1` |
| Admin | `https://admin.dunnaa.com.br` |
| Packages npm | `@dunnaa/*` |

## Visão Geral

**DUNNAA** é um monorepo Turborepo + pnpm com:

| Pacote | Stack | Status |
|--------|-------|--------|
| `packages/api` | FastAPI + SQLAlchemy async + PostgreSQL + Redis | Implementado (~90%) |
| `apps/cliente` | React Native / Expo | A criar |
| `apps/barbeiro` | React Native / Expo (DUNNAA Pro) | A criar |
| `apps/admin` | Next.js 15 | Implementado |
| `packages/shared` | Tipos TypeScript compartilhados | Implementado |

Documentação principal: `docs/BLUEPRINT.md`, `docs/ARCHITECTURE.md`, `docs/API.md`, `docs/DATABASE.md`, `docs/FEATURES.md`, `docs/BACKEND_REVIEW.md`.

## Princípios Críticos

### 1. Idioma e Domínio

- Mensagens de API e docs em **português (BR)**
- Domínio: agendamentos, fila virtual, assinaturas, pagamentos (Stripe + Mercado Pago), check-in QR, comissões (8% avulso / 6% assinatura)
- Roles: `customer`, `owner`, `staff`, `admin`

### 2. Arquitetura Backend

```
Routes (app/api/v1/*.py)
  → Services (app/services/*.py)   # lógica + queries SQLAlchemy
  → Models (app/models/*.py)
  → Schemas (app/schemas/*.py)     # Pydantic v2
```

- Usar **`app/api/deps.py`** e **`app/core/config.py`** (fontes canônicas)
- Evitar `app/dependencies.py` e `app/config.py` (legado — migrar quando tocar)
- Exceções via `AppException` (`UnauthorizedError`, `ForbiddenError`, etc.), não `HTTPException` genérico em código novo
- Pagamentos: factory pattern em `app/services/payment_providers/`

### 3. Segurança

- Nunca commitar `.env`, chaves Stripe, tokens SMS
- OTP deve ir para Redis (não memória) — ver `docs/BACKEND_REVIEW.md`
- RBAC por estabelecimento: owner, admin ou staff ativo vinculado
- Validar acesso com `verify_establishment_access` em endpoints sensíveis

### 4. Desenvolvimento Local

```bash
docker-compose up -d              # Postgres 16 (5455) + Redis (6385)
cd packages/api && alembic upgrade head
pnpm dev:api                      # uvicorn com reload
```

Testes (em `packages/api`):

```bash
pytest tests/ -v                  # suite completa
ruff check . && ruff format --check .
```

### 5. Escopo de Mudanças

- Mudanças mínimas e focadas — não refatorar código não relacionado
- Ao criar endpoints: route + schema + service + teste
- Ao alterar schema: model + migration Alembic + atualizar `docs/API.md` se contrato mudar
- Frontend ainda não existe — ao scaffoldar apps, seguir monorepo pnpm e consumir `docs/API.md`

## Mapa de Componentes Cursor

| Tipo | Local | Uso |
|------|-------|-----|
| Rules | `.cursor/rules/*.mdc` | Padrões por stack/domínio |
| Agents | `.cursor/agents/*.md` | Subagentes especializados |
| Skills | `.cursor/skills/*/SKILL.md` | Workflows passo a passo |
| Commands | `.cursor/commands/*.md` | Ações rápidas via `/` |

## Dívida Técnica Conhecida

Consultar `docs/BACKEND_REVIEW.md` antes de alterar auth, RBAC ou config:

1. Config duplicada (`app/config.py` vs `app/core/config.py`)
2. Deps duplicadas (`dependencies.py` vs `api/deps.py`)
3. OTP em memória (precisa Redis)
4. Alguns routes ainda owner-only onde staff deveria ter acesso
