"""Create update_change_timestamp_function

Revision ID: e1257e56e176
Revises: f3ec71fe86e6
Create Date: 2020-11-25 22:16:07.471270

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e1257e56e176'
down_revision = 'f3ec71fe86e6'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    conn.execute(       """
                            CREATE OR REPLACE FUNCTION automatic_update_stamp_column()
                            RETURNS TRIGGER AS $$
                            BEGIN
                                NEW.update_stamp = now(); 
                                RETURN NEW;
                            END;
                            $$ language 'plpgsql';
                        """                   
                )


def downgrade():
    conn = op.get_bind()
    conn.execute(text(
                        """
                            DROP FUNCTION IF EXISTS automatic_update_stamp_column();
                        """
                    )
                )
