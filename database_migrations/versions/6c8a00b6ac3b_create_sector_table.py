"""create sector table

Revision ID: 6c8a00b6ac3b
Revises: 
Create Date: 2020-11-09 22:43:03.767280

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6c8a00b6ac3b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("sector",
                    sa.Column("id", sa.SmallInteger, primary_key=True),
                    sa.Column("name_code", sa.String(10), nullable=False),
                    sa.Column("name", sa.String(60), nullable=False),
                    sa.Column("locked", sa.Boolean, nullable=False, server_default="True")

    )


def downgrade():
    op.drop_table("sector")
