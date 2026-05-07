

from pydantic import BaseModel


class PaginationMeta(BaseModel):
    """Metadatos estándar para respuestas paginadas."""

    page: int
    page_size: int
    total: int
    total_pages: int