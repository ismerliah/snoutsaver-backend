# ssl patch
from gevent import monkey

monkey.patch_all()

from fastapi import FastAPI
from . import models
from . import routers
from . import config
from . import seed_data

def create_app(settings=None):
    settings = config.get_settings()
    app = FastAPI()

    models.init_db(settings)
    
    routers.init_router(app)

    @app.on_event("startup")
    async def on_startup():
        await models.create_all()
        async for session in models.get_session():
            await seed_data.seed_default_categories(session)

    @app.on_event("shutdown")
    async def on_shutdown():
        await models.close_session()

    return app