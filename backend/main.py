from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import users, dashboard, firs, legal, ai, criminals, emergency

app = FastAPI(
    title="CrimeVision AI API",
    description="Backend API for Smart Crime Intelligence & Police Command Platform",
    version="1.0.0"
)

# CORS config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(dashboard.router)
app.include_router(firs.router)
app.include_router(legal.router)
app.include_router(ai.router)
app.include_router(criminals.router)
app.include_router(emergency.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to CrimeVision AI API"}
