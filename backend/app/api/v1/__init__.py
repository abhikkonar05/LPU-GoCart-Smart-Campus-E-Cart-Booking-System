from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.routes import router as routes_router
from app.api.v1.carts import router as carts_router
from app.api.v1.bookings import router as bookings_router
from app.api.v1.payments import router as payments_router
from app.api.v1.drivers import router as drivers_router
from app.api.v1.tracking import router as tracking_router
from app.api.v1.admin import router as admin_router

api_v1_router = APIRouter()
api_v1_router.include_router(auth_router)
api_v1_router.include_router(routes_router)
api_v1_router.include_router(carts_router)
api_v1_router.include_router(bookings_router)
api_v1_router.include_router(payments_router)
api_v1_router.include_router(drivers_router)
api_v1_router.include_router(tracking_router)
api_v1_router.include_router(admin_router)

