"""Add date triggers to new tables

Revision ID: e7ccdd1e57fd
Revises: c532c87952fd
Create Date: 2020-12-06 16:40:01.262883

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e7ccdd1e57fd'
down_revision = 'c532c87952fd'
branch_labels = None
depends_on = None

def upgrade():
    conn = op.get_bind()
    
    conn.execute(       """
                            CREATE TRIGGER update_stamp_balance_sheet_data BEFORE UPDATE OR INSERT
                            ON balance_sheet_data FOR EACH ROW EXECUTE PROCEDURE 
                            automatic_update_stamp_column();
                        """                   
                )

    conn.execute(       """
                            CREATE TRIGGER update_stamp_income_statement_data BEFORE UPDATE OR INSERT
                            ON income_statement_data FOR EACH ROW EXECUTE PROCEDURE 
                            automatic_update_stamp_column();
                        """                   
                )

    conn.execute(       """
                            CREATE TRIGGER update_stamp_cash_flow_statement_data BEFORE UPDATE OR INSERT
                            ON cash_flow_statement_data FOR EACH ROW EXECUTE PROCEDURE 
                            automatic_update_stamp_column();
                        """                   
                )


def downgrade():
    conn = op.get_bind()
    
    conn.execute(       """
                            DROP TRIGGER IF EXISTS update_stamp_balance_sheet_data on balance_sheet_data;
                        """                   
                )

    conn.execute(       """
                            DROP TRIGGER IF EXISTS update_stamp_income_statement_data on balance_sheet_data;
                        """                   
                )

    conn.execute(       """
                            DROP TRIGGER IF EXISTS update_stamp_cash_flow_statement_data on balance_sheet_data;
                        """                   
                )
