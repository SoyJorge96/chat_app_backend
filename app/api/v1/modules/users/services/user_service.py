"""Servicio del módulo `users`.

Aquí vive la lógica de negocio del dominio users.
"""

from app.api.v1.shared.dtos.pagination_dto import PaginationMeta
from app.api.v1.modules.users.dtos.user_dto import UserCreate, UserListResponse, UserResponse, UserUpdate
from app.api.v1.modules.users.repositories.user_repository import UserRepository
from app.core.exceptions import ConflictError, NotFoundError
from app.core.security import hash_password
from app.services.pagination import build_pagination, calculate_total_pages


class UserService:
    """Casos de uso del módulo `users`."""

    def __init__(self, repository: UserRepository) -> None:
        self.repository = repository

    def list_users(self, *, page: int, page_size: int) -> UserListResponse:
        pagination = build_pagination(page=page, page_size=page_size)
        users, total = self.repository.list_all(offset=pagination.offset, limit=pagination.limit)

        return UserListResponse(
            items=[UserResponse.model_validate(user) for user in users],
            meta=PaginationMeta(
                page=pagination.page,
                page_size=pagination.page_size,
                total=total,
                total_pages=calculate_total_pages(total=total, page_size=pagination.page_size),
            ),
        )

    def get_user(self, user_id: int) -> UserResponse:
        user = self.repository.get_by_id(user_id)
        if user is None:
            raise NotFoundError(detail=f"No existe un usuario con id={user_id}")

        return UserResponse.model_validate(user)

    def create_user(self, payload: UserCreate) -> UserResponse:
        existing_user = self.repository.get_by_email(str(payload.email))
        if existing_user is not None:
            raise ConflictError(detail="Ya existe un usuario con ese email")

        user = self.repository.create(
            full_name=payload.full_name,
            email=str(payload.email),
            hashed_password=hash_password(payload.password),
            is_active=payload.is_active,
        )
        return UserResponse.model_validate(user)

    def update_user(self, user_id: int, payload: UserUpdate) -> UserResponse:
        user = self.repository.get_by_id(user_id)
        if user is None:
            raise NotFoundError(detail=f"No existe un usuario con id={user_id}")

        data = payload.model_dump(exclude_unset=True)

        new_email = data.get("email")
        if new_email is not None:
            existing_user = self.repository.get_by_email(str(new_email))
            if existing_user is not None and existing_user.id != user.id:
                raise ConflictError(detail="El email ya está siendo usado por otro usuario")
            user.email = str(new_email)

        if "full_name" in data:
            user.full_name = data["full_name"]

        if "is_active" in data:
            user.is_active = data["is_active"]
        updated_user = self.repository.save(user)
        return UserResponse.model_validate(updated_user)
