"""add scanner fields to cheque

Revision ID: 001
Revises:
Create Date: 2026-05-14
"""
from alembic import op
import sqlalchemy as sa

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("cheque", sa.Column("monto_letras", sa.Text(), nullable=True))
    op.add_column("cheque", sa.Column("pagador_cuit", sa.String(20), nullable=True))
    op.add_column("cheque", sa.Column("beneficiario", sa.String(200), nullable=True))
    op.add_column("cheque", sa.Column("sucursal", sa.String(100), nullable=True))
    op.add_column("cheque", sa.Column("localidad", sa.String(100), nullable=True))
    op.add_column("cheque", sa.Column("es_cpd", sa.Boolean(), nullable=False, server_default="false"))
    op.add_column("cheque", sa.Column("discrepancia_monto", sa.Boolean(), nullable=False, server_default="false"))
    op.add_column("cheque", sa.Column("raw_ocr_text", sa.Text(), nullable=True))
    op.add_column("cheque", sa.Column("raw_json", sa.Text(), nullable=True))
    op.add_column("cheque", sa.Column("image_filename", sa.String(255), nullable=True))


def downgrade() -> None:
    op.drop_column("cheque", "image_filename")
    op.drop_column("cheque", "raw_json")
    op.drop_column("cheque", "raw_ocr_text")
    op.drop_column("cheque", "discrepancia_monto")
    op.drop_column("cheque", "es_cpd")
    op.drop_column("cheque", "localidad")
    op.drop_column("cheque", "sucursal")
    op.drop_column("cheque", "beneficiario")
    op.drop_column("cheque", "pagador_cuit")
    op.drop_column("cheque", "monto_letras")
