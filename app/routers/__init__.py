"""
Routers package for the experimentation platform
"""
from app.routers.experiments import router as experiments_router
from app.routers.events import router as events_router

__all__ = ["experiments_router", "events_router"]

