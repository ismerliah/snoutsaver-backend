from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from .. import models, deps

router = APIRouter(tags=["Category"], prefix="/categories")

# Create Category
@router.post("")
async def create_category(
    category: models.CreatedCategory,
    current_user: Annotated[models.User, Depends(deps.get_current_user)],
    session: Annotated[AsyncSession, Depends(models.get_session)]
) -> models.Category:
    
    data = await session.execute(
        select(models.DBCategory).where(models.DBCategory.name == category.name)
    )
    existing_category = data.scalars().first()

    if existing_category:
        raise HTTPException( status_code=400, detail="Category already exists")
    
    db_category = models.DBCategory.model_validate(category)
    session.add(db_category)
    await session.commit()
    await session.refresh(db_category)

    return models.Category.model_validate(db_category)

# Get All Categories
@router.get("")
async def read_all_categories(
    current_user: Annotated[models.User, Depends(deps.get_current_user)],
    session: Annotated[AsyncSession, Depends(models.get_session)]
) -> models.CategoryList:
    
    result = await session.exec(select(models.DBCategory))
    categories = result.all()

    if not categories:
        raise HTTPException(status_code=404, detail="Category not found")

    return models.CategoryList.model_validate(
        dict(items=categories, page_size=0, page=0, size_per_page=0)
    )

# Get Category by ID
@router.get("/{category_id}")
async def read_category(
    category_id: int,
    current_user: Annotated[models.User, Depends(deps.get_current_user)],
    session: Annotated[AsyncSession, Depends(models.get_session)]
) -> models.Category:
    
    db_category = await session.get(models.DBCategory, category_id)

    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return models.Category.model_validate(db_category)

# Update Category
@router.put("/{category_id}")
async def update_category(
    category_id: int,
    category: models.UpdatedCategory,
    current_user: Annotated[models.User, Depends(deps.get_current_user)],
    session: Annotated[AsyncSession, Depends(models.get_session)]
) -> models.Category:
    
    data = category.model_dump()
    db_category = await session.get(models.DBCategory, category_id)

    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    db_category.sqlmodel_update(data)
    session.add(db_category)
    await session.commit()
    await session.refresh(db_category)

    return models.Category.model_validate(db_category)

# Delete Category
@router.delete("/{category_id}")
async def delete_category(
    category_id: int,
    current_user: Annotated[models.User, Depends(deps.get_current_user)],
    session: Annotated[AsyncSession, Depends(models.get_session)]
) -> dict:
    
    db_category = await session.get(models.DBCategory, category_id)

    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    await session.delete(db_category)
    await session.commit()

    return dict(message="Delete category success")