"""empty message

Revision ID: ee66599b7cb2
Revises: c372634e5a77
Create Date: 2018-07-24 22:44:31.627726

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ee66599b7cb2'
down_revision = 'c372634e5a77'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('materials', sa.Column('default_base_units_per_stock_unit', sa.Float(), nullable=True))
    op.drop_constraint('materials_standard_uom_id_fkey', 'materials', type_='foreignkey')
    op.drop_column('materials', 'standard_uom_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('materials', sa.Column('standard_uom_id', sa.VARCHAR(length=5), autoincrement=False, nullable=True))
    op.create_foreign_key('materials_standard_uom_id_fkey', 'materials', 'units_of_measures', ['standard_uom_id'], ['uom'])
    op.drop_column('materials', 'default_base_units_per_stock_unit')
    # ### end Alembic commands ###