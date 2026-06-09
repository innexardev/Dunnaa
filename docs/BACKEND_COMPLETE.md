# Backend Completo — DUNNAA

Plano e status para backend **production-ready** com ~90% cobertura de testes e documentação sincronizada com o código.

**Escopo:** `packages/api`  
**Meta CI:** `--cov-fail-under=90`  
**Última atualização:** 2026-06-08

---

## Status geral

| Área | Status | Notas |
|------|--------|-------|
| Auth SMS + JWT | ✅ | OTP Redis + rate limit; SMS nVoIP em produção |
| Estabelecimentos + serviços + staff | ✅ | Inclui service↔staff linking |
| Agendamentos + fila + check-in | ✅ | RBAC reforçado em list/no-show |
| Pagamentos + wallet + payouts | ✅ | Webhooks Stripe/MP |
| Assinaturas (cliente + owner) | ✅ | Créditos no check-in |
| Reviews, favoritos, portfolio | ✅ | |
| Produtos, bundles, promoções | ✅ | Promoções CRUD (novo) |
| Referrals | ✅ | Ledger + claim (novo) |
| Analytics + admin | ✅ | |
| Admin settings | ✅ | |
| Testes | ✅ ~90% meta CI | 60+ arquivos de teste |
| Docs API/DB/FEATURES | ✅ | Sincronizado com MVP 2.0 |
| Plugins/Ads API | ✅ | CRUD + search boost |
| Google Reviews sync | ✅ | approve + send (mock Places) |
| Auto no-show scheduler | ✅ | Job a cada hora (:30) |
| Stripe billing recorrente | ⏳ | Criação local; webhook parcial |

---

## Entregas desta fase

### Fundação técnica
- [x] `app/config.py` → shim para `app/core/config.py`
- [x] Imports legados migrados (`payment_service`, `stripe_p`, `auth_service`)
- [x] RBAC: `GET /appointments/establishments/{id}` e `POST .../no-show`
- [x] OTP: limite de 5 tentativas (Redis + fallback memória)
- [x] SMS produção via `SMSService` (nVoIP)
- [x] Remoção model legado `app/models/checkin.py`

### Features MVP 1.1
- [x] Tabela + API **referrals** (`GET /referrals/me`, `POST /referrals/{id}/claim`)
- [x] Tabela + API **promotions** (CRUD em `/establishments/{id}/promotions`)
- [x] **Service-staff** (`GET/PUT .../services/{id}/staff`)
- [x] Migration `f7a8b9c0d1e2_add_promotions_referrals`

### Testes adicionados
- `test_payouts`, `test_analytics`, `test_admin_settings`, `test_rbac_http`
- `test_promotions`, `test_referrals`, `test_service_staff`
- Services: `otp`, `payout`, `analytics`, `referral`, `promotion`, `wallet`, `settings`, `checkin`, `subscription`

### Documentação
- [x] `docs/API.md` — referência completa (~100 endpoints)
- [x] Este plano (`BACKEND_COMPLETE.md`)
- [ ] `docs/DATABASE.md` — sync referrals/promotions (parcial)
- [ ] `docs/FEATURES.md` — marcar implementado vs pendente

---

## Roadmap restante (→ 90% + prod)

### P1 — Cobertura 90% ✅ (em progresso)
1. ~~Testes HTTP: webhooks Stripe/MP, tips, notifications read-all~~ ✅
2. ~~Testes services: payment, queue, search, notification, establishment, audit~~ ✅
3. RBAC matrix completa (staff role vinculado a `StaffMember.user_id`)
4. CI `--cov-fail-under=90` ✅ configurado

### P2 — MVP 1.1 restante
5. Auto no-show (scheduler job)
6. Queue ETA notification
7. Tips via Stripe PaymentIntent
8. Google review approve + sync

### P3 — MVP 2.0
9. ~~Plugins + Ad campaigns API~~ ✅
10. ~~Google review approve + sync~~ ✅
11. ~~Auto no-show scheduler~~ ✅
12. Analytics export (PDF/Excel)
13. Redis rate limiting multi-instância
14. Audit trail em mutações sensíveis

---

## Comandos

```bash
# Subir infra
docker compose up -d

# Migrations
cd packages/api && alembic upgrade head

# Testes + cobertura
cd packages/api && pytest tests/ -v --cov=app --cov-report=term-missing --cov-fail-under=70

# Lint
cd packages/api && ruff check . && ruff format --check .
```

---

## Matriz RBAC (resumo)

| Recurso | Customer | Staff | Owner | Admin |
|---------|----------|-------|-------|-------|
| Agendamentos próprios | ✅ | ✅ | ✅ | ✅ |
| Lista agendamentos estab. | ❌ | ✅ | ✅ | ✅ |
| Payouts / Analytics | ❌ | ❌ | ✅ | ✅ |
| CRUD serviços/staff | ❌ | ❌ | ✅ | ✅ |
| Admin `/admin/*` | ❌ | ❌ | ❌ | ✅ |
| Promoções (write) | ❌ | ❌ | ✅ | ✅ |
| Promoções (read) | ✅ público | ✅ | ✅ | ✅ |
