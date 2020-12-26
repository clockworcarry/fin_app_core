"""chaneg company ticker length

Revision ID: 30474952299c
Revises: 8ba5741124b2
Create Date: 2020-11-29 16:30:39.697670

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '30474952299c'
down_revision = '8ba5741124b2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('company', 'ticker',
               existing_type=sa.VARCHAR(length=5),
               type_=sa.String(length=10),
               existing_nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('company', 'ticker',
               existing_type=sa.String(length=10),
               type_=sa.VARCHAR(length=5),
               existing_nullable=False)
    # ### end Alembic commands ###