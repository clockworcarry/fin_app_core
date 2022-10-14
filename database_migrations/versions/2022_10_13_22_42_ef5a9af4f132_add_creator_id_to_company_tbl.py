"""add creator_id to company tbl

Revision ID: ef5a9af4f132
Revises: 097aa9b87fe4
Create Date: 2022-10-13 22:42:20.849722

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ef5a9af4f132'
down_revision = '097aa9b87fe4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('company', sa.Column('creator_id', sa.BigInteger(), nullable=False))
    op.create_foreign_key(op.f('fk_company_creator_id_account'), 'company', 'account', ['creator_id'], ['id'], onupdate='CASCADE', ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(op.f('fk_company_creator_id_account'), 'company', type_='foreignkey')
    op.drop_column('company', 'creator_id')
    # ### end Alembic commands ###
