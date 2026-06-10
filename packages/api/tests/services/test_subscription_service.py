"""Subscription service unit tests."""

from uuid import UUID

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.models.establishment import EstablishmentStatus
from app.models.subscription import SubscriptionPlan, SubscriptionPlanItem
from app.services.subscription_service import SubscriptionService


@pytest.mark.asyncio
async def test_list_subscriptions_empty(db_engine):
    Session = async_sessionmaker(bind=db_engine, expire_on_commit=False)
    async with Session() as session:
        from app.models.user import User

        user = User(phone="+5511444000002", referral_code="SUB00001")
        session.add(user)
        await session.commit()
        await session.refresh(user)

        service = SubscriptionService(session)
        subs = await service.list_for_user(user.id)
        assert subs == []


@pytest.mark.asyncio
async def test_create_subscription_requires_active_establishment(
    db_engine, establishment_id, service_id
):
    Session = async_sessionmaker(bind=db_engine, expire_on_commit=False)
    est_id = UUID(str(establishment_id))
    svc_id = UUID(str(service_id))
    async with Session() as session:
        from app.models.user import User
        from sqlalchemy import select

        plan = SubscriptionPlan(
            establishment_id=est_id,
            name="Plano Mensal",
            price=99.0,
            active=True,
        )
        session.add(plan)
        await session.flush()
        session.add(SubscriptionPlanItem(plan_id=plan.id, service_id=svc_id, quantity_per_month=4))
        await session.commit()
        await session.refresh(plan)

        user = (await session.execute(select(User).limit(1))).scalar_one()
        service = SubscriptionService(session)

        with pytest.raises(ValueError, match="indisponível"):
            await service.create(user.id, plan.id)

        from app.models.establishment import Establishment

        est = await session.get(Establishment, est_id)
        est.status = EstablishmentStatus.active
        await session.commit()

        sub = await service.create(user.id, plan.id)
        assert sub.status.value == "active"


@pytest.mark.asyncio
async def test_subscription_cancel_and_duplicate(db_engine, establishment_id, service_id):
    Session = async_sessionmaker(bind=db_engine, expire_on_commit=False)
    est_id = UUID(str(establishment_id))
    svc_id = UUID(str(service_id))
    async with Session() as session:
        from app.models.establishment import Establishment
        from app.models.user import User
        from sqlalchemy import select

        est = await session.get(Establishment, est_id)
        est.status = EstablishmentStatus.active
        await session.flush()

        plan = SubscriptionPlan(
            establishment_id=est_id,
            name="Plano Semanal",
            price=49.0,
            active=True,
        )
        session.add(plan)
        await session.flush()
        session.add(SubscriptionPlanItem(plan_id=plan.id, service_id=svc_id, quantity_per_month=2))
        await session.commit()
        await session.refresh(plan)

        user = (await session.execute(select(User).limit(1))).scalar_one()
        service = SubscriptionService(session)

        sub = await service.create(user.id, plan.id)
        with pytest.raises(ValueError, match="já possui"):
            await service.create(user.id, plan.id)

        cancelled = await service.cancel(sub.id, user.id)
        assert cancelled.status.value == "cancelled"

        with pytest.raises(ValueError, match="cancelada"):
            await service.cancel(sub.id, user.id)


@pytest.mark.asyncio
async def test_subscription_usage_and_consume_credit(db_engine, establishment_id, service_id):
    Session = async_sessionmaker(bind=db_engine, expire_on_commit=False)
    est_id = UUID(str(establishment_id))
    svc_id = UUID(str(service_id))
    async with Session() as session:
        from app.models.establishment import Establishment
        from app.models.user import User
        from sqlalchemy import select

        est = await session.get(Establishment, est_id)
        est.status = EstablishmentStatus.active
        await session.flush()

        plan = SubscriptionPlan(
            establishment_id=est_id,
            name="Plano Uso",
            price=79.0,
            active=True,
        )
        session.add(plan)
        await session.flush()
        session.add(SubscriptionPlanItem(plan_id=plan.id, service_id=svc_id, quantity_per_month=2))
        await session.commit()
        await session.refresh(plan)

        user = (await session.execute(select(User).limit(1))).scalar_one()
        service = SubscriptionService(session)
        sub = await service.create(user.id, plan.id)

        active = await service.find_active_for_establishment(user.id, est_id)
        assert active is not None

        summary = await service.build_usage_summary(sub)
        assert summary.items[0].remaining == 2

        await service.consume_credit(sub, svc_id)
        summary_after = await service.build_usage_summary(sub)
        assert summary_after.items[0].uses_this_month == 1

        est_subs = await service.list_for_establishment(est_id)
        assert len(est_subs) >= 1

        fetched = await service.get_for_user(sub.id, user.id)
        assert fetched is not None
