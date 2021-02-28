"""add trigger update stamp quarteryfinancialdata tbl

Revision ID: 16f6aeb9ee5e
Revises: 9602723d194b
Create Date: 2021-02-17 21:56:51.449456

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '16f6aeb9ee5e'
down_revision = '9602723d194b'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    
    conn.execute(       """
                            CREATE TRIGGER update_stamp_company_quarterly_financial_data BEFORE UPDATE OR INSERT
                            ON company_quarterly_financial_data FOR EACH ROW EXECUTE PROCEDURE 
                            automatic_update_stamp_column();
                        """                   
                )


def downgrade():
    conn = op.get_bind()
    
    conn.execute(       """
                            DROP TRIGGER IF EXISTS update_stamp_company_quarterly_financial_data on company_quarterly_financial_data;
                        """                   
                )
