"""add creator_id column to classifications and metric descs

Revision ID: 204557a565f0
Revises: d0ba2dcdeb98
Create Date: 2022-08-26 08:48:19.840018

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '204557a565f0'
down_revision = 'd0ba2dcdeb98'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('account', sa.Column('disabled', sa.Boolean(), server_default=sa.text('false'), nullable=False))
    op.add_column('company_metric_classification', sa.Column('creator_id', sa.BigInteger(), nullable=True))
    op.create_foreign_key(op.f('fk_company_metric_classification_creator_id_account'), 'company_metric_classification', 'account', ['creator_id'], ['id'], ondelete='SET NULL')
    op.add_column('company_metric_description', sa.Column('creator_id', sa.BigInteger(), nullable=True))
    op.create_foreign_key(op.f('fk_company_metric_description_creator_id_account'), 'company_metric_description', 'account', ['creator_id'], ['id'], ondelete='SET NULL')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(op.f('fk_company_metric_description_creator_id_account'), 'company_metric_description', type_='foreignkey')
    op.drop_column('company_metric_description', 'creator_id')
    op.drop_constraint(op.f('fk_company_metric_classification_creator_id_account'), 'company_metric_classification', type_='foreignkey')
    op.drop_column('company_metric_classification', 'creator_id')
    op.drop_column('account', 'disabled')
    # ### end Alembic commands ###
