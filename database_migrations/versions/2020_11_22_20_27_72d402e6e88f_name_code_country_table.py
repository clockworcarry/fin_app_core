"""name_code country table

Revision ID: 72d402e6e88f
Revises: 8f8bb0fb5a5e
Create Date: 2020-11-22 20:27:02.154244

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '72d402e6e88f'
down_revision = '8f8bb0fb5a5e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('country_info', sa.Column('name_info', sa.String(length=10), nullable=True))
    op.create_unique_constraint(op.f('uq_country_info_name_info'), 'country_info', ['name_info'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(op.f('uq_country_info_name_info'), 'country_info', type_='unique')
    op.drop_column('country_info', 'name_info')
    # ### end Alembic commands ###
