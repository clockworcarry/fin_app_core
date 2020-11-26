"""Create trigger company_update_stamp

Revision ID: ed86e7f69152
Revises: e1257e56e176
Create Date: 2020-11-25 22:44:46.650361

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ed86e7f69152'
down_revision = 'e1257e56e176'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    conn.execute(       """
                            CREATE TRIGGER update_company_update_stamp BEFORE UPDATE OR INSERT
                            ON company FOR EACH ROW EXECUTE PROCEDURE 
                            automatic_update_stamp_column();
                        """                   
                )


def downgrade():
    conn = op.get_bind()
    conn.execute(       """
                            DROP TRIGGER IF EXISTS update_company_update_stamp;
                        """                   
                )
