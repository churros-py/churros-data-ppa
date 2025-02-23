from sqlmodel import Session, select, SQLModel
from typing import Type, TypeVar, List, Optional, Generic, cast

T = TypeVar("T", bound=SQLModel)
ID = TypeVar("ID")

class BaseRepository(Generic[T]):
    def __init__(self, session: Session, model: Type[T]):
        self.session = session
        self.model = model

    def save(self, entity: T) -> T:
        self.session.add(entity)
        self.session.commit()
        self.session.refresh(entity)
        return entity

    def find_by_id(self, id: ID) -> Optional[T]:
        return cast(Optional[T], self.session.get(self.model, id))

    def find_all(self) -> List[T]:
        return cast(List[T], self.session.exec(select(self.model)).all())

    def update(self, entity: T) -> T:
        self.session.add(entity)
        self.session.commit()
        self.session.refresh(entity)
        return entity

    def delete(self, model_id: ID) -> Optional[T]:
        entity = self.find_by_id(model_id)
        if entity is not None:
            self.session.delete(entity)
            self.session.commit()
        return entity

    def delete_all(self) -> int:
        query = select(self.model)
        result = self.session.exec(query).all()
        deleted_count = len(result)
        for entity in result:
            self.session.delete(entity)
        self.session.commit()
        return deleted_count
