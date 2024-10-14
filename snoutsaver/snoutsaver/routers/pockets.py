from fastapi import APIRouter, HTTPException, Depends, Query

from typing import List, Optional,Annotated
from sqlmodel import Field, SQLModel, select, func, Session
from sqlmodel.ext.asyncio.session import AsyncSession

from snoutsaver.snoutsaver.models.pockets import PocketCreate, PocketTransfer

from .. import models
from .. import deps

router = APIRouter(tags=["Pocket"], prefix="/pockets")

@router.post("/pockets/", response_model=PocketCreate)
async def create_pocket(pocket: PocketCreate, session: AsyncSession = Depends(models.get_session)):
    session.add(pocket)
    await session.commit()
    await session.refresh(pocket)
    return pocket

# Route to transfer balance between pockets
@router.post("/pockets/transfer")
async def transfer_balance(transfer: PocketTransfer, session: AsyncSession = Depends(models.get_session)):
    query_from = select(PocketCreate).where(PocketCreate.pocket_id == transfer.from_pocket_id)
    query_to = select(PocketCreate).where(PocketCreate.pocket_id == transfer.to_pocket_id)

    from_pocket = (await session.execute(query_from)).scalar_one_or_none()
    to_pocket = (await session.execute(query_to)).scalar_one_or_none()

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

# Route to get all pockets
@router.get("/pockets/", response_model=List[PocketCreate])
async def get_all_pockets(session: AsyncSession = Depends(models.get_session)):
    result = await session.execute(select(PocketCreate))
    pockets = result.scalars().all()
    return pockets