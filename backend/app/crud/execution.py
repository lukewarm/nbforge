from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.execution import Execution
from app.schemas.execution import ExecutionCreate, ExecutionUpdate
from app.crud.base import CRUDBase

class CRUDExecution(CRUDBase[Execution, ExecutionCreate, ExecutionUpdate]):
    def get_by_user(
        self, db: Session, *, user_id: str, skip: int = 0, limit: int = 100
    ) -> List[Execution]:
        return (
            db.query(self.model)
            .filter(Execution.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def create_with_owner(
        self, db: Session, *, obj_in: ExecutionCreate, user_id: str
    ) -> Execution:
        obj_in_data = obj_in.dict()
        db_obj = Execution(**obj_in_data, user_id=user_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

execution = CRUDExecution(Execution) 