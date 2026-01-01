from sqlalchemy.orm import Session
from app.db.models import Item
from app.schemas.items import ItemCreate, ItemUpdate
from app.db.models import User
from app.core.security import hash_password, verify_password


def create_item(db: Session, item: ItemCreate) -> Item:
    db_item = Item(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)   
    return db_item


def get_item(db: Session, item_id: str):
    return db.query(Item).filter(Item.id == item_id).first()


def get_items(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    category: str | None = None,
    sort: str | None = None,
):
    query = db.query(Item)

    if category:
        query = query.filter(Item.category == category)

    if sort:
        if sort.startswith("-"):
            query = query.order_by(getattr(Item, sort[1:]).desc())
        else:
            query = query.order_by(getattr(Item, sort).asc())

    return query.offset(skip).limit(limit).all()


def update_item(db: Session, item: Item, updates: ItemUpdate):
    for field, value in updates.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item


def delete_item(db: Session, item: Item):
    db.delete(item)
    db.commit()

def create_user(db, email: str, password: str, role: str = "user"):
    user = User(
        email=email,
        hashed_password=hash_password(password),
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user