from fastapi import FastAPI
from .models import init_db
from .routers import init_router

def create_app():
    app = FastAPI()

    init_db()
    
    init_router(app)

    return app