from fastapi import APIRouter

from .. import models

router = APIRouter(tags=["Record"], prefix="/records")