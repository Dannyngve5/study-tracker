from fastapi import FastAPI

from study_tracker.presentation.api.exception_handlers import (
    register_exception_handlers,
)
from study_tracker.presentation.api.routes.subjects import (
    router as subjects_router,
)

app = FastAPI(title="Study Tracker")

register_exception_handlers(app)

app.include_router(subjects_router)
