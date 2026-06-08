# DUNNAA

> 💈 Sistema de agendamento e assinaturas para barbearias e salões  
> 🌐 [dunnaa.com.br](https://dunnaa.com.br)

## 📱 Apps

- **DUNNAA** - App para clientes (React Native/Expo)
- **DUNNAA Pro** - App para barbeiros (React Native/Expo)
- **Admin** - Painel administrativo (Next.js)

## 🏗️ Arquitetura

```
dunnaa/
├── apps/
│   ├── cliente/          # App Cliente (Expo)
│   ├── barbeiro/         # App Barbeiro (Expo)
│   └── admin/            # Painel Admin (Next.js)
├── packages/
│   ├── api/              # Backend (FastAPI)
│   ├── database/         # Models + Migrations
│   └── shared/           # Tipos compartilhados
├── docs/                 # Documentação
└── docker-compose.yml    # Dev environment
```

## 🚀 Quick Start

### Pré-requisitos

- Node.js 20+
- Python 3.12+
- Docker & Docker Compose
- pnpm

### Instalação

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/dunnaa.git
cd dunnaa

# Instale dependências
pnpm install

# Inicie banco de dados
docker-compose up -d

# Rode migrations
cd packages/api
alembic upgrade head

# Inicie o backend
pnpm dev:api

# Inicie os apps (em outro terminal)
pnpm dev:cliente
pnpm dev:barbeiro
pnpm dev:admin
```

## 📚 Documentação

- [**Blueprint do Projeto**](docs/BLUEPRINT.md) — visão, produto, roadmap e estado atual
- [Arquitetura](docs/ARCHITECTURE.md)
- [Features](docs/FEATURES.md)
- [Banco de Dados](docs/DATABASE.md)
- [API Reference](docs/API.md)
- [Plano de Implementação](docs/IMPLEMENTATION_PLAN.md)

## 💰 Modelo de Negócio

### Mensalidade
| Porte | Valor |
|-------|-------|
| Pequeno | R$ 29/mês |
| Médio/Grande | R$ 49/mês |

### Comissões
| Tipo | Taxa |
|------|------|
| Avulso | 8% |
| Assinatura | 6% |

## 🛠️ Stack

| Componente | Tecnologia |
|------------|------------|
| Mobile | React Native + Expo |
| Web Admin | Next.js 15 |
| Backend | FastAPI (Python) |
| Database | PostgreSQL |
| Cache | Redis |
| Pagamentos | Stripe |
| Deploy | Railway + Vercel |

## 📝 License

Proprietary - All rights reserved.
