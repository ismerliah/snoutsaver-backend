from fastapi import APIRouter, Depends, HTTPException, status

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
    print("create_user", user_info)
    
    user = await session.exec(
        select(models.DBUser).where(models.DBUser.username == user_info.username)
    )
    user = user.one_or_none()

    # Check if user already exists
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    # Check password length
    if len(user_info.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters"
        )
    
    # Check if password and confirm password match
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
    print("current_user", current_user)

    return current_user


# Change password
@router.put("/{user_id}/change_password")
async def change_password (
    user_id: int,
    password_update: models.ChangePassword,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: models.User = Depends(deps.get_current_user)
) -> models.User:
    print("change_password", password_update)

    db_user = await session.get(models.DBUser, user_id)

    # Check if user exists
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if user is authorized
    if db_user.id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not authorized"
        )
    
    # Check password length
    if len(db_user.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters"
        )
    
    # Check if new password and confirm password match
    if not await db_user.verify_password(password_update.current_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    await db_user.set_password(password_update.new_password)
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user


# Update user information
@router.put("/{user_id}/update")
async def update_user(
    user_id: int,
    user_update: models.UpdateUser,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: models.User = Depends(deps.get_current_user)
) -> models.User:
    print("update_user", user_update)

    db_user = await session.get(models.DBUser, user_id)

    # Check if user exists
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if user is authorized
    if db_user.id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not authorized"
        )
    
    db_user.sqlmodel_update(user_update)
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user


# Delete user
@router.delete("/{user_id}/delete")
async def delete_user(
    user_id: int,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: models.User = Depends(deps.get_current_user)
) -> dict:
    print("delete_user", user_id)

    db_user = await session.get(models.DBUser, user_id)

    # Check if user exists
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if user is authorized
    if db_user.id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not authorized"
        )
    
    await session.delete(db_user)
    await session.commit()
    return dict(message="delete user success")
