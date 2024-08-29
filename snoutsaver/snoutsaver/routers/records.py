from fastapi import APIRouter, HTTPException, Depends, Query

from typing import Optional,Annotated

from sqlmodel import Field, SQLModel, select, func, Session
from sqlmodel.ext.asyncio.session import AsyncSession

from snoutsaver.snoutsaver.models.records import Record,Records

from .. import models

router = APIRouter(tags=["Record"], prefix="/records")


records = []

# Create
@router.post("/records/")
async def create_record(record: Record):
    record.id = len(records) + 1
    records.append(record)
    return record

# Read 
@router.get("/records/")
async def read_records():
    return Records(__root__=records)

# Read a single record by ID
@router.get("/records/{record_id}")
async def read_record(record_id: int):
    for record in records:
        if record.id == record_id:
            return record
    raise HTTPException(status_code=404, detail="Record not found")

# Update
@router.put("/records/{record_id}")
async def update_record(record_id: int, record: Record):
    for i, existing_record in enumerate(records):
        if existing_record.id == record_id:
            records[i] = record
            return record
    raise HTTPException(status_code=404, detail="Record not found")

# Delete
@router.delete("/records/{record_id}")
async def delete_record(record_id: int):
    for i, existing_record in enumerate(records):
        if existing_record.id == record_id:
            del records[i]
            return {"message": "Record deleted"}
    raise HTTPException(status_code=404, detail="Record not found")