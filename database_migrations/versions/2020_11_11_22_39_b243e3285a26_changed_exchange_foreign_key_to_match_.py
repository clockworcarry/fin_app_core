"""Changed Exchange foreign key to match country_info id type

Revision ID: b243e3285a26
Revises: e9477c0bd6bf
Create Date: 2020-11-11 22:39:40.729060

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b243e3285a26'
down_revision = 'e9477c0bd6bf'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(table_name="exchange", column_name="country_info_id", existing_type=sa.Integer, type_=sa.SmallInteger)


def downgrade():
    op.alter_column(table_name="exchange", column_name="country_info_id", existing_type=sa.SmallInteger, type_=sa.Integer)
