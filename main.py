from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.db import funcion_prueba, check_db_connection
from app.core.config import settings
from app.core.exception_handlers import register_exception_handlers
from app.api.v1.router import router as api_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    funcion_prueba()
    if settings.CHECK_DB_ON_STARTUP:
        check_db_connection()
    yield


def create_application() -> FastAPI:

    app = FastAPI(title="Chat app", version="1.0", debug=True, lifespan=lifespan)

    cors_origins = settings.get_cors_origins()

    # CORS controla qué frontends pueden llamar la API desde el navegador.
    #
    # Si usas `*`, FastAPI no debería combinarlo con credenciales abiertas.
    # Por eso `allow_credentials` solo se activa cuando NO estamos usando `*`.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=("*" not in cors_origins),
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Registramos manejadores globales para transformar excepciones del dominio
    # en respuestas HTTP consistentes.
    register_exception_handlers(app)

    app.include_router(api_router, prefix=settings.API_PREFIX)

    @app.get("/", tags=["Root"])
    def read_root() -> dict[str, str]:
        """Endpoint mínimo para comprobar que la aplicación arrancó.

        No representa lógica de negocio. Solo sirve como punto de verificación
        rápida para saber que la API está viva.
        """
        return {
            "project": settings.PROJECT_NAME,
            "version": settings.PROJECT_VERSION,
            "message": "Plantilla FastAPI modular lista",
        }

    return app


app = create_application()
