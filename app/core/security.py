"""Utilidades compartidas de seguridad.

Este archivo concentra la parte técnica de autenticación:
- hash de contraseñas
- validación de contraseñas
- creación de access tokens
- creación de refresh tokens
- decodificación de JWT
- hash seguro de refresh tokens para persistirlos en DB

Importante:
- aquí NO va acceso a base de datos
- aquí NO va lógica HTTP
- aquí NO va lógica de negocio como “si el usuario está activo”

En resumen:
- `security.py` sabe de criptografía y tokens
- `auth/service.py` sabe de reglas de autenticación
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta
from typing import Any
from uuid import uuid4

import jwt
from jwt import InvalidTokenError

from app.api.v1.shared.utils.datetime_utils import current_datetime_tz, normalize_datetime
from app.core.config import settings

PASSWORD_HASH_ITERATIONS = 600_000


class TokenError(Exception):
    """Error técnico relacionado con tokens.

    Este error es interno de la capa de seguridad. Luego `auth/service.py`
    decide cómo traducirlo a una excepción de dominio/HTTP.
    """



def _generate_salt() -> str:
    """Genera una sal aleatoria para hashing de contraseñas."""
    return base64.urlsafe_b64encode(secrets.token_bytes(16)).decode("utf-8")



def hash_password(password: str) -> str:
    """Hashea una contraseña con PBKDF2-HMAC-SHA256.

    El valor final se guarda en formato:

    `pbkdf2_sha256$iteraciones$salt$hash`

    Esto permite verificar después sin guardar la contraseña real.
    """
    salt = _generate_salt()
    derived_key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        PASSWORD_HASH_ITERATIONS,
    )
    password_hash = base64.urlsafe_b64encode(derived_key).decode("utf-8")
    return f"pbkdf2_sha256${PASSWORD_HASH_ITERATIONS}${salt}${password_hash}"



def verify_password(password: str, stored_hash: str) -> bool:
    """Verifica si una contraseña coincide con su hash almacenado."""
    try:
        algorithm, iterations_raw, salt, password_hash = stored_hash.split("$", 3)
    except ValueError:
        return False

    if algorithm != "pbkdf2_sha256":
        return False

    derived_key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        int(iterations_raw),
    )
    computed_hash = base64.urlsafe_b64encode(derived_key).decode("utf-8")
    return hmac.compare_digest(computed_hash, password_hash)



def hash_token(token: str) -> str:
    """Hashea un token para no guardarlo en texto plano en la base."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()



def _build_token(
    *,
    subject: str,
    token_type: str,
    expires_delta: timedelta,
    extra_claims: dict[str, Any] | None = None,
) -> tuple[str, str, datetime]:
    """Crea un JWT firmado.

    Devuelve una tupla con:
    - token firmado
    - jti (identificador único del token)
    - fecha de expiración

    `jti` es útil para revocar refresh tokens guardándolos en DB.
    """
    now = current_datetime_tz()
    expires_at = now + expires_delta
    jti = str(uuid4())

    payload: dict[str, Any] = {
        "sub": subject,
        "type": token_type,
        "jti": jti,
        # Guardamos `iat` y `exp` como epoch seconds para que la validación del
        # JWT siga siendo correcta aunque la API exponga fechas sin UTC/Z.
        "iat": int(now.timestamp()),
        "exp": int(expires_at.timestamp()),
    }

    if extra_claims:
        payload.update(extra_claims)

    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    normalized_expires_at = normalize_datetime(expires_at)
    return token, jti, normalized_expires_at if normalized_expires_at is not None else expires_at.replace(tzinfo=None)



def create_access_token(*, subject: str) -> tuple[str, str, datetime]:
    """Crea un access token de vida corta."""
    return _build_token(
        subject=subject,
        token_type="access",
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )



def create_refresh_token(*, subject: str) -> tuple[str, str, datetime]:
    """Crea un refresh token de vida más larga."""
    return _build_token(
        subject=subject,
        token_type="refresh",
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )



def decode_token(token: str) -> dict[str, Any]:
    """Decodifica y valida un JWT firmado por esta aplicación."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except InvalidTokenError as exc:
        raise TokenError("Token inválido o expirado") from exc

    return payload
