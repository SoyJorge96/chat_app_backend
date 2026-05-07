"""Configuración centralizada del proyecto.

¿Por qué existe este archivo?
- Para que toda la aplicación lea su configuración desde un solo lugar.
- Para no tener `os.getenv()` regado por routers, services o repositorios.
- Para dejar claro qué valores pueden tener un default razonable y cuáles
  deben venir obligatoriamente del entorno.

Regla práctica usada aquí:
- Valores estructurales y poco sensibles -> pueden tener default en código.
- Valores sensibles o que cambian entre entornos -> deben venir desde `.env`.

Ejemplo claro:
- `PROJECT_NAME` puede tener default.
- `DATABASE_URL` y `SECRET_KEY` NO deberían estar quemadas en el código.
"""

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Objeto único de configuración de la aplicación.

    FastAPI no lee `.env` por sí sola. Quien lo hace aquí es Pydantic Settings.
    Cuando se instancia esta clase:

    1. Busca variables en el entorno del sistema.
    2. Luego en el archivo `.env` indicado en `model_config`.
    3. Si no encuentra una variable, usa el valor por defecto del atributo.

    Ojo:
    - Si un campo NO tiene valor por defecto, entonces es obligatorio.
    - Si falta un campo obligatorio, la aplicación fallará al arrancar.

    Esa falla temprana es buena práctica para no descubrir errores de
    configuración en mitad de una petición real.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    PROJECT_NAME: str = "MI API"
    PROJECT_VERSION: str = "0.1.0"

    API_PREFIX: str = "/api"
    API_V1_PREFIX: str = "/v1"

    DATABASE_URL: str

    DEBUG: bool = False
    DB_ECHO: bool = False
    AUTO_CREATE_TABLES: bool = False
    CHECK_DB_ON_STARTUP: bool = True

    # Zona horaria base del proyecto para fechas mostradas al usuario.
    # La usamos para evitar responder siempre en UTC (`Z`) cuando tú quieres
    # trabajar con fechas actuales tipo `datetime.now()`.
    APP_TIMEZONE: str = "America/Bogota"

    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"

    # ------------------------------------------------------------------
    # Autenticación / Seguridad
    # ------------------------------------------------------------------
    # `SECRET_KEY` es obligatoria porque firma tokens JWT. Debe venir del
    # entorno para que cada despliegue tenga su propio secreto.
    SECRET_KEY: str

    # HS256 es suficiente para una plantilla base con JWT firmados por la API.
    JWT_ALGORITHM: str = "HS256"

    # Access token corto = menor ventana de riesgo si se roba.
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Refresh token más largo para no pedir login tan seguido.
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    @field_validator("API_PREFIX", "API_V1_PREFIX")
    @classmethod
    def validate_prefix(cls, value: str) -> str:
        """Asegura que los prefijos empiecen por `/`."""
        if not value.startswith("/"):
            raise ValueError("Los prefijos de la API deben empezar con '/'")

        if len(value) > 1:
            return value.rstrip("/")
        return value

    def get_cors_origins(self) -> list[str]:
        """Convierte `CORS_ORIGINS` a lista para FastAPI."""
        raw_value = self.CORS_ORIGINS.strip()

        if raw_value == "":
            return []

        if raw_value == "*":
            return ["*"]

        return [origin.strip() for origin in raw_value.split(",") if origin.strip()]


settings = Settings()
