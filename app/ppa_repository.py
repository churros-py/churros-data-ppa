from typing import TypeVar, Union, Generic, List
from app.repository_interface import RepositoryInterface

ET = TypeVar("ET")
ID = TypeVar("ID")


class ModelExample:
    pass


class Identifier(Generic[ID]):
    id: ID


class AbstractPersistable(RepositoryInterface[ET, ID]):
    def save(self, entity: ET) -> Union[ET, Identifier[ID]]:
        """Returns the number of models available."""
        object.__setattr__(entity, "id", 123)
        return entity

    def find_by_id(self, id: ID) -> ET | None:
        """Retrieves an model by its id."""
        entity: ET = ModelExample()
        object.__setattr__(entity, "id", id)
        return entity

    def find_all(self) -> List[Union[ET, Identifier[ID]]]:
        """Returns the number of models available."""
        model_1: ET = ModelExample()
        object.__setattr__(model_1, "id", 123)
        model_2: ET = ModelExample()
        object.__setattr__(model_2, "id", 123)

        return [model_1, model_2]

    def update(self, model: ET) -> None:
        """Update model"""

    def update_and_return(self, model: ET) -> ET:
        """Update model"""
        return model

    def delete(self, model_id: ID) -> None:
        """Update model"""

    def delete_all(self) -> None:
        """Deletes all models managed by the repository"""
