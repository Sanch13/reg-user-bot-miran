"""added colomn ticket on users's table

Revision ID: 737c2d6a46c2
Revises: 999f0669944d
Create Date: 2024-11-23 09:57:36.489157

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '737c2d6a46c2'
down_revision: Union[str, None] = '999f0669944d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('ticket', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'ticket')
    # ### end Alembic commands ###
