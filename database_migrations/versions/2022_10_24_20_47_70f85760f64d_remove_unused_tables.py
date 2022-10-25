"""remove unused tables

Revision ID: 70f85760f64d
Revises: 29a2cfc8fc42
Create Date: 2022-10-24 20:47:03.151384

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '70f85760f64d'
down_revision = '29a2cfc8fc42'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_exchange_country_info_id', table_name='exchange')
    op.drop_table('company_exchange_relation')
    op.drop_table('exchange')
    op.drop_table('country_info')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('country_info',
    sa.Column('id', sa.SMALLINT(), server_default=sa.text("nextval('country_info_id_seq'::regclass)"), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(length=60), autoincrement=False, nullable=False),
    sa.Column('currency', sa.VARCHAR(length=10), autoincrement=False, nullable=False),
    sa.Column('name_code', sa.VARCHAR(length=10), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='pk_country_info'),
    sa.UniqueConstraint('name', name='uq_country_info_name'),
    sa.UniqueConstraint('name_code', name='uq_country_info_name_code'),
    postgresql_ignore_search_path=False
    )
    op.create_table('exchange',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('country_info_id', sa.SMALLINT(), autoincrement=False, nullable=False),
    sa.Column('name_code', sa.VARCHAR(length=10), autoincrement=False, nullable=False),
    sa.Column('name', sa.VARCHAR(length=60), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['country_info_id'], ['country_info.id'], name='fk_exchange_country_info_id_country_info', onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name='pk_exchange'),
    sa.UniqueConstraint('name', name='uq_exchange_name'),
    sa.UniqueConstraint('name_code', name='uq_exchange_name_code')
    )
    op.create_table('company_exchange_relation',
    sa.Column('company_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('exchange_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['company_id'], ['company.id'], name='fk_company_exchange_relation_company_id_company', onupdate='CASCADE', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['exchange_id'], ['exchange.id'], name='fk_company_exchange_relation_exchange_id_exchange', onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('company_id', 'exchange_id', name='pk_company_exchange_relation')
    )


    op.create_index('ix_exchange_country_info_id', 'exchange', ['country_info_id'], unique=False)
    # ### end Alembic commands ###
