"""create update_stamp triggers on all tables

Revision ID: b78b42e16692
Revises: c5a260d9d49e
Create Date: 2020-11-26 22:38:05.004849

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b78b42e16692'
down_revision = 'c5a260d9d49e'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    
    conn.execute(       """
                            CREATE TRIGGER update_company_exchange_relation_update_stamp BEFORE UPDATE OR INSERT
                            ON company_exchange_relation FOR EACH ROW EXECUTE PROCEDURE 
                            automatic_update_stamp_column();
                        """                   
                )

    conn.execute(       """
                            CREATE TRIGGER update_country_info_update_stamp BEFORE UPDATE OR INSERT
                            ON country_info FOR EACH ROW EXECUTE PROCEDURE 
                            automatic_update_stamp_column();
                        """                   
                )

    conn.execute(       """
                            CREATE TRIGGER update_exchange_update_stamp BEFORE UPDATE OR INSERT
                            ON exchange FOR EACH ROW EXECUTE PROCEDURE 
                            automatic_update_stamp_column();
                        """                   
                )

    conn.execute(       """
                            CREATE TRIGGER update_industry_update_stamp BEFORE UPDATE OR INSERT
                            ON industry FOR EACH ROW EXECUTE PROCEDURE 
                            automatic_update_stamp_column();
                        """                   
                )

    conn.execute(       """
                            CREATE TRIGGER update_sector_update_stamp BEFORE UPDATE OR INSERT
                            ON sector FOR EACH ROW EXECUTE PROCEDURE 
                            automatic_update_stamp_column();
                        """                   
                )

    conn.execute(       """
                            CREATE TRIGGER update_state_info_update_stamp BEFORE UPDATE OR INSERT
                            ON state_info FOR EACH ROW EXECUTE PROCEDURE 
                            automatic_update_stamp_column();
                        """                   
                )

    conn.execute(       """
                            CREATE TRIGGER update_sub_industry_update_stamp BEFORE UPDATE OR INSERT
                            ON sub_industry FOR EACH ROW EXECUTE PROCEDURE 
                            automatic_update_stamp_column();
                        """                   
                )


def downgrade():
    conn = op.get_bind()
    
    conn.execute(       """
                            DROP TRIGGER IF EXISTS update_company_exchange_relation_update_stamp on company_exchange_relation;
                        """                   
                )

    conn.execute(       """
                            DROP TRIGGER IF EXISTS update_country_info_update_stamp on country_info;
                        """                   
                )

    conn.execute(       """
                            DROP TRIGGER IF EXISTS update_exchange_update_stamp on exchange;
                        """                   
                )

    conn.execute(       """
                            DROP TRIGGER IF EXISTS update_industry_update_stamp on industry;
                        """                   
                )

    conn.execute(       """
                            DROP TRIGGER IF EXISTS update_sector_update_stamp on sector;
                        """                   
                )

    conn.execute(       """
                            DROP TRIGGER IF EXISTS update_sub_industry_update_stamp on sub_industry;
                        """                   
                )
