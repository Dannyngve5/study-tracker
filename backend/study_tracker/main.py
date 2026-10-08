from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from study_tracker.infrastructure.database.config import settings
from study_tracker.presentation.api.exception_handlers import (
    register_exception_handlers,
)
from study_tracker.presentation.api.routes.analytics import router as analytics_router
from study_tracker.presentation.api.routes.study_sessions import (
    router as study_sessions_router,
)
from study_tracker.presentation.api.routes.subjects import router as subjects_router
from study_tracker.presentation.api.routes.sub_subjects import (
    router as sub_subjects_router,
)

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.cors_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(subjects_router)
app.include_router(sub_subjects_router)
app.include_router(study_sessions_router)
app.include_router(analytics_router)
