"""Servicio del subdominio de roles y permisos."""

from app.api.v1.modules.users.repositories.role_repository import RoleRepository



class RoleService:
    """Casos de uso para membresías y permisos por rol."""

    def __init__(self, repository: RoleRepository) -> None:
        self.repository = repository

