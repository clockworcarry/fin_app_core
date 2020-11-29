"""add stamp to company table

Revision ID: 94abbca64372
Revises: ed86e7f69152
Create Date: 2020-11-25 23:12:12.214243

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.schema import *


# revision identifiers, used by Alembic.
revision = '94abbca64372'
down_revision = 'ed86e7f69152'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('company', sa.Column('update_stamp', sa.DateTime(timezone=True), server_default=FetchedValue(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('company', 'update_stamp')
    # ### end Alembic commands ###