from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth.router import router as auth_router
from app.users.router import router as users_router

app = FastAPI()

api = APIRouter(prefix="/api")
api.include_router(auth_router, tags=["auth"])
api.include_router(users_router, tags=["users"])
app.include_router(api)

origins = ["http://localhost", "http://127.0.0.1", "http://localhost:5173", "http://127.0.0.1:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
