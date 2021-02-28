"""add trigger new tbls

Revision ID: 8182e32dbf5a
Revises: c5ed198a4fc7
Create Date: 2021-02-25 16:52:25.065037

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8182e32dbf5a'
down_revision = 'c5ed198a4fc7'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    
    conn.execute(       """
                            CREATE TRIGGER update_stamp_company_metric_description_data BEFORE UPDATE OR INSERT
                            ON company_metric_description FOR EACH ROW EXECUTE PROCEDURE 
                            automatic_update_stamp_column();
                        """                   
                )


def downgrade():
    conn = op.get_bind()
    
    conn.execute(       """
                            DROP TRIGGER IF EXISTS update_stamp_company_metric_description_data on company_metric_description;
                        """                   
                )
