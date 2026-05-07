"""Entorno de ejecución de Alembic.

Este archivo es el puente entre Alembic y tu aplicación.

Su trabajo es decirle a Alembic:
- cómo encontrar la URL de la base de datos
- dónde está el metadata de SQLAlchemy
- qué modelos deben considerarse al autogenerar migraciones

En esta plantilla, la fuente de verdad es:
- configuración -> `app.core.config.settings`
- metadata ORM -> `app.core.db.Base.metadata`
- registro de modelos -> `app.core.base`
"""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.core.config import settings
from app.core.db import Base
import app.core.base  # noqa: F401

# `context.config` representa la configuración cargada desde `alembic.ini`.
config = context.config

# Si Alembic tiene archivo de logging, lo activamos.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Sobrescribimos aquí la URL placeholder del `alembic.ini` con la URL real
# que viene desde `.env` a través de `settings`.
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# `target_metadata` es la referencia que Alembic usa para comparar el estado
# actual de los modelos contra el estado registrado en migraciones.
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Ejecuta migraciones en modo offline.

    Este modo no abre una conexión real a la base. Se usa cuando Alembic genera
    SQL a partir de la metadata y la configuración.
    """
    context.configure(
        url=settings.DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        compare_server_default=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Ejecuta migraciones en modo online.

    Aquí sí se crea un engine temporal para conectarse realmente a PostgreSQL y
    aplicar o inspeccionar cambios de esquema.
    """
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = settings.DATABASE_URL

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        future=True,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
