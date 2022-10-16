"""add primary keys to company_sector_relation_tbl

Revision ID: 22317c1e0fff
Revises: ef5a9af4f132
Create Date: 2022-10-15 14:51:41.019660

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '22317c1e0fff'
down_revision = 'ef5a9af4f132'
branch_labels = None
depends_on = None


def upgrade():
    op.create_primary_key('pk_company_sector_relation', 'company_sector_relation', ['company_business_segment_id', 'sector_id'])


def downgrade():
    op.drop_constraint('pk_company_sector_relation', 'company_sector_relation', type_='primary')
