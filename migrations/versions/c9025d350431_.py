"""empty message

Revision ID: c9025d350431
Revises: e9cf17ba2270
Create Date: 2018-06-01 22:19:34.499564

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'c9025d350431'
down_revision = 'e9cf17ba2270'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('inventory_items', sa.Column('quantity_base', sa.Float(), nullable=True))
    op.drop_constraint('inventory_items_sku_uom_fkey', 'inventory_items', type_='foreignkey')
    op.drop_column('inventory_items', 'sku_uom')
    op.drop_column('inventory_items', 'quantity_issue')
    op.add_column('materials', sa.Column('uom_stock_id', sa.String(length=5), nullable=True))
    op.alter_column('materials', 'standard_uom_id',
               existing_type=sa.VARCHAR(length=5),
               nullable=True)
    op.alter_column('materials', 'uom_base_id',
               existing_type=sa.VARCHAR(length=5),
               nullable=False)
    op.create_foreign_key(None, 'materials', 'units_of_measures', ['uom_stock_id'], ['uom'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'materials', type_='foreignkey')
    op.alter_column('materials', 'uom_base_id',
               existing_type=sa.VARCHAR(length=5),
               nullable=True)
    op.alter_column('materials', 'standard_uom_id',
               existing_type=sa.VARCHAR(length=5),
               nullable=False)
    op.drop_column('materials', 'uom_stock_id')
    op.add_column('inventory_items', sa.Column('quantity_issue', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True))
    op.add_column('inventory_items', sa.Column('sku_uom', sa.VARCHAR(length=5), autoincrement=False, nullable=False))
    op.create_foreign_key('inventory_items_sku_uom_fkey', 'inventory_items', 'units_of_measures', ['sku_uom'], ['uom'])
    op.drop_column('inventory_items', 'quantity_base')
    # ### end Alembic commands ###
