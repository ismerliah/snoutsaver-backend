from fastapi import APIRouter, HTTPException, Depends, Query, status

from typing import List, Optional,Annotated
from sqlmodel import Field, SQLModel, select, func, Session
from sqlmodel.ext.asyncio.session import AsyncSession


from .. import models
from .. import deps

router = APIRouter(tags=["Pocket"], prefix="/pockets")

@router.post("")
async def create_pocket(
    pocket: models.PocketCreate,
    current_user: Annotated[models.DBUser, Depends(deps.get_current_user)],
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> models.PocketCreate:
    
    print("create_pocket", pocket)

    pocket = models.DBPocket(
        user_id=current_user.id,
        name=pocket.name,
        balance=pocket.balance
    )

    session.add(pocket)
    await session.commit()
    await session.refresh(pocket)
    return pocket


# Route to get all pockets
@router.get("")
async def get_all_pockets(
    session: AsyncSession = Depends(models.get_session),
) -> models.PocketList:

    print("get_all_pockets")
    
    result = await session.execute(select(models.DBPocket))
    pockets = result.scalars().all()

    return models.PocketList.model_validate(
        dict(items=pockets, page_size=0, page=0, size_per_page=0)
    )

# Route to get all pockets by user_id
@router.get("/{user_id}")
async def get_all_pockets_id(
    user_id: int,
    current_user: Annotated[models.DBUser, Depends(deps.get_current_user)],
    session: AsyncSession = Depends(models.get_session),
) -> models.PocketList:
    
    print("get_all_pockets_by_id")

    user = await session.exec(
        select(models.DBUser).where(models.DBUser.id == user_id)
    )
    user = user.one_or_none()

    # Check if user exists
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if user is authorized
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not authorized"
        )
    
    db_pocket = await session.exec(
        select(models.DBPocket).where(models.DBPocket.user_id == user_id)
    )
    db_pocket = db_pocket.all()

    return models.PocketList(
        items=db_pocket,
        page_size=0,
        page=0,
        size_per_page=0
    )


# Route to transfer balance between pockets
@router.post("/transfer")
async def transfer_balance(
    transfer: models.PocketTransfer, 
    current_user: Annotated[models.DBUser, Depends(deps.get_current_user)],
    session: AsyncSession = Depends(models.get_session)
):
    query_from = select(models.DBPocket).where(models.DBPocket.id == transfer.from_pocket_id)
    query_to = select(models.DBPocket).where(models.DBPocket.id == transfer.to_pocket_id)

    from_pocket = (await session.execute(query_from)).scalar_one_or_none()
    to_pocket = (await session.execute(query_to)).scalar_one_or_none()

    # Check if user is authorized
    if from_pocket.user_id != current_user.id or to_pocket.user_id != current_user.id:
         raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not authorized"
        )

    if not from_pocket or not to_pocket:
        raise HTTPException(status_code=404, detail="One or both pockets not found")

    if from_pocket.balance < transfer.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds in the source pocket")

    from_pocket.balance -= transfer.amount
    to_pocket.balance += transfer.amount

    session.add(from_pocket)
    session.add(to_pocket)
    await session.commit()

    return {"message": "Transfer successful", "from_pocket_balance": from_pocket.balance, "to_pocket_balance": to_pocket.balance}
