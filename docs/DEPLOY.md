# Deploy DUNNAA — Produção

Domínios:

| Serviço | URL |
|---------|-----|
| API | `https://api.dunnaa.com.br` |
| Admin | `https://admin.dunnaa.com.br` |
| Site público | `https://dunnaa.com.br` (landing — a configurar) |

Stack: **Docker Compose** + **Traefik** (certresolver `cloudflare`) + **Postgres** + **Redis**.

---

## 1. No servidor (primeira vez)

```bash
# Clone
git clone https://github.com/innexardev/Dunnaa.git
cd Dunnaa/deploy

# Secrets locais (não vai pro Git)
cp .env.example .env
nano .env   # preencha POSTGRES_PASSWORD, SECRET_KEY, Stripe, etc.

# Build e subir
docker compose up -d --build

# Migrations (após postgres healthy)
docker compose exec api alembic upgrade head
```

Verifique:

- `https://api.dunnaa.com.br/health`
- `https://admin.dunnaa.com.br`

---

## 2. DNS (Cloudflare)

| Registro | Tipo | Destino |
|----------|------|---------|
| `api` | A / CNAME | IP do VPS ou proxy CF |
| `admin` | A / CNAME | idem |
| `@` / `www` | A / CNAME | site público |

Traefik usa `tls.certresolver=cloudflare` — configure o token DNS no Traefik (fora deste repo).

---

## 3. Secrets no GitHub (CI/CD)

**Nunca** commite `.env` com senhas. Use **GitHub → Settings → Secrets and variables → Actions**.

### Como criar

1. Abra `https://github.com/innexardev/Dunnaa/settings/secrets/actions`
2. **New repository secret** para cada item abaixo
3. Nome = exatamente como na tabela (case-sensitive)

### Secrets obrigatórios (deploy)

| Secret GitHub | O que é | Como gerar |
|---------------|---------|------------|
| `POSTGRES_PASSWORD` | Senha do banco | `openssl rand -base64 32` |
| `SECRET_KEY` | JWT da API | `openssl rand -hex 32` |
| `SSH_HOST` | IP ou hostname do VPS | ex: `123.45.67.89` |
| `SSH_USER` | Usuário SSH | ex: `root` ou `deploy` |
| `SSH_PRIVATE_KEY` | Chave privada SSH | `ssh-keygen -t ed25519` → conteúdo de `id_ed25519` |

### Secrets recomendados (produção)

| Secret | Uso |
|--------|-----|
| `STRIPE_SECRET_KEY` | Pagamentos live |
| `STRIPE_WEBHOOK_SECRET` | Webhook `https://api.dunnaa.com.br/api/v1/webhooks/stripe` |
| `SENTRY_DSN` | Erros em produção |
| `NVOIP_TOKEN` | SMS OTP |
| `S3_ACCESS_KEY` / `S3_SECRET_KEY` | Upload de imagens |

### SSH key — passo a passo

```bash
# Na sua máquina
ssh-keygen -t ed25519 -C "github-dunnaa-deploy" -f ~/.ssh/dunnaa_deploy

# No servidor: adicionar chave pública
cat dunnaa_deploy.pub >> ~/.ssh/authorized_keys

# No GitHub: Secret SSH_PRIVATE_KEY = conteúdo INTEIRO de dunnaa_deploy (privada)
```

---

## 4. Deploy manual vs GitHub Actions

### Manual (atual)

```bash
ssh user@servidor
cd /opt/Dunnaa && git pull
cd deploy && docker compose up -d --build
docker compose exec api alembic upgrade head
```

### Automático (opcional)

Crie `.github/workflows/deploy.yml` que:

1. Faz checkout
2. Usa `appleboy/ssh-action` com `SSH_HOST`, `SSH_USER`, `SSH_PRIVATE_KEY`
3. No servidor: escreve `.env` a partir dos secrets e roda `docker compose up -d --build`

Exemplo de montagem do `.env` no workflow:

```yaml
env:
  POSTGRES_PASSWORD: ${{ secrets.POSTGRES_PASSWORD }}
  SECRET_KEY: ${{ secrets.SECRET_KEY }}
```

---

## 5. Traefik — headers importantes

O compose já usa:

- `CF-Connecting-IP` no rate limit do Traefik (Cloudflare)
- `passHostHeader=true` nos services

A API lê `X-Forwarded-For` para rate limit interno. Com Cloudflare + Traefik, o IP real costuma chegar via headers encadeados.

Webhook Stripe: configure no dashboard Stripe a URL:

```
https://api.dunnaa.com.br/api/v1/webhooks/stripe
```

---

## 6. CORS

No `docker-compose.yml`:

```yaml
CORS_ORIGINS: '["https://admin.dunnaa.com.br","https://dunnaa.com.br"]'
```

Quando o app mobile/web cliente usar a API, adicione a origem correspondente.

---

## 7. Checklist pós-deploy

- [ ] `GET /health` → 200
- [ ] `GET /ready` → 200
- [ ] Login admin via SMS (OTP)
- [ ] Migrations aplicadas
- [ ] Stripe webhook test mode → live
- [ ] Backup Postgres (`pg_dump` cron)
