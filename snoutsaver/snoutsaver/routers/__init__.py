from . import root
from . import users
from . import records
from . import categories

def init_router(app):
    app.include_router(root.router)
    app.include_router(users.router)
    app.include_router(records.router)
    app.include_router(categories.router)
