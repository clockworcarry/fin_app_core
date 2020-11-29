"""populate existing records update_stamp col with values

Revision ID: ac4fdae2309b
Revises: 4779be2af6fb
Create Date: 2020-11-26 22:28:19.878944

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ac4fdae2309b'
down_revision = '4779be2af6fb'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    conn.execute(       """
                            UPDATE state_info set update_stamp = current_timestamp
                        """                   
                )


def downgrade():
    conn = op.get_bind()
    conn.execute(       """
                            UPDATE state_info set update_stamp = NULL
                        """                   
                )
