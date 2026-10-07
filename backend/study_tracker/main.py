from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from study_tracker.presentation.api.exception_handlers import (
    register_exception_handlers,
)
from study_tracker.presentation.api.routes.subjects import (
    router as subjects_router,
)

from study_tracker.presentation.api.routes.study_sessions import (
    router as study_sessions_router,
)

app = FastAPI(title="Study Tracker")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(subjects_router)
app.include_router(study_sessions_router)
