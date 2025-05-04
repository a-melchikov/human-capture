from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    """Общий интерфейс для всех репозиториев."""

    @classmethod
    @abstractmethod
    async def find_all(cls, **filter_by: Any) -> list[T]:
        """Найти все записи по фильтру."""
        pass

    @classmethod
    @abstractmethod
    async def find_one_or_none_by_id(cls, data_id: int) -> T | None:
        """Найти одну запись по идентификатору."""
        pass

    @classmethod
    @abstractmethod
    async def find_one_or_none(cls, **filter_by: Any) -> T | None:
        """Найти одну запись по фильтру."""
        pass

    @classmethod
    @abstractmethod
    async def add(cls, **values: Any) -> T:
        """Добавить новую запись."""
        pass

    @classmethod
    @abstractmethod
    async def update(cls, filter_by: dict[str, Any], **values: Any) -> int:
        """Обновить записи по фильтру."""
        pass

    @classmethod
    @abstractmethod
    async def delete(cls, delete_all: bool = False, **filter_by: Any) -> int:
        """Удалить записи по фильтру."""
        pass
