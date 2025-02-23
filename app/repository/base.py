import re
from sqlalchemy.orm import Session
from typing import Type, TypeVar, List

T = TypeVar("T")

class GenericRepository:
    def __init__(self, session: Session, model: Type[T]):
        self.session = session
        self.model = model

    def _generate_query(self, method_name: str, *args) -> List[T]:
        pattern = r"find_by_(\w+)"
        match = re.match(pattern, method_name)

        if not match:
            raise AttributeError(f"Method '{method_name}' is not recognized")

        field_names = match.group(1).split("_and_")

        if len(field_names) != len(args):
            raise ValueError(f"Method '{method_name}' expects {len(field_names)} parameters, but got {len(args)}")

        filters = [getattr(self.model, field) == value for field, value in zip(field_names, args)]
        query = self.session.query(self.model).filter(*filters)
        
        result = query.all()
        print(f"🔍 Executing Query: {query}")  
        print(f"🔍 Query Result: {result}")  

        return result or []

    def __getattr__(self, name: str):
        if name.startswith("find_by_"):
            def method(*args):
                return self._generate_query(name, *args)
            return method
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
