"""Repositorio base reutilizable.

Este archivo existe para evitar repetir la misma lógica en cada repositorio.

¿Qué tipo de lógica conviene centralizar aquí?
- `save()` con commit/rollback/refresh
- `delete()` con commit/rollback
- helpers comunes de persistencia

¿Qué NO conviene meter aquí?
- reglas de negocio específicas del dominio
- queries particulares de `users`, `properties`, etc.

Es decir:
- lo común va aquí
- lo específico va en cada repositorio del módulo
"""

from typing import Generic, TypeVar

from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    """Clase base para reducir código repetido entre repositorios."""

    def __init__(self, db: Session, model: type[ModelType]) -> None:
        # `db` es la sesión del request actual.
        self.db = db

        # `model` deja explícito con qué entidad trabaja el repositorio.
        # No es obligatorio para todos los diseños, pero en una plantilla ayuda
        # a hacer más claro el propósito de la clase.
        self.model = model

    def save(self, instance: ModelType) -> ModelType:
        """Guarda una entidad y devuelve su estado final.

        Flujo:
        1. se agrega al contexto de sesión
        2. se hace commit
        3. se hace refresh para traer cambios finales desde la BD

        El `rollback()` en el `except` es importante: si una transacción falla,
        la sesión no debe quedar “rota” para el resto del request.
        """
        try:
            self.db.add(instance)
            self.db.commit()
            self.db.refresh(instance)
            return instance
        except Exception:
            self.db.rollback()
            raise

    def delete(self, instance: ModelType) -> None:
        """Elimina una entidad de forma segura."""
        try:
            self.db.delete(instance)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
