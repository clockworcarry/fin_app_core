"""delete state info tbl

Revision ID: 9761c285cb91
Revises: 904e7631943e
Create Date: 2021-03-10 20:58:26.834980

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '9761c285cb91'
down_revision = '904e7631943e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_state_info_country_info_id', table_name='state_info')
    op.drop_table('state_info')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('state_info',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('country_info_id', sa.SMALLINT(), autoincrement=False, nullable=False),
    sa.Column('name', sa.VARCHAR(length=60), autoincrement=False, nullable=False),
    sa.Column('update_stamp', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['country_info_id'], ['country_info.id'], name='fk_state_info_country_info_id_country_info', onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name='pk_state_info'),
    sa.UniqueConstraint('name', name='uq_state_info_name')
    )
    op.create_index('ix_state_info_country_info_id', 'state_info', ['country_info_id'], unique=False)
    # ### end Alembic commands ###
