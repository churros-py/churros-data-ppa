import re
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

class DynamicQueryMixin(Generic[T]):
    def _generate_query(self, method_name: str, *args) -> List[T]:
        pattern = r"find_by_(\w+)"
        match = re.match(pattern, method_name)
        if not match:
            raise AttributeError(f"Method '{method_name}' is not recognized")
        field_names = match.group(1).split("_and_")
        if len(field_names) != len(args):
            raise ValueError(f"Method '{method_name}' expects {len(field_names)} parameters, but got {len(args)}")
        filters = [getattr(self.model, field) == value for field, value in zip(field_names, args)]
        query = select(self.model).where(*filters)
        return cast(List[T], self.session.exec(query).all())

    def __getattr__(self, name: str):
        if name.startswith("find_by_"):
            def method(*args):
                return self._generate_query(name, *args)
            return method
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

class ChurrosRepository(BaseRepository[T], DynamicQueryMixin[T]):
    pass
