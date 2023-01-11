from typing import Generic, TypeVar, List
from abc import ABC, abstractmethod

ET = TypeVar("ET")
ID = TypeVar("ID")


class RepositoryInterface(Generic[ET, ID], ABC):
    @abstractmethod
    def save(self, model: ET) -> None:
        raise NotImplementedError()

    @abstractmethod
    def find_by_id(self, model_id: ID) -> ET:
        raise NotImplementedError()

    # @abstractmethod
    # def find_all(self) -> List[ET]:
    #     raise NotImplementedError()

    # @abstractmethod
    # def update(self, model: ET) -> None:
    #     raise NotImplementedError()

    # @abstractmethod
    # def delete(self, model_id: ID) -> None:
    #     raise NotImplementedError()
