from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db import crud
from app.schemas.items import ItemCreate, ItemUpdate, ItemResponse
from app.core.auth_dependencies import get_current_user, require_role
from fastapi import Request
from app.core.cache import cache_get, cache_set, cache_invalidate_prefix

from app.services.external import fetch_quote
from app.schemas.items import ItemResponse
from fastapi import HTTPException
from sqlalchemy.orm import Session
from fastapi import Depends
from app.db.session import get_db
from app.db import crud

from app.core.exceptions import NotFoundError

#Background task - Temporary

import logging
from fastapi import BackgroundTasks




router = APIRouter(prefix="/items", tags=["Items"], dependencies=[Depends(get_current_user)])


@router.get("/", response_model=list[ItemResponse])
async def list_items(
    request: Request,
    skip: int = 0,
    limit: int = 10,
    category: str | None = None,
    sort: str | None = None,
    db: Session = Depends(get_db),
):
    cached = await cache_get(request, prefix="items_list")
    if cached is not None:
        return cached  # FastAPI will validate/serialize to response_model

    items = crud.get_items(db, skip, limit, category, sort)
    # Convert ORM objects to dicts for caching
    payload = [
        ItemResponse.model_validate(i).model_dump(mode="json")
        for i in items
    ]

    await cache_set(request, prefix="items_list", payload=payload)
    return payload


@router.get("/{item_id}", response_model=ItemResponse)
def get_item(item_id: str, db: Session = Depends(get_db)):
    item = crud.get_item(db, item_id)
    if not item:
        raise NotFoundError("Item not found")
    return item

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

#Patch endpoints

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
    await cache_invalidate_prefix("items_list")
    return updated

# Delete endpoints

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
    await cache_invalidate_prefix("items_list")

# Background Task

logger = logging.getLogger(__name__)

def audit_log(event: str, item_id: str):
    logger.info({"audit": event, "item_id": item_id})

@router.post("/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(
    item: ItemCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    created = crud.create_item(db, item)
    background_tasks.add_task(audit_log, "item_created", str(created.id))
    await cache_invalidate_prefix("items_list")
    return created

# End Background Task