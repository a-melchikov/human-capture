from typing import Any, TypeVar

from sqlalchemy import delete as sqlalchemy_delete
from sqlalchemy import select
from sqlalchemy import update as sqlalchemy_update
from sqlalchemy.exc import SQLAlchemyError

from app.database.base import Base
from app.database.core import async_session_maker
from app.repositories.base import BaseRepository

T = TypeVar("T", bound=Base)


class SQLAlchemyRepository(BaseRepository[T]):
    """Базовый репозиторий для работы с моделями SQLAlchemy."""

    model: type[T]

    @classmethod
    async def find_all(cls, **filter_by: Any) -> list[T]:
        """
        Найти все записи в таблице, соответствующие фильтру.

        :param filter_by: Параметры фильтрации.
        :return: Список объектов модели.
        """
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by)
            result = await session.execute(query)
            return list(result.scalars().all())

    @classmethod
    async def find_one_or_none_by_id(cls, data_id: int) -> T | None:
        """
        Найти одну запись по идентификатору.

        :param data_id: Идентификатор записи.
        :return: Объект модели или None.
        """
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(id=data_id)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def find_one_or_none(cls, **filter_by: Any) -> T | None:
        """
        Найти одну запись, соответствующую фильтру.

        :param filter_by: Параметры фильтрации.
        :return: Объект модели или None.
        """
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def add(cls, **values: Any) -> T:
        """
        Добавить новую запись в базу данных.

        :param values: Данные для новой записи.
        :return: Созданный объект модели.
        """
        async with async_session_maker() as session:
            async with session.begin():
                new_instance = cls.model(**values)
                session.add(new_instance)
                try:
                    await session.commit()
                    return new_instance
                except SQLAlchemyError as e:
                    await session.rollback()
                    raise e

    @classmethod
    async def update(cls, filter_by: dict[str, Any], **values: Any) -> int:
        """
        Обновить записи, соответствующие фильтру.

        :param filter_by: Параметры фильтрации.
        :param values: Новые значения.
        :return: Количество обновлённых строк.
        """
        async with async_session_maker() as session:
            async with session.begin():
                query = (
                    sqlalchemy_update(cls.model)
                    .where(*[getattr(cls.model, k) == v for k, v in filter_by.items()])
                    .values(**values)
                    .execution_options(synchronize_session="fetch")
                )
                result = await session.execute(query)
                try:
                    await session.commit()
                    return result.rowcount
                except SQLAlchemyError as e:
                    await session.rollback()
                    raise e

    @classmethod
    async def delete(cls, delete_all: bool = False, **filter_by: Any) -> int:
        """
        Удалить записи, соответствующие фильтру.

        :param delete_all: Флаг удаления всех записей таблицы (осторожно).
        :param filter_by: Параметры фильтрации.
        :return: Количество удалённых строк.
        """
        if not delete_all and not filter_by:
            raise ValueError("Необходимо указать хотя бы один параметр для удаления")

        async with async_session_maker() as session:
            async with session.begin():
                query = sqlalchemy_delete(cls.model).filter_by(**filter_by)
                result = await session.execute(query)
                try:
                    await session.commit()
                    return result.rowcount
                except SQLAlchemyError as e:
                    await session.rollback()
                    raise e
