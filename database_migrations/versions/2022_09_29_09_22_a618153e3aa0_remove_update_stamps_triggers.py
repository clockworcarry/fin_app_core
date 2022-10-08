"""remove update_stamps triggers

Revision ID: a618153e3aa0
Revises: 66347196da4f
Create Date: 2022-09-29 09:22:03.090076

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a618153e3aa0'
down_revision = '66347196da4f'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    conn.execute(       """
                            DROP TRIGGER IF EXISTS update_sector_update_stamp on sector;
                        """                   
                )
    conn.execute(       """
                            DROP TRIGGER IF EXISTS update_company_update_stamp on company;
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
                            DROP TRIGGER IF EXISTS update_company_sector_relation_update_stamp on company_sector_relation;
                        """                   
                )
    conn.execute(       """
                            DROP TRIGGER IF EXISTS update_log_update_stamp on log;
                        """                   
                )
    conn.execute(       """
                            DROP TRIGGER IF EXISTS update_stamp_company_quarterly_financial_data on company_financial_data;
                        """                   
                )
    conn.execute(       """
                            DROP TRIGGER IF EXISTS update_stamp_company_group on company_group;
                        """                   
                )
    conn.execute(       """
                            DROP TRIGGER IF EXISTS update_stamp_account_trade on account_trade;
                        """                   
                )


def downgrade():
    conn = op.get_bind()
    
    conn.execute(       """
                            CREATE TRIGGER update_sector_update_stamp BEFORE UPDATE OR INSERT
                            ON sector FOR EACH ROW EXECUTE PROCEDURE 
                            automatic_update_stamp_column();
                        """                   
                )
    conn.execute(       """
                            CREATE TRIGGER update_company_update_stamp BEFORE UPDATE OR INSERT
                            ON company FOR EACH ROW EXECUTE PROCEDURE 
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
                            CREATE TRIGGER update_company_sector_relation_update_stamp BEFORE UPDATE OR INSERT
                            ON company_sector_relation FOR EACH ROW EXECUTE PROCEDURE 
                            automatic_update_stamp_column();
                        """                   
                )
    conn.execute(       """
                            CREATE TRIGGER update_log_update_stamp BEFORE UPDATE OR INSERT
                            ON log FOR EACH ROW EXECUTE PROCEDURE 
                            automatic_update_stamp_column();
                        """                   
                )
    conn.execute(       """
                            CREATE TRIGGER update_stamp_company_quarterly_financial_data BEFORE UPDATE OR INSERT
                            ON company_financial_data FOR EACH ROW EXECUTE PROCEDURE 
                            automatic_update_stamp_column();
                        """                   
                )
    conn.execute(       """
                            CREATE TRIGGER update_stamp_company_group BEFORE UPDATE OR INSERT
                            ON company_group FOR EACH ROW EXECUTE PROCEDURE 
                            automatic_update_stamp_column();
                        """                   
                )
    conn.execute(       """
                            CREATE TRIGGER update_stamp_account_trade BEFORE UPDATE OR INSERT
                            ON account_trade FOR EACH ROW EXECUTE PROCEDURE 
                            automatic_update_stamp_column();
                        """                   
                )
