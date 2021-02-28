"""note_data stamp trigger

Revision ID: 66586ad2b1b1
Revises: 8a6a8989d9b1
Create Date: 2021-02-25 20:41:20.563228

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '66586ad2b1b1'
down_revision = '8a6a8989d9b1'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    
    conn.execute(       """
                            CREATE TRIGGER update_stamp_company_metric_description_note BEFORE UPDATE OR INSERT
                            ON company_metric_description_note FOR EACH ROW EXECUTE PROCEDURE 
                            automatic_update_stamp_column();
                        """                   
                )


def downgrade():
    conn = op.get_bind()
    
    conn.execute(       """
                            DROP TRIGGER IF EXISTS update_stamp_company_metric_description_note on company_metric_description_note;
                        """                   
                )
