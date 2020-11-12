"""Update country_info pkey type

Revision ID: e9477c0bd6bf
Revises: 77fb7348217c
Create Date: 2020-11-11 22:25:23.182410

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e9477c0bd6bf'
down_revision = '77fb7348217c'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(table_name="country_info", column_name="id", existing_type=sa.Integer, type_=sa.SmallInteger)


def downgrade():
    op.alter_column(table_name="country_info", column_name="id", existing_type=sa.SmallInteger, type_=sa.Integer)
