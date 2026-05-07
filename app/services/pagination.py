"""Lógica genérica de paginación.

Todo lo que sea reutilizable entre módulos debería vivir fuera de
`app/api/v1/modules/...` para no duplicar código.

Este archivo resuelve una necesidad común:
- normalizar `page` y `page_size`
- calcular `offset` y `limit`
- calcular cuántas páginas hay en total
"""

from dataclasses import dataclass
from math import ceil


@dataclass(slots=True)
class Pagination:
    """Objeto interno con valores ya normalizados.

    - `page`: página pedida por el cliente
    - `page_size`: tamaño final permitido
    - `offset`: desde qué registro empezar en SQL
    - `limit`: cuántos registros traer
    """

    page: int
    page_size: int
    offset: int
    limit: int


def build_pagination(page: int, page_size: int, *, max_page_size: int = 100) -> Pagination:
    """Normaliza parámetros de paginación y calcula offset/limit.

    Ejemplo:
    - page=1, page_size=10 -> offset=0, limit=10
    - page=3, page_size=20 -> offset=40, limit=20

    También protege contra valores absurdos:
    - páginas menores que 1
    - tamaños mayores que el máximo permitido
    """
    normalized_page = max(page, 1)
    normalized_page_size = max(1, min(page_size, max_page_size))

    return Pagination(
        page=normalized_page,
        page_size=normalized_page_size,
        offset=(normalized_page - 1) * normalized_page_size,
        limit=normalized_page_size,
    )


def calculate_total_pages(total: int, page_size: int) -> int:
    """Calcula el total de páginas para una colección paginada."""
    if total == 0:
        return 0
    return ceil(total / page_size)
