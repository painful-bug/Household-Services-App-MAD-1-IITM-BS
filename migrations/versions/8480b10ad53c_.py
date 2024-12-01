"""empty message

Revision ID: 8480b10ad53c
Revises: 008274e427ee
Create Date: 2024-11-27 14:22:04.854696

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8480b10ad53c'
down_revision = '008274e427ee'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('docs', schema=None) as batch_op:
        batch_op.add_column(sa.Column('professional_id', sa.Integer(), nullable=False))
        batch_op.create_foreign_key(
            'fk_docs_professional_id',
            'professionals',
            ['professional_id'],
            ['id']
        )

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('docs', schema=None) as batch_op:
        batch_op.drop_constraint('fk_docs_professional_id', type_='foreignkey')
        batch_op.drop_column('professional_id')

    # ### end Alembic commands ###