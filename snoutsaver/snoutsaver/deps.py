from fastapi import Depends, HTTPException, logger, status, Path, Query
from fastapi.security import OAuth2PasswordBearer

import typing
import jwt

from pydantic import ValidationError

from . import models
from . import security
from . import config


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

settings = config.get_settings()


async def get_current_user(
    token: typing.Annotated[str, Depends(oauth2_scheme)],
    session: typing.Annotated[models.AsyncSession, Depends(models.get_session)],
) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        user_id: int = payload.get("sub")

        if user_id is None:
            raise credentials_exception

    except jwt.PyJWTError as e:
        print(e)
        raise credentials_exception

    user = await session.get(models.DBUser, user_id)
    if user is None:
        raise credentials_exception

    return user