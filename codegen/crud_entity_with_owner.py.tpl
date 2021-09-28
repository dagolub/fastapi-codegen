from typing import List, Optional, TypeVar

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from app.db.base_class import Base
from app.crud.base import CRUDBase
from app.models.{{ entity_lower }} import {{ entity }}
from app.schemas.{{ entity_lower }} import {{ entity }}Create,  {{ entity }}Update

ModelType = TypeVar("ModelType", bound=Base)


class CRUD{{ entity }}(CRUDBase[{{ entity }}, {{ entity }}Create, {{ entity }}Update]):
    def create_with_owner(
        self, db: Session, *, obj_in: {{ entity }}Create, owner_id: int
    ) -> {{ entity }}:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data, owner_id=owner_id) # noqa
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_owner(self, db: Session, id: int, owner_id: int) -> Optional[ModelType]:
        return db.query(self.model).filter(self.model.id == id, {{ entity }}.owner_id == owner_id).first()

    def get_multi_by_owner(
        self, db: Session, *, owner_id: int, skip: int = 0, limit: int = 100
    ) -> List[{{ entity }}]:
        return (
            db.query(self.model)
            .filter({{ entity }}.owner_id == owner_id)
            .offset(skip)
            .limit(limit)
            .all()
        )


{{ entity_lower }} = CRUD{{ entity }}({{ entity }})
