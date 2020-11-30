"""create update_stamp trigger for company_sector_relation tbl

Revision ID: 6e401f88dfc4
Revises: d80ba31f7a33
Create Date: 2020-11-29 14:12:02.636205

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6e401f88dfc4'
down_revision = 'd80ba31f7a33'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    
    conn.execute(       """
                            CREATE TRIGGER update_company_sector_relation_update_stamp BEFORE UPDATE OR INSERT
                            ON company_sector_relation FOR EACH ROW EXECUTE PROCEDURE 
                            automatic_update_stamp_column();
                        """                   
                )


def downgrade():
    conn = op.get_bind()
    
    conn.execute(       """
                            DROP TRIGGER IF EXISTS update_company_sector_relation_update_stamp on company_sector_relation;
                        """                   
                )
