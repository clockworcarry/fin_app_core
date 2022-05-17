"""update_stamp trigger group tables

Revision ID: 880cdfda0cd2
Revises: a479c9da906a
Create Date: 2022-05-16 20:53:20.110260

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '880cdfda0cd2'
down_revision = 'a479c9da906a'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    
    conn.execute(       """
                            CREATE TRIGGER update_stamp_company_group BEFORE UPDATE OR INSERT
                            ON company_group FOR EACH ROW EXECUTE PROCEDURE 
                            automatic_update_stamp_column();
                        """                   
                )

    conn.execute(       """
                            CREATE TRIGGER update_stamp_company_group_relation BEFORE UPDATE OR INSERT
                            ON company_group_relation FOR EACH ROW EXECUTE PROCEDURE 
                            automatic_update_stamp_column();
                        """                   
                )


def downgrade():
    conn = op.get_bind()
    
    conn.execute(       """
                            DROP TRIGGER IF EXISTS update_stamp_company_group_relation on company_group_relation;
                        """                   
                )
    
    conn.execute(       """
                            DROP TRIGGER IF EXISTS update_stamp_company_group_relation on company_group_relation;
                        """                   
                )
