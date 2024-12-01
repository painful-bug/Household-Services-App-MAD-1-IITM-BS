"""empty message

Revision ID: 008274e427ee
Revises: e7505c0e230f
Create Date: 2024-11-27 14:12:28.582776

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '008274e427ee'
down_revision = 'e7505c0e230f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('docs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('filename', sa.String(length=50), nullable=True),
    sa.Column('data', sa.LargeBinary(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('docs')
    # ### end Alembic commands ###