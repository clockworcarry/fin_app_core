"""add trigger stamp new tbl

Revision ID: 10f145d3959d
Revises: c7fd3782bc09
Create Date: 2021-03-01 20:38:36.777009

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '10f145d3959d'
down_revision = 'c7fd3782bc09'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    
    conn.execute(       """
                            CREATE TRIGGER update_stamp_company_metric_relation BEFORE UPDATE OR INSERT
                            ON company_metric_relation FOR EACH ROW EXECUTE PROCEDURE 
                            automatic_update_stamp_column();
                        """                   
                )


def downgrade():
    conn = op.get_bind()
    
    conn.execute(       """
                            DROP TRIGGER IF EXISTS update_stamp_company_metric_relation on company_metric_relation;
                        """                   
                )
