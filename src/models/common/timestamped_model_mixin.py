import arrow
import sqlalchemy as sa
from sqlalchemy import ext


class TimestampedModelMixin:
    """
    Ensures and maintains ``created_at`` and ``updated_at`` attributes on
    SQLAlchemy models.
    """

    @ext.declarative.declared_attr
    def created_at(cls):
        return sa.Column(
            sa.DateTime(timezone=True),
            default=lambda: arrow.utcnow().datetime,
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        )

    @ext.declarative.declared_attr
    def updated_at(cls):
        return sa.Column(
            sa.DateTime(timezone=True),
            default=lambda: arrow.utcnow().datetime,
            onupdate=lambda: arrow.utcnow().datetime,
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
            server_onupdate=sa.text("CURRENT_TIMESTAMP"),
        )
