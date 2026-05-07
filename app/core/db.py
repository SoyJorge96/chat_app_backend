"""Configuración de base de datos con SQLAlchemy.

Este archivo concentra todo lo relacionado con la infraestructura de BD:
- la clase `Base` de la que heredan los modelos ORM
- el `engine` de SQLAlchemy
- la fábrica de sesiones
- helpers para crear tablas y validar conexión

¿Por qué centralizar esto?
Porque la conexión a base de datos es un recurso transversal. Si cada módulo
creara su propio engine o su propia sesión, el proyecto se volvería difícil
de mantener y de testear.
"""

from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings


class Base(DeclarativeBase):
    """Clase base para todos los modelos ORM.

    Cada modelo del proyecto debe heredar de esta clase, por ejemplo:

    ```python
    class User(Base):
        __tablename__ = "users"
        ...
    ```

    Gracias a esto, SQLAlchemy y Alembic pueden descubrir todas las tablas
    registradas bajo un mismo metadata.
    """


# `engine` representa la conexión principal contra la base.
#
# `pool_pre_ping=True` hace una comprobación ligera antes de reutilizar una
# conexión del pool. Eso ayuda a detectar conexiones muertas y reduce errores
# típicos cuando PostgreSQL cierra conexiones inactivas.
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DB_ECHO,
    future=True,
    pool_pre_ping=True,
)


# `SessionLocal` es la fábrica que crea sesiones por request.
#
# Importante:
# - `autoflush=False` evita envíos automáticos inesperados.
# - `autocommit=False` obliga a hacer commit explícito.
#
# En otras palabras: nada se persiste “por accidente”.
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session)

def funcion_prueba():
    print("se esta ejecutando")

def create_db_and_tables() -> None:
    """Crea tablas usando `Base.metadata.create_all()`.

    ¿Cuándo sirve?
    - prototipos rápidos
    - ejemplos pequeños
    - pruebas locales muy simples

    ¿Cuándo NO conviene?
    - cuando ya trabajas con Alembic
    - cuando tienes varios entornos
    - cuando necesitas trazabilidad de cambios de esquema

    Nota importante:
    `import app.core.base` parece raro, pero es intencional. Ese archivo importa
    los modelos de los módulos para que queden registrados en `Base.metadata`
    antes de ejecutar `create_all()`.
    """
    import app.core.base  # noqa: F401

    Base.metadata.create_all(bind=engine)


def check_db_connection() -> None:
    """Prueba una conexión simple contra la base de datos.

    Ejecutamos `SELECT 1` porque es una consulta mínima y suficiente para saber
    si PostgreSQL responde.

    Beneficio:
    si la conexión está mal, la app falla al arrancar y no en mitad de una
    petición de usuario.
    """
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))


def get_db_session() -> Generator[Session, None, None]:
    """Abre una sesión de base de datos y la cierra al terminar el request.

    Este patrón es la base de inyección de dependencias del proyecto:

    router -> service -> repository -> session

    FastAPI ejecuta esta función por request cuando una dependencia la pide.
    `yield` entrega la sesión al resto de la cadena, y el `finally` garantiza
    que se cierre incluso si ocurre una excepción.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
