"""update company misc info seq type

Revision ID: b2affe853001
Revises: 133eff1ba4b6
Create Date: 2021-01-23 12:47:48.428807

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b2affe853001'
down_revision = '133eff1ba4b6'
branch_labels = None
depends_on = None

def upgrade():
    conn = op.get_bind()
    
    conn.execute(       """
                            alter sequence company_misc_info_id_seq as bigint;
                        """                   
                )


def downgrade():
    conn = op.get_bind()
    
    conn.execute(       """
                            alter sequence company_misc_info_id_seq as bigint;
                        """                   
                )
