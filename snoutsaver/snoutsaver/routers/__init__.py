from . import root
from . import authentication
from . import users
from . import records
from . import categories
from . import setups
from . import pockets

def init_router(app):
    app.include_router(root.router)
    app.include_router(authentication.router)
    app.include_router(users.router)
    app.include_router(records.router)
    app.include_router(categories.router)
    app.include_router(setups.router)
    app.include_router(pockets.router)
