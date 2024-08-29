from fastapi import APIRouter, Depends, HTTPException, status, Request

from typing import Annotated

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from .. import models
from .. import deps

router = APIRouter(tags=["User"], prefix="/users")

# Create a new user
@router.post("/create")
async def create_user(
    user_info: models.RegisterUser,
    session: Annotated[AsyncSession, Depends(models.get_session)]
) -> models.User:
    
    user = await session.exec(
        select(models.DBUser).where(models.DBUser.username == user_info.username)
    )

    user = user.one_or_none()

    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    if user_info.password != user_info.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )
    
    user = models.DBUser.model_validate(user_info)
    await user.set_password(user_info.password)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

# Get current user
@router.get("/me")
def get_user_me(
    current_user: models.User = Depends(deps.get_current_user)
) -> models.User:
    return current_user

# Update user information
@router.put("{user_id}/update")
async def update_user(
    request: Request,
    user_id: int,
    user_update: models.UpdateUser,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: models.User = Depends(deps.get_current_user)
) -> models.User:
    
    db_user = await session.get(models.DBUser, user_id)

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )