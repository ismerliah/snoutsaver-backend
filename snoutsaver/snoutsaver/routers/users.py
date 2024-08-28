from fastapi import APIRouter

from .. import models

router = APIRouter(tags=["User"], prefix="/users")