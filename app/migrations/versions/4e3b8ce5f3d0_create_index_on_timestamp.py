"""Create index on timestamp

Revision ID: 4e3b8ce5f3d0
Revises: 347d00318b56
Create Date: 2025-04-10 13:01:59.832225

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "4e3b8ce5f3d0"
down_revision: Union[str, None] = "347d00318b56"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "detections_new",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "timestamp",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            default=sa.func.now(),
        ),
        sa.Column("image_path", sa.String(), nullable=False),
        sa.Column("x", sa.Integer, nullable=False),
        sa.Column("y", sa.Integer, nullable=False),
        sa.Column("width", sa.Integer, nullable=False),
        sa.Column("height", sa.Integer, nullable=False),
    )

    op.execute("INSERT INTO detections_new SELECT * FROM detections")

    op.drop_table("detections")

    op.rename_table("detections_new", "detections")

    op.create_index(
        op.f("ix_detections_timestamp"), "detections", ["timestamp"], unique=False
    )


def downgrade() -> None:
    op.create_table(
        "detections_old",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("timestamp", sa.DATETIME(), nullable=False, default=sa.func.now()),
        sa.Column("image_path", sa.String(), nullable=False),
        sa.Column("x", sa.Integer, nullable=False),
        sa.Column("y", sa.Integer, nullable=False),
        sa.Column("width", sa.Integer, nullable=False),
        sa.Column("height", sa.Integer, nullable=False),
    )

    op.execute("INSERT INTO detections_old SELECT * FROM detections")

    op.drop_table("detections")

    op.rename_table("detections_old", "detections")

    op.drop_index(op.f("ix_detections_timestamp"), table_name="detections")
