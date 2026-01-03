from fastapi import (
    APIRouter,
    Depends,
    status,
    Request,
    BackgroundTasks,
)
from sqlalchemy.orm import Session
import logging

from app.db.session import get_db
from app.db import crud
from app.schemas.items import ItemCreate, ItemUpdate, ItemResponse
from app.core.auth_dependencies import get_current_user, require_role
from app.core.cache import (
    cache_get,
    cache_set,
    cache_invalidate_prefix,
    safe_cache_call,
)
from app.services.external import fetch_quote
from app.core.exceptions import NotFoundError


router = APIRouter(
    prefix="/items",
    tags=["Items"],
    dependencies=[Depends(get_current_user)],
)

logger = logging.getLogger(__name__)


# --------------------
# LIST ITEMS (cached)
# --------------------
@router.get("/", response_model=list[ItemResponse])
async def list_items(
    request: Request,
    skip: int = 0,
    limit: int = 10,
    category: str | None = None,
    sort: str | None = None,
    db: Session = Depends(get_db),
):
    cached = await safe_cache_call(
        cache_get,
        request,
        prefix="items_list",
    )
    if cached is not None:
        return cached

    items = crud.get_items(db, skip, limit, category, sort)

    payload = [
        ItemResponse.model_validate(item).model_dump(mode="json")
        for item in items
    ]

    await safe_cache_call(
        cache_set,
        request,
        prefix="items_list",
        payload=payload,
    )

    return payload


# --------------------
# GET SINGLE ITEM
# --------------------
@router.get("/{item_id}", response_model=ItemResponse)
def get_item(item_id: str, db: Session = Depends(get_db)):
    item = crud.get_item(db, item_id)
    if not item:
        raise NotFoundError("Item not found")
    return item


# --------------------
# ENRICH ITEM (ASYNC)
# --------------------
@router.get("/{item_id}/enrich")
async def enrich_item(item_id: str, db: Session = Depends(get_db)):
    item = crud.get_item(db, item_id)
    if not item:
        raise NotFoundError("Item not found")

    quote = await fetch_quote()

    return {
        "item": ItemResponse.model_validate(item).model_dump(mode="json"),
        "external": {
            "quote": quote.get("content"),
            "author": quote.get("author"),
        },
    }


# --------------------
# UPDATE ITEM
# --------------------
@router.patch("/{item_id}", response_model=ItemResponse)
async def update_item(
    item_id: str,
    updates: ItemUpdate,
    db: Session = Depends(get_db),
):
    item = crud.get_item(db, item_id)
    if not item:
        raise NotFoundError("Item not found")

    updated = crud.update_item(db, item, updates)

    await safe_cache_call(
        cache_invalidate_prefix,
        "items_list",
    )

    return updated


# --------------------
# DELETE ITEM (ADMIN)
# --------------------
@router.delete(
    "/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_role("admin"))],
)
async def delete_item(item_id: str, db: Session = Depends(get_db)):
    item = crud.get_item(db, item_id)
    if not item:
        raise NotFoundError("Item not found")

    crud.delete_item(db, item)

    await safe_cache_call(
        cache_invalidate_prefix,
        "items_list",
    )


# --------------------
# CREATE ITEM + AUDIT
# --------------------
def audit_log(event: str, item_id: str):
    logger.info({"audit": event, "item_id": item_id})


@router.post("/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(
    item: ItemCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    created = crud.create_item(db, item)

    background_tasks.add_task(
        audit_log,
        "item_created",
        str(created.id),
    )

    await safe_cache_call(
        cache_invalidate_prefix,
        "items_list",
    )

    return created