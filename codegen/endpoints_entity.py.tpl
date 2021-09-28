from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud, models, schemas
from app.api import deps
from app.translate import _

router = APIRouter()


@router.get("/", response_model=List[schemas.{{ entity }}])
def read_{{ entity_lower }}s(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve {{ entity_lower }}.
    """
    {{ entity_lower }}s = crud.{{ entity_lower }}.get_multi(db, skip=skip, limit=limit)
    return {{ entity_lower }}s


@router.post("/", response_model=schemas.{{ entity }})
def create_{{ entity_lower }}(
    *,
    db: Session = Depends(deps.get_db),
    {{ entity_lower }}_in: schemas.{{ entity }}Create,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create new {{ entity_lower }}.
    """

    {{ entity_lower }} = crud.{{ entity_lower }}.create(db=db, obj_in={{ entity_lower }}_in)

    return {{ entity_lower }}


@router.get("/{id}", response_model=schemas.{{ entity }})
def read_{{ entity_lower }}(
    id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser),
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Get a {{ entity_lower }}.
    """
    {{ entity_lower }} = crud.{{ entity_lower }}.get(db=db, id=id)
    if not {{ entity_lower }}:
        raise HTTPException(
            status_code=400, detail=_("{{ entity }} doesn't exists")
        )
    return {{ entity_lower }}


@router.put("/{id}", response_model=schemas.{{ entity }})
def update_{{ entity_lower }}(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    {{ entity_lower }}_in: schemas.{{ entity }}Update,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update a {{ entity_lower }}.
    """
    {{ entity_lower }} = crud.{{ entity_lower }}.get(db=db, id=id)
    if not {{ entity_lower }}:
        raise HTTPException(
            status_code=404,
            detail=_("{{ entity }} doesn't exists"),
        )
    {{ entity_lower }} = crud.{{ entity_lower }}.update(db=db, db_obj={{ entity_lower }}, obj_in={{ entity_lower }}_in)
    return {{ entity_lower }}


@router.delete("/{id}", response_model=schemas.{{ entity }})
def delete_{{ entity_lower }}(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Delete an {{ entity_lower }}.
    """
    {{ entity_lower }} = crud.{{ entity_lower }}.get(db=db, id=id)
    if not {{ entity_lower }}:
        raise HTTPException(status_code=404, detail=_("{{ entity }} doesn't exists"))

    {{ entity_lower }} = crud.{{ entity_lower }}.remove(db=db, id=id)
    return {{ entity_lower }}
