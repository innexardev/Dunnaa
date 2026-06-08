# Cursor — Configuração DUNNAA

Configuração de agentes, rules, skills e commands adaptada ao monorepo **DUNNAA** ([dunnaa.com.br](https://dunnaa.com.br)).

Inspirado em [cursor-handbook](https://github.com/girijashankarj/cursor-handbook), customizado para FastAPI + Expo + Next.js.

## Marca

| Item | Valor |
|------|-------|
| App | **DUNNAA** / **DUNNAA Pro** |
| Domínio | **dunnaa.com.br** |
| API | `https://api.dunnaa.com.br/api/v1` |
| Packages | `@dunnaa/*` |

## Estrutura

```
.cursor/
├── agents/          # Subagentes especializados
├── commands/        # Comandos rápidos (/dev-api, /new-endpoint)
├── rules/           # Regras .mdc por stack e domínio
└── skills/          # Workflows detalhados
```

## Agents Disponíveis

| Agent | Quando usar |
|-------|-------------|
| `backend-api` | Criar/revisar endpoints FastAPI |
| `backend-reviewer` | Code review do backend |
| `backend-debugger` | Falhas de teste, bugs async/SQLAlchemy |
| `migration` | Alembic migrations e alterações de schema |
| `expo-mobile` | Apps cliente e barbeiro (React Native) |
| `nextjs-admin` | Painel admin Next.js |
| `frontend-scaffold` | Criar apps que ainda não existem |

## Como Usar

1. **Rules** aplicam automaticamente conforme glob patterns
2. **Agents**: mencione `@backend-api`
3. **Skills**: peça "siga a skill create-api-endpoint"
4. **Commands**: digite `/dev-api` no chat do Agent
