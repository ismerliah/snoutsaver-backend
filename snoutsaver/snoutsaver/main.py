from fastapi import FastAPI
from . import models
from . import routers
from . import config

def create_app(settings=None):
    settings = config.get_settings()
    app = FastAPI()

    models.init_db(settings)
    
    routers.init_router(app)

    @app.on_event("startup")
    async def on_startup():
        await models.create_all()

    return app