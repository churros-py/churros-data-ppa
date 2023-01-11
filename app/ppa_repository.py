from typing import TypeVar, Union, Generic

T = TypeVar("T")


class Identifier:
    id: int


class AbstractPersistable(Generic[T]):
    def save(self, entity: T) -> Union[T, Identifier]:
        """Returns the number of models available."""
        object.__setattr__(entity, "id", 123)
        return entity

    def find_by_id(self, id: int) -> T | None:
        """Retrieves an model by its id."""
        entity = T()
        object.__setattr__(entity, "id", id)
        return entity

    def delete_all(self) -> None:
        """Deletes all models managed by the repository"""

    def exists(self) -> bool:
        """Checks whether the data store contains elements that match the given"""
