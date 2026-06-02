from fastapi import APIRouter, FastAPI

from app.auth.router import router as auth_router
from app.users.router import router as users_router

app = FastAPI()

api = APIRouter(prefix="/api")
api.include_router(auth_router, tags=["auth"])
api.include_router(users_router, tags=["users"])
app.include_router(api)
