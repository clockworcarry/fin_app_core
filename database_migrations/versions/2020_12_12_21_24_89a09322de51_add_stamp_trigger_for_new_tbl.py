"""add stamp trigger for new tbl

Revision ID: 89a09322de51
Revises: 451d94b90fdd
Create Date: 2020-12-12 21:24:35.179502

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '89a09322de51'
down_revision = '451d94b90fdd'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    
    conn.execute(       """
                            CREATE TRIGGER update_stamp_company_misc_info BEFORE UPDATE OR INSERT
                            ON company_misc_info FOR EACH ROW EXECUTE PROCEDURE 
                            automatic_update_stamp_column();
                        """                   
                )


def downgrade():
    conn = op.get_bind()
    
    conn.execute(       """
                            DROP TRIGGER IF EXISTS update_stamp_company_misc_info on company_misc_info;
                        """                   
                )
