"""populate existing records (again) update_stamp col with values

Revision ID: b4f8d18d5ebc
Revises: ac4fdae2309b
Create Date: 2020-11-26 22:33:10.369885

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b4f8d18d5ebc'
down_revision = 'ac4fdae2309b'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    conn.execute(       """
                            UPDATE country_info set update_stamp = current_timestamp
                        """                   
                )


def downgrade():
    conn = op.get_bind()
    conn.execute(       """
                            UPDATE country_info set update_stamp = NULL
                        """                   
                )
