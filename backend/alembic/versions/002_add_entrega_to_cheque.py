"""add entrega to cheque

Revision ID: 002
Revises: 001
Create Date: 2026-05-14
"""
from alembic import op
import sqlalchemy as sa

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("cheque", sa.Column("entrega", sa.String(200), nullable=True))


def downgrade() -> None:
    op.drop_column("cheque", "entrega")
