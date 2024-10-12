from sqlmodel import select
from . import models
from sqlmodel.ext.asyncio.session import AsyncSession

DEFAULT_CATEGORIES = [
    {"name": "Salary", "type": "Income", "icon": "business_center_rounded"},
    {"name": "Gift", "type": "Income", "icon": "card_giftcard_rounded"},
    {"name": "Investment", "type": "Income", "icon": "monetization_on_rounded"},
    {"name": "Loan", "type": "Income", "icon": "account_balance_rounded"},
    {"name": "Other", "type": "Income", "icon": "more_horiz_rounded"},

    {"name": "Food & Drinks", "type": "Expense", "icon": "fastfood_rounded"},
    {"name": "Transport", "type": "Expense", "icon": "train_rounded"},
    {"name": "Shopping", "type": "Expense", "icon": "shopping_cart_rounded"},
    {"name": "Home", "type": "Expense", "icon": "home_rounded"},
    {"name": "Bills", "type": "Expense", "icon": "receipt_long_rounded"},
    {"name": "Entertainment", "type": "Expense", "icon": "music_note_rounded"},
    {"name": "Education", "type": "Expense", "icon": "school_rounded"},
    {"name": "Health", "type": "Expense", "icon": "medical_services_rounded"},
    {"name": "Other", "type": "Expense", "icon": "more_horiz_rounded"},
]

async def seed_default_categories(session: AsyncSession):
    for category_data in DEFAULT_CATEGORIES:
        # Check if the category already exists
        existing_category = await session.exec(
            select(models.DBCategory).where(
                models.DBCategory.name == category_data["name"],
                models.DBCategory.type == category_data["type"]
            )
        )
        existing_category = existing_category.one_or_none()
        
        if not existing_category:
            # If it doesn't exist, create a new category
            new_category = models.DBCategory(**category_data)
            session.add(new_category)
            print(f"Created category: {new_category.name}")
    
    await session.commit()