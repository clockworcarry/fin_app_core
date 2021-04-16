"""add trigger stamp new tbl

Revision ID: 126654ba690f
Revises: 8c96c2b06ebc
Create Date: 2021-04-12 23:05:39.866126

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '126654ba690f'
down_revision = '8c96c2b06ebc'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    
    conn.execute(       """
                            CREATE TRIGGER update_stamp_account_trade BEFORE UPDATE OR INSERT
                            ON account_trade FOR EACH ROW EXECUTE PROCEDURE 
                            automatic_update_stamp_column();
                        """                   
                )


def downgrade():
    conn = op.get_bind()
    
    conn.execute(       """
                            DROP TRIGGER IF EXISTS update_stamp_account_trade on account_trade;
                        """                   
                )
