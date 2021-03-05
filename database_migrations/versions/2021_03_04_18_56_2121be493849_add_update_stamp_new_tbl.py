"""add update stamp new tbl

Revision ID: 2121be493849
Revises: c3b655948ceb
Create Date: 2021-03-04 18:56:25.433773

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2121be493849'
down_revision = 'c3b655948ceb'
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
