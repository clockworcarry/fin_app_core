"""fix

Revision ID: 39e5169fe00c
Revises: 9d87f64757e0
Create Date: 2021-02-26 10:21:33.320778

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '39e5169fe00c'
down_revision = '9d87f64757e0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_company_metric_description_company_id', table_name='company_metric_description')
    op.drop_constraint('uq_company_metric_description_company_id', 'company_metric_description', type_='unique')
    op.drop_constraint('fk_company_metric_description_company_id_company', 'company_metric_description', type_='foreignkey')
    op.drop_column('company_metric_description', 'company_id')
    op.add_column('company_metric_description_note', sa.Column('company_id', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_company_metric_description_note_company_id'), 'company_metric_description_note', ['company_id'], unique=False)
    op.create_foreign_key(op.f('fk_company_metric_description_note_company_id_company'), 'company_metric_description_note', 'company', ['company_id'], ['id'], onupdate='CASCADE', ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(op.f('fk_company_metric_description_note_company_id_company'), 'company_metric_description_note', type_='foreignkey')
    op.drop_index(op.f('ix_company_metric_description_note_company_id'), table_name='company_metric_description_note')
    op.drop_column('company_metric_description_note', 'company_id')
    op.add_column('company_metric_description', sa.Column('company_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key('fk_company_metric_description_company_id_company', 'company_metric_description', 'company', ['company_id'], ['id'], onupdate='CASCADE', ondelete='CASCADE')
    op.create_unique_constraint('uq_company_metric_description_company_id', 'company_metric_description', ['company_id', 'code'])
    op.create_index('ix_company_metric_description_company_id', 'company_metric_description', ['company_id'], unique=False)
    # ### end Alembic commands ###
