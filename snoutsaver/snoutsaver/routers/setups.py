from fastapi import APIRouter, HTTPException, Depends
from typing import Annotated
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from .. import models
from .. import deps
from sqlalchemy.orm import selectinload

router = APIRouter(tags=["Setup"], prefix="/setups")

# Create
@router.post("")
async def create_setups(
    setup: models.CreateSetup,
    current_user: Annotated[models.DBUser, Depends(deps.get_current_user)],
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> models.Setups:

    # Check if the user already setup
    existing_setup = await session.exec(
        select(models.DBSetup).where(models.DBSetup.user_id == current_user.id)
    )
    existing_setup = existing_setup.one_or_none()

    if existing_setup:
        raise HTTPException(status_code=400, detail="Setup already exists")

    db_setup = models.DBSetup(
        user_id=current_user.id,
        monthly_income=setup.monthly_income,
        saving_goal=setup.saving_goal,
        year=setup.year
    )

    session.add(db_setup)
    await session.flush()

    # Create monthly income record
    if setup.monthly_income:
        category = await session.exec(
            select(models.DBCategory).where(models.DBCategory.name == "Salary")
        )
        category = category.one_or_none()

        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

        db_income = models.DBRecord(
            user_id=current_user.id,
            amount=setup.monthly_income,
            currency="THB",
            type="Income",
            description="Monthly Income",
            category_id=category.id,
            category_name=category.name,
            is_monthly=True,
            setup_id=db_setup.id
        )

        session.add(db_income)

    # Create monthly expenses records
    if setup.monthly_expenses:
        for expense_record in setup.monthly_expenses:
            category = await session.exec(
                select(models.DBCategory).where(models.DBCategory.id == expense_record["category_id"])
            )
            category = category.one_or_none()

            if not category:
                raise HTTPException(status_code=404, detail="Category not found")

            db_expense = models.DBRecord(
                user_id=current_user.id,
                amount=expense_record["amount"],
                currency="THB",
                type="Expense",
                description=expense_record.get("description", "Monthly Expense"),
                category_id=category.id,
                category_name=category.name,
                is_monthly=True,
                setup_id=db_setup.id
            )

            session.add(db_expense)

    await session.commit()

    setup_result = await session.exec(
        select(models.DBSetup)
        .options(selectinload(models.DBSetup.monthly_expenses))
        .where(models.DBSetup.id == db_setup.id)
    )
    db_setup = setup_result.one_or_none()

    monthly_expenses = [expense.dict() for expense in db_setup.monthly_expenses]

    setup_data = models.Setups.model_validate({
        **db_setup.dict(),
        "monthly_expenses": monthly_expenses
    })

    return setup_data

# Read
@router.get("")
async def read_setups(
    current_user: Annotated[models.DBUser, Depends(deps.get_current_user)],
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> models.Setups:
    
    setup_result = await session.exec(
        select(models.DBSetup)
        .options(selectinload(models.DBSetup.monthly_expenses))
        .where(models.DBSetup.user_id == current_user.id)
    )
    db_setup = setup_result.one_or_none()

    if not db_setup:
        raise HTTPException(status_code=404, detail="Setup not found")

    monthly_expenses = [expense.dict() for expense in db_setup.monthly_expenses]

    setup_data = models.Setups.model_validate({
        **db_setup.dict(),
        "monthly_expenses": monthly_expenses
    })

    return setup_data

# Update
@router.put("")
async def update_setups(
    setup: models.UpdatedSetup,
    current_user: Annotated[models.DBUser, Depends(deps.get_current_user)],
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> models.Setups:

    setup_result = await session.exec(
        select(models.DBSetup)
        .options(selectinload(models.DBSetup.monthly_expenses))
        .where(models.DBSetup.user_id == current_user.id)
    )
    db_setup = setup_result.one_or_none()

    if not db_setup:
        raise HTTPException(status_code=404, detail="Setup not found")

    if setup.monthly_income is not None:
        db_setup.monthly_income = setup.monthly_income

    if setup.saving_goal is not None:
        db_setup.saving_goal = setup.saving_goal

    if setup.year is not None:
        db_setup.year = setup.year

    # Update monthly income record
    income_record = await session.exec(
        select(models.DBRecord)
        .where(models.DBRecord.setup_id == db_setup.id, models.DBRecord.type == "Income", models.DBRecord.is_monthly == True)
    )
    income_record = income_record.one_or_none()

    if income_record:
        income_record.amount = setup.monthly_income
        income_record.description = "Monthly Income"
    else:
        category = await session.exec(
            select(models.DBCategory).where(models.DBCategory.name == "Salary")
        )
        category = category.one_or_none()

        if not category:
            raise HTTPException(status_code=404, detail="Category 'Salary' not found")

        db_income = models.DBRecord(
            user_id=current_user.id,
            amount=setup.monthly_income,
            currency="THB",
            type="Income",
            description="Monthly Income",
            category_id=category.id,
            category_name=category.name,
            is_monthly=True,
            setup_id=db_setup.id
        )

        session.add(db_income)

    # Update monthly expenses records
    existing_expenses_by_id = {expense.id: expense for expense in db_setup.monthly_expenses}
    
    updated_expense_ids = set()

    for expense_record in setup.monthly_expenses:
        if "id" in expense_record and expense_record["id"] in existing_expenses_by_id:
            # Update existing expense record
            db_expense = existing_expenses_by_id[expense_record["id"]]
            db_expense.amount = expense_record["amount"]
            db_expense.description = expense_record.get("description", db_expense.description)
            updated_expense_ids.add(expense_record["id"])
        else:
            # Add new expense record
            category = await session.exec(
                select(models.DBCategory).where(models.DBCategory.id == expense_record["category_id"])
            )
            category = category.one_or_none()

            if not category:
                raise HTTPException(status_code=404, detail=f"Category not found for ID {expense_record['category_id']}")

            db_expense = models.DBRecord(
                user_id=current_user.id,
                amount=expense_record["amount"],
                currency="THB",
                type="Expense",
                description=expense_record.get("description", "Monthly Expense"),
                category_id=category.id,
                category_name=category.name,
                is_monthly=True,
                setup_id=db_setup.id
            )

            session.add(db_expense)
            db_setup.monthly_expenses.append(db_expense)

    # Delete expenses that are not in the updated list
    for expense_id, db_expense in existing_expenses_by_id.items():
        if expense_id not in updated_expense_ids:
            await session.delete(db_expense)

    await session.commit()

    setup_result = await session.exec(
        select(models.DBSetup)
        .options(selectinload(models.DBSetup.monthly_expenses))
        .where(models.DBSetup.id == db_setup.id)
    )
    db_setup = setup_result.one_or_none()

    monthly_expenses = [expense.dict() for expense in db_setup.monthly_expenses]

    setup_data = models.Setups.model_validate({
        **db_setup.dict(),
        "monthly_expenses": monthly_expenses
    })

    return setup_data

# Delete
@router.delete("")
async def delete_setup(
    setup_id: int,
    current_user: Annotated[models.DBUser, Depends(deps.get_current_user)],
    session: Annotated[AsyncSession, Depends(models.get_session)],
):
    # Fetch the setup to delete
    setup_to_delete = await session.exec(
        select(models.DBSetup)
        .where(models.DBSetup.id == setup_id, models.DBSetup.user_id == current_user.id)
    )
    setup_to_delete = setup_to_delete.one_or_none()

    if not setup_to_delete:
        raise HTTPException(status_code=404, detail="Setup not found")

    # Delete the setup
    await session.delete(setup_to_delete)
    await session.commit()

    return {"detail": "Setup deleted successfully"}