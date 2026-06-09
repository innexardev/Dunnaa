# DUNNAA — API Reference (Completa)

**Base URL:** `https://api.dunnaa.com.br/api/v1`  
**Swagger:** `/docs` (dev)  
**Site:** [dunnaa.com.br](https://dunnaa.com.br)

---

## Convenções

### Autenticação

Rotas protegidas exigem:

```
Authorization: Bearer <access_token>
```

### Respostas de erro

```json
{
  "detail": {
    "code": "FORBIDDEN",
    "message": "Sem permissão para esta ação"
  }
}
```

Códigos comuns: `UNAUTHORIZED`, `FORBIDDEN`, `NOT_FOUND`, `VALIDATION_ERROR`, `PAYMENT_ERROR`, `CHECKIN_ERROR`, `AVAILABILITY_ERROR`, `SMS_ERROR`.

### Paginação (listas admin/geo)

```json
{
  "items": [],
  "total": 0,
  "page": 1,
  "page_size": 20
}
```

---

## Health (raiz, sem prefixo `/api/v1`)

| Método | Path | Auth | Descrição |
|--------|------|------|-----------|
| GET | `/health` | — | Liveness |
| GET | `/ready` | — | Readiness (DB + Redis) |
| GET | `/metrics` | — | Métricas Prometheus |

---

## Auth — `/auth`

| Método | Path | Auth | Descrição |
|--------|------|------|-----------|
| POST | `/auth/send-code` | — | Envia OTP SMS |
| POST | `/auth/verify` | — | Verifica OTP, retorna tokens + user |
| POST | `/auth/refresh` | — | Renova access token |

**POST /auth/send-code**

```json
{ "phone": "+5511999999999" }
```

Resposta: `{ "message": "...", "expires_in_seconds": 300 }`  
Em `ENVIRONMENT=development`, o código aparece na mensagem.

**POST /auth/verify**

```json
{
  "phone": "+5511999999999",
  "code": "123456",
  "name": "João",
  "email": "joao@email.com",
  "referral_code": "ABC12345"
}
```

Resposta:

```json
{
  "tokens": {
    "access_token": "eyJ...",
    "refresh_token": "eyJ...",
    "token_type": "bearer",
    "expires_in": 1800
  },
  "user": {
    "id": "uuid",
    "phone": "+5511999999999",
    "name": "João",
    "email": null,
    "avatar_url": null,
    "role": "customer",
    "referral_code": "XYZ98765",
    "referred_by_id": "uuid-or-null"
  }
}
```

---

## Users — `/users`

| Método | Path | Auth | Descrição |
|--------|------|------|-----------|
| GET | `/users/me` | ✅ | Perfil autenticado |
| PATCH | `/users/me` | ✅ | Atualiza perfil |
| GET | `/users` | Admin | Lista usuários |

**Search history** — `/users/me/search-history`

| Método | Path | Descrição |
|--------|------|-----------|
| GET | `/users/me/search-history` | Histórico de buscas |
| POST | `/users/me/search-history` | Registra busca |
| DELETE | `/users/me/search-history/{entry_id}` | Remove entrada |
| DELETE | `/users/me/search-history` | Limpa histórico |

---

## Establishments — `/establishments`

| Método | Path | Auth | Descrição |
|--------|------|------|-----------|
| POST | `/establishments` | Owner | Cria estabelecimento |
| GET | `/establishments` | — | Lista pública (geo, categoria) |
| GET | `/establishments/my` | Owner | Meus estabelecimentos |
| GET | `/establishments/{id}` | — | Detalhe |
| GET | `/establishments/slug/{slug}` | — | Por slug |
| PATCH | `/establishments/{id}` | Owner | Atualiza |
| DELETE | `/establishments/{id}` | Owner | Remove |

Query params em `GET /establishments`: `page`, `page_size`, `category`, `lat`, `lng`, `radius`, `city`, `search`.

---

## Services — `/establishments/{id}/services`

| Método | Path | Auth | Descrição |
|--------|------|------|-----------|
| GET | `.../services` | — | Lista serviços |
| POST | `.../services` | Owner | Cria |
| GET | `.../services/{service_id}` | — | Detalhe |
| PATCH | `.../services/{service_id}` | Owner | Atualiza |
| DELETE | `.../services/{service_id}` | Owner | Soft delete |
| GET | `.../services/{service_id}/staff` | — | Staff vinculados |
| PUT | `.../services/{service_id}/staff` | Owner | Atribui staff (`staff_ids[]`) |

---

## Staff — `/establishments/{id}/staff`

| Método | Path | Auth | Descrição |
|--------|------|------|-----------|
| GET | `.../staff` | — | Lista |
| POST | `.../staff` | Owner | Cria |
| GET | `.../staff/{staff_id}` | — | Detalhe |
| PATCH | `.../staff/{staff_id}` | Owner | Atualiza |
| DELETE | `.../staff/{staff_id}` | Owner | Desativa |
| POST | `.../staff/{staff_id}/blocks` | Owner | Bloqueio de agenda |
| GET | `.../staff/{staff_id}/blocks` | Owner | Lista bloqueios |

---

## Availability — `/establishments/{id}/staff/{staff_id}/availability`

| Método | Path | Descrição |
|--------|------|-----------|
| GET | `.../availability?service_id=&date=` | Slots disponíveis |

---

## Appointments — `/appointments`

| Método | Path | Auth | Descrição |
|--------|------|------|-----------|
| GET | `/appointments` | ✅ | Meus agendamentos |
| GET | `/appointments/establishments/{id}` | Owner/Staff | Agenda do estabelecimento |
| POST | `/appointments` | ✅ | Cria agendamento |
| PATCH | `/appointments/{id}` | ✅ | Atualiza status |
| DELETE | `/appointments/{id}` | ✅ | Cancela |
| POST | `/appointments/{id}/no-show` | Owner/Staff | Marca no-show |

---

## Queue — `/queue`

| Método | Path | Auth | Descrição |
|--------|------|------|-----------|
| POST | `/queue` | ✅ | Entra na fila |
| GET | `/queue/my` | ✅ | Minha posição |
| GET | `/queue/establishments/{id}` | Owner/Staff | Fila do estabelecimento |
| PATCH | `/queue/{entry_id}/status` | Owner/Staff | Atualiza status |
| DELETE | `/queue/{entry_id}` | ✅ | Sai da fila |

---

## Check-ins — `/checkins`

| Método | Path | Auth | Descrição |
|--------|------|------|-----------|
| GET | `/checkins/establishments/{id}/qr` | Owner/Staff | QR JWT + imagem base64 |
| POST | `/checkins` | ✅ | Check-in via token QR |

Check-in consome créditos de assinatura quando aplicável.

---

## Subscription plans (owner) — `/establishments/{id}/subscription-plans`

| Método | Path | Auth | Descrição |
|--------|------|------|-----------|
| GET | `.../subscription-plans` | — | Lista planos |
| POST | `.../subscription-plans` | Owner | Cria plano |
| PATCH | `.../subscription-plans/{plan_id}` | Owner | Atualiza |

**Owner subscribers:** `GET /establishments/{id}/subscriptions`

---

## Customer subscriptions — `/subscriptions`

| Método | Path | Auth | Descrição |
|--------|------|------|-----------|
| GET | `/subscriptions` | ✅ | Minhas assinaturas |
| GET | `/subscriptions/{id}` | ✅ | Detalhe + uso |
| POST | `/subscriptions` | ✅ | Assina plano |
| DELETE | `/subscriptions/{id}` | ✅ | Cancela |

---

## Promotions — `/establishments/{id}/promotions`

| Método | Path | Auth | Descrição |
|--------|------|------|-----------|
| GET | `.../promotions` | — | Lista ativas (público) |
| POST | `.../promotions` | Owner | Cria promoção |
| PATCH | `.../promotions/{promotion_id}` | Owner | Atualiza |
| DELETE | `.../promotions/{promotion_id}` | Owner | Desativa |

Campos: `title`, `description`, `discount_type` (`percent`|`fixed`), `discount_value`, `service_id`, `bundle_id`, `start_date`, `end_date`.

---

## Referrals — `/referrals`

| Método | Path | Auth | Descrição |
|--------|------|------|-----------|
| GET | `/referrals/me` | ✅ | Indicações + stats |
| POST | `/referrals/{id}/claim` | ✅ | Resgata recompensa |

Criado automaticamente no signup com `referral_code` válido.

---

## Products — `/establishments/{id}/products`

CRUD completo: GET list, POST, GET `{id}`, PATCH, DELETE.

---

## Bundles — `/establishments/{id}/bundles`

CRUD completo de combos de serviços.

---

## Reviews — `/reviews`

| Método | Path | Auth | Descrição |
|--------|------|------|-----------|
| POST | `/reviews` | ✅ | Cria avaliação |
| GET | `/reviews/establishments/{id}` | — | Lista do estabelecimento |
| GET | `/reviews/my` | ✅ | Minhas avaliações |
| PATCH | `/reviews/{id}` | ✅ | Edita |
| PATCH | `/reviews/{id}/respond` | Owner | Resposta do estabelecimento |

---

## Favorites — `/favorites`

| Método | Path | Descrição |
|--------|------|-----------|
| POST | `/favorites/establishments` | Toggle favorito estabelecimento |
| POST | `/favorites/staff` | Toggle favorito profissional |
| GET | `/favorites` | Lista favoritos |

---

## Portfolio — `/portfolio`

| Método | Path | Descrição |
|--------|------|-----------|
| POST | `/portfolio` | Upload imagem |
| DELETE | `/portfolio/{image_id}` | Remove |
| GET | `/portfolio/establishments/{id}` | Galeria do estabelecimento |
| GET | `/portfolio/staff/{staff_id}` | Galeria do profissional |

---

## Notifications — `/notifications`

| Método | Path | Descrição |
|--------|------|-----------|
| GET | `/notifications` | Lista |
| PATCH | `/notifications/{id}/read` | Marca lida |
| PATCH | `/notifications/read-all` | Marca todas |

---

## Tips — `/tips`

| Método | Path | Descrição |
|--------|------|-----------|
| POST | `/tips/` | Envia gorjeta |
| GET | `/tips/me` | Minhas gorjetas |

---

## Payments — `/payments`

| Método | Path | Auth | Descrição |
|--------|------|------|-----------|
| GET | `/payments` | ✅ | Meus pagamentos |
| GET | `/payments/establishments/{id}` | Owner | Pagamentos do estabelecimento |
| POST | `/payments/create-intent` | ✅ | Stripe PaymentIntent |
| GET | `/payments/wallet` | ✅ | Saldo carteira |
| GET | `/payments/wallet/transactions` | ✅ | Extrato |
| POST | `/payments/webhooks/stripe` | — | Webhook Stripe |
| POST | `/payments/webhooks/mercadopago` | — | Webhook Mercado Pago |

Taxas plataforma: 8% avulso, 6% assinatura (configurável via env).

---

## Payouts — `/payouts`

| Método | Path | Auth | Descrição |
|--------|------|------|-----------|
| GET | `/payouts/establishments/{id}/balance` | Owner | Saldo disponível |
| POST | `/payouts/establishments/{id}/requests` | Owner | Solicita saque (mín. R$50) |
| GET | `/payouts/establishments/{id}/history` | Owner | Histórico |

---

## Analytics — `/analytics`

| Método | Path | Auth | Descrição |
|--------|------|------|-----------|
| GET | `/analytics/establishments/{id}/dashboard` | Owner | KPIs (`start_date`, `end_date`) |

Retorna: `total_revenue`, `total_appointments`, `no_show_rate`, `ticket_average`, `staff_performance`.

---

## Admin — `/admin` (role: admin)

| Método | Path | Descrição |
|--------|------|-----------|
| GET | `/admin/dashboard` | KPIs plataforma |
| GET/POST | `/admin/establishments` | Lista / cria |
| GET/PATCH/DELETE | `/admin/establishments/{id}` | CRUD |
| GET/PATCH | `/admin/users`, `/admin/users/{id}` | Usuários |
| GET | `/admin/subscriptions` | Assinaturas |
| GET | `/admin/payments` | Pagamentos |
| GET | `/admin/audit-logs` | Audit trail |

---

## Admin Settings — `/admin/settings`

| Método | Path | Descrição |
|--------|------|-----------|
| GET | `/admin/settings` | Lista (secrets mascarados) |
| GET | `/admin/settings/{key}` | Detalhe |
| PUT | `/admin/settings/{key}` | Atualiza |
| POST | `/admin/settings` | Cria |
| DELETE | `/admin/settings/{key}` | Remove |
| POST | `/admin/settings/seed-defaults` | Seed nVoIP, SMS, fees |

---

## Rate limiting

Middleware global in-memory (dev) / Redis (prod planejado):

- `RATE_LIMIT_REQUESTS=100` por `RATE_LIMIT_WINDOW_SECONDS=60`
- Desabilitado em testes (`RATE_LIMIT_ENABLED=False`)

---

## Roles

| Role | Descrição |
|------|-----------|
| `customer` | Cliente final |
| `owner` | Dono de estabelecimento |
| `staff` | Profissional vinculado |
| `admin` | Plataforma DUNNAA |

---

## Plugins — `/establishments/{id}/plugins`

| Método | Path | Auth | Descrição |
|--------|------|------|-----------|
| GET | `.../plugins` | Owner | Lista plugins instalados |
| POST | `.../plugins` | Owner | Instala/reativa plugin |
| PATCH | `.../plugins/{plugin_id}` | Owner | Atualiza config |
| DELETE | `.../plugins/{plugin_id}` | Owner | Desativa |

Tipos: `ads`, `marketing`, `analytics`.

---

## Ad Campaigns — `/establishments/{id}/ad-campaigns`

| Método | Path | Auth | Descrição |
|--------|------|------|-----------|
| GET | `.../ad-campaigns` | Owner | Lista campanhas |
| POST | `.../ad-campaigns` | Owner | Cria campanha |
| PATCH | `.../ad-campaigns/{id}` | Owner | Atualiza |
| DELETE | `.../ad-campaigns/{id}` | Owner | Desativa |
| POST | `.../ad-campaigns/{id}/impressions` | — | Registra impressão |

Estabelecimentos com campanha ativa aparecem primeiro na busca pública.

---

## Google Reviews — `/reviews`

| Método | Path | Auth | Descrição |
|--------|------|------|-----------|
| POST | `/reviews/{id}/approve-google` | Owner | Aprova review 4+★ |
| POST | `/reviews/{id}/send-google` | Owner | Envia ao Google (mock) |
| GET | `/reviews/establishments/{id}/google-pending` | Owner | Pendentes de envio |

---

## Pendências documentadas

- Analytics export PDF/Excel
- Stripe billing recorrente automático para assinaturas
- Redis rate limiting multi-instância
- Google Places API real (substituir mock)

Ver [`BACKEND_COMPLETE.md`](./BACKEND_COMPLETE.md) para roadmap detalhado.
