from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
import app.models
from app.api import organizations, goals, auth, feedback, reviews

# Create the database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Performance Management System API",
    description="Multi-tenant goal and performance tracking API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(organizations.router, prefix="/api/v1/organizations", tags=["Organizations"])
app.include_router(goals.router, prefix="/api/v1/goals", tags=["Goals Engine"])
app.include_router(feedback.router, prefix="/api/v1/feedback", tags=["Continuous Feedback"])
app.include_router(reviews.router, prefix="/api/v1/reviews", tags=["Performance Reviews"])

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Performance Management System API is running"}
