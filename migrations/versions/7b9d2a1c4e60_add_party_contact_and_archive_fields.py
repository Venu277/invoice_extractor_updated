"""add party contact and archive fields

Revision ID: 7b9d2a1c4e60
Revises: fca048943767
Create Date: 2026-11-01
"""
from typing import Sequence, Union

from alembic import context, op
import sqlalchemy as sa


revision: str = "7b9d2a1c4e60"
down_revision: Union[str, Sequence[str], None] = "fca048943767"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    if context.is_offline_mode():
        with op.batch_alter_table("parties") as batch:
            batch.add_column(sa.Column("shipping_address", sa.String(length=500), nullable=True))
            batch.add_column(sa.Column("gst_registration_type", sa.String(length=32), nullable=False, server_default="unregistered"))
            batch.add_column(sa.Column("notes", sa.Text(), nullable=True))
            batch.add_column(sa.Column("is_archived", sa.Boolean(), nullable=False, server_default=sa.false()))
        return

    inspector = sa.inspect(op.get_bind())
    if "parties" not in inspector.get_table_names():
        return
    columns = {col["name"] for col in inspector.get_columns("parties")}
    with op.batch_alter_table("parties") as batch:
        if "shipping_address" not in columns:
            batch.add_column(sa.Column("shipping_address", sa.String(length=500), nullable=True))
        if "gst_registration_type" not in columns:
            batch.add_column(sa.Column("gst_registration_type", sa.String(length=32), nullable=False, server_default="unregistered"))
        if "notes" not in columns:
            batch.add_column(sa.Column("notes", sa.Text(), nullable=True))
        if "is_archived" not in columns:
            batch.add_column(sa.Column("is_archived", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.execute("UPDATE parties SET gst_registration_type = 'regular' WHERE gstin IS NOT NULL AND gstin != ''")


def downgrade() -> None:
    if context.is_offline_mode():
        with op.batch_alter_table("parties") as batch:
            batch.drop_column("is_archived")
            batch.drop_column("notes")
            batch.drop_column("gst_registration_type")
            batch.drop_column("shipping_address")
        return
    inspector = sa.inspect(op.get_bind())
    if "parties" not in inspector.get_table_names():
        return
    columns = {col["name"] for col in inspector.get_columns("parties")}
    with op.batch_alter_table("parties") as batch:
        for name in ("is_archived", "notes", "gst_registration_type", "shipping_address"):
            if name in columns:
                batch.drop_column(name)
