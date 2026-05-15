"""add pagare table

Revision ID: 004
Revises: 003
Create Date: 2026-05-15
"""
from alembic import op
import sqlalchemy as sa

revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE estado_pagare AS ENUM ('pendiente', 'cobrado', 'rechazado');
        EXCEPTION WHEN duplicate_object THEN null;
        END $$
    """)
    op.execute("""
        CREATE TABLE IF NOT EXISTS pagare (
            id SERIAL PRIMARY KEY,
            numero VARCHAR(20) NOT NULL,
            monto NUMERIC(14, 2) NOT NULL,
            vencimiento DATE NOT NULL,
            firmante VARCHAR(160),
            calle VARCHAR(200),
            localidad VARCHAR(100),
            estado estado_pagare NOT NULL DEFAULT 'pendiente',
            observaciones TEXT,
            raw_ocr_text TEXT,
            image_filename VARCHAR(255),
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """)


def downgrade() -> None:
    op.drop_table("pagare")
    op.execute("DROP TYPE IF EXISTS estado_pagare")
