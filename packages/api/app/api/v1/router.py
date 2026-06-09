"""API v1 router."""

from fastapi import APIRouter

from app.api.v1 import (
    admin,
    admin_settings,
    ad_campaigns,
    analytics,
    appointments,
    auth,
    availability,
    bundles,
    checkins,
    customer_subscriptions,
    establishments,
    favorites,
    notifications,
    payments,
    payouts,
    plugins,
    portfolio,
    products,
    promotions,
    queue,
    referrals,
    reviews,
    search,
    services,
    staff,
    subscriptions,
    tips,
    users,
)

router = APIRouter(prefix="/api/v1", tags=["API v1"])

# Include all routers
router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
router.include_router(auth.router)
router.include_router(users.router)
router.include_router(establishments.router)
router.include_router(services.router)
router.include_router(staff.router)
router.include_router(appointments.router)
router.include_router(queue.router)
router.include_router(reviews.router)
router.include_router(favorites.router)
router.include_router(portfolio.router)
router.include_router(notifications.router)
router.include_router(checkins.router, prefix="/checkins", tags=["Check-ins"])
router.include_router(bundles.router)
router.include_router(subscriptions.router)
router.include_router(subscriptions.owner_subs_router)
router.include_router(customer_subscriptions.router)
router.include_router(availability.router)
router.include_router(search.router)
router.include_router(products.router)
router.include_router(tips.router)
router.include_router(plugins.router)
router.include_router(ad_campaigns.router)
router.include_router(promotions.router)
router.include_router(referrals.router)
router.include_router(payments.router, prefix="/payments", tags=["Payments"])
router.include_router(payouts.router, prefix="/payouts", tags=["Payouts"])
router.include_router(admin_settings.router)
router.include_router(admin.router)
