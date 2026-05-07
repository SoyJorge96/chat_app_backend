"""Repositorio del módulo `users`.

Esta capa se encarga exclusivamente del acceso a datos.
"""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.v1.modules.users.models.user_model import UserModel
from app.core.repositories.base import BaseRepository


class UserRepository(BaseRepository[UserModel]):
    """Repositorio especializado para la tabla `users`."""

    def __init__(self, db: Session) -> None:
        super().__init__(db=db, model=UserModel)

    def get_by_id(self, user_id: int) -> UserModel | None:
        statement = select(UserModel).where(UserModel.id == user_id)
        return self.db.execute(statement).scalar_one_or_none()

    def get_by_email(self, email: str) -> UserModel | None:
        statement = select(UserModel).where(UserModel.email == email)
        return self.db.execute(statement).scalar_one_or_none()

    def list_all(self, *, offset: int, limit: int) -> tuple[list[UserModel], int]:
        items_statement = select(UserModel).order_by(UserModel.id.desc()).offset(offset).limit(limit)
        total_statement = select(func.count()).select_from(UserModel)

        items = list(self.db.execute(items_statement).scalars().all())
        total = self.db.execute(total_statement).scalar_one()
        return items, total

    def create(
        self,
        *,
        full_name: str,
        email: str,
        hashed_password: str,
        is_active: bool = True,
        is_superuser: bool = False,
    ) -> UserModel:
        """Crea y persiste un usuario nuevo."""
        user = UserModel(
            full_name=full_name,
            email=email,
            hashed_password=hashed_password,
            is_active=is_active,
            is_superuser=is_superuser,
        )
        return self.save(user)
