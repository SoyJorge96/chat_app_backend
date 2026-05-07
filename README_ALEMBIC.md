# Guía rápida de Alembic

Este archivo es **informativo**.  
La configuración ya quedó preparada, pero **no se ejecutó ningún comando de Alembic**.

---

## 1) Archivos que ya quedaron listos

- `alembic.ini`
- `alembic/env.py`
- `alembic/script.py.mako`
- `alembic/versions/`

Alembic toma:

- la URL desde `.env` usando `app/core/config.py`
- los modelos desde `app/core/base.py`

Por eso, cuando crees nuevos modelos, recuerda importarlos en:

```python
# app/core/base.py
from app.api.v1.modules.users.models import User  # noqa: F401
```

---

## 2) Recomendación importante

Si vas a trabajar con migraciones, usa:

```env
AUTO_CREATE_TABLES=false
```

Y asegúrate de tener configurada tu conexión real en:

```env
DATABASE_URL=postgresql+psycopg://...
```

Así evitas mezclar:

- `Base.metadata.create_all()`
- migraciones versionadas con Alembic

---

## 3) Comandos más usados

### Ver historial de migraciones

```bash
alembic history
```

### Ver la revisión actual aplicada en la base

```bash
alembic current
```

### Ver la última revisión disponible

```bash
alembic heads
```

### Crear una migración manual

```bash
alembic revision -m "create users table"
```

### Crear una migración automática desde los modelos

```bash
alembic revision --autogenerate -m "creacion de tabla roles y ajuste en relaciones"
```

### Aplicar todas las migraciones pendientes

```bash
alembic upgrade head
```

### Aplicar hasta una revisión específica

```bash
alembic upgrade <revision_id>
```

### Retroceder una migración

```bash
alembic downgrade -1
```

### Volver al estado inicial

```bash
alembic downgrade base
```

### Marcar la base como actual sin ejecutar cambios

```bash
alembic stamp head
```

---

## 4) Flujo recomendado en este proyecto

### Paso 1: crear o modificar modelos

Ejemplo:

- creas `app/api/v1/modules/properties/models.py`
- importas ese modelo en `app/core/base.py`

### Paso 2: generar migración

```bash
alembic revision --autogenerate -m "create properties table"
```

### Paso 3: revisar el archivo generado

Siempre revisa lo que Alembic generó en:

```text
alembic/versions/
```

Especialmente valida:

- nombres de tablas
- índices
- constraints
- `nullable=True/False`
- cambios de tipo

### Paso 4: aplicar migración

```bash
alembic upgrade head
```

---

## 5) Ejemplo real de flujo

Supón que agregas este modelo:

```python
class Property(Base):
    __tablename__ = "properties"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    price: Mapped[float] = mapped_column(nullable=False)
```

Y luego lo registras en:

```python
# app/core/base.py
from app.api.v1.modules.properties.models import Property  # noqa: F401
```

El flujo sería:

```bash
alembic revision --autogenerate -m "create properties table"
alembic upgrade head
```

---

## 6) Qué archivo toca qué cosa

### `alembic.ini`

Configuración general de Alembic.

### `alembic/env.py`

Conecta Alembic con:

- la URL de PostgreSQL
- el metadata de SQLAlchemy
- los modelos importados en `app/core/base.py`

### `alembic/versions/*.py`

Aquí vivirán las migraciones reales del proyecto.

### `app/core/base.py`

Registro central de modelos para que Alembic los detecte.

---

## 7) Buenas prácticas

- No confíes ciegamente en `--autogenerate`; revisa siempre el archivo.
- No mezcles `AUTO_CREATE_TABLES=true` con Alembic en un entorno formal.
- Haz migraciones pequeñas y con nombres claros.
- Si renombras columnas o tablas, revisa manualmente la migración.
- Antes de producción, prueba `upgrade` y `downgrade` en una base de desarrollo.

---

## 8) Nota final

Ya quedó la base preparada para usar Alembic, pero:

- **no se creó ninguna migración**
- **no se ejecutó ningún upgrade**
- **no se tocó la base de datos**

Todo quedó listo solo como configuración y guía de uso.
