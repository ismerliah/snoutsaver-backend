from fastapi import APIRouter, HTTPException, Depends, Query

router = APIRouter(tags=["root"])

@router.get("/")
async def index() -> dict:
    return dict(message="Snoutsaver API")