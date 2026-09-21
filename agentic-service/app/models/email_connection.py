from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    DateTime,
    ForeignKey,
    String,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)


class EmailConnection:
    """
    Read-only representation of the core-backend
    email_connections table.

    Agentic service does NOT own this table.
    """

    pass