from fastapi import APIRouter, HTTPException, Depends, Query

from typing import Optional,Annotated
from sqlmodel import Field, SQLModel, select, func, Session
from sqlmodel.ext.asyncio.session import AsyncSession

from .. import models
from .. import deps

router = APIRouter(tags=["Record"], prefix="/records")


# Create
@router.post("")
async def create_record(
    record: models.CreateRecord,
    current_user: Annotated[models.User, Depends(deps.get_current_user)],
    session: Annotated[AsyncSession, Depends(models.get_session)],
    ) -> models.Records | None:
    # data = await session.get(models.DBRecord, record.id)
    # if not data:
    #     raise HTTPException(status_code=404, detail=" data not found ;( ")
    
    # data = await session.exec(
    #     select(models.DBRecord).where(models.DBRecord.id == record.id)
    # )

    db_record = models.DBRecord.model_validate(record)

    category = await session.exec(
        select(models.DBCategory).where(models.DBCategory.id == record.category_id) 
    )
    category = category.one_or_none()

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    db_record.user = current_user
    db_record.category = category
    db_record.category_name = category.name

    session.add(db_record)
    await session.commit()
    await session.refresh(db_record)

    return models.Records.model_validate(db_record)

# Read 
@router.get("")
async def read_all_records(
    current_user: Annotated[models.User, Depends(deps.get_current_user)],
    session: Annotated[AsyncSession, Depends(models.get_session)]
) -> models.RecordList:
    
    result = await session.exec(
        select(models.DBRecord).where(models.DBRecord.user_id == current_user.id)
    )
    records = result.all()

    if not records:
        raise HTTPException(status_code=404, detail="Record not found")
    

    return models.RecordList.model_validate(
        dict(records=records)
    )

# Read record by ID
@router.get("/{record_id}")
async def read_record(
    record_id: int,
    session: Annotated[AsyncSession, Depends(models.get_session)]
    ) -> models.Records:
    
    db_record = await session.get(models.DBRecord, record_id)
    if not db_record:
        raise HTTPException(status_code=404, detail="Record not found")

    return models.Records.model_validate

# Update
@router.put("/{record_id}")
async def update_record(
    record_id: int, 
    record: models.UpdatedRecord,
    session: Annotated[AsyncSession, Depends(models.get_session)]
    ) -> models.Records:
    
    data = record.model_dump()
    db_record = await session.get(models.DBRecord, record_id)

    if not db_record:
        raise HTTPException(status_code=404, detail="Record not found")
    
    db_record.sqlmodel_update(data)
    session.add(db_record)
    await session.commit()
    await session.refresh(db_record)

    return models.Records.model_validate(db_record)

# Delete
@router.delete("/{record_id}")
async def delete_record(
    record_id: int,
    session: Annotated[AsyncSession, Depends(models.get_session)]
    ) -> dict:

    db_record = await session.get(models.DBRecord, record_id)

    if not db_record:
        raise HTTPException(status_code=404, detail="Record not found")
    
    await session.delete(db_record)
    await session.commit()

    return dict(message="Delete record success")
  