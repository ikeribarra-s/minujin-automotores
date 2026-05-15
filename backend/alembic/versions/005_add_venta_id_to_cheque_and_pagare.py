"""add venta_id to cheque and pagare

Revision ID: 005
Revises: 004
Create Date: 2026-05-15
"""
from alembic import op
import sqlalchemy as sa

revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("cheque", sa.Column("venta_id", sa.Integer(), nullable=True))
    op.create_foreign_key("fk_cheque_venta", "cheque", "venta", ["venta_id"], ["id"])
    op.add_column("pagare", sa.Column("venta_id", sa.Integer(), nullable=True))
    op.create_foreign_key("fk_pagare_venta", "pagare", "venta", ["venta_id"], ["id"])


def downgrade() -> None:
    op.drop_constraint("fk_pagare_venta", "pagare", type_="foreignkey")
    op.drop_column("pagare", "venta_id")
    op.drop_constraint("fk_cheque_venta", "cheque", type_="foreignkey")
    op.drop_column("cheque", "venta_id")
