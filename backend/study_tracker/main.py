from fastapi import FastAPI

from study_tracker.presentation.api.routes.subjects import router as subjects_router

app = FastAPI(title="Study Tracker")

app.include_router(subjects_router)
