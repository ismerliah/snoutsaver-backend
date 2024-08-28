from fastapi import APIRouter

from .. import models

router = APIRouter(tags=["Category"], prefix="/categories")