"""empty message

Revision ID: 097c5812873f
Revises: bd97958ce114
Create Date: 2018-05-31 22:15:31.697937

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '097c5812873f'
down_revision = 'bd97958ce114'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key(None, 'consumption_plan_items', 'inventories', ['inventory_id'], ['id'])
    op.create_foreign_key(None, 'consumption_plans', 'users', ['creator_id'], ['id'])
    op.add_column('inventory_items', sa.Column('title', sa.String(length=160), nullable=True))
    op.drop_index('ix_material_forecasts_consumption_plan_item_id', table_name='material_forecasts')
    op.drop_index('ix_material_forecasts_diet_plan_item_id', table_name='material_forecasts')
    op.create_foreign_key(None, 'material_forecasts', 'inventories', ['inventory_id'], ['id'])
    op.create_foreign_key(None, 'material_forecasts', 'diet_plan_items', ['diet_plan_item_id'], ['id'])
    op.create_foreign_key(None, 'meals', 'users', ['owner_id'], ['id'])
    op.add_column('shopping_order_items', sa.Column('title', sa.String(length=80), nullable=True))
    op.create_foreign_key(None, 'shopping_orders', 'users', ['creator_id'], ['id'])
    op.create_foreign_key(None, 'user_group_association', 'users', ['user_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'user_group_association', type_='foreignkey')
    op.drop_constraint(None, 'shopping_orders', type_='foreignkey')
    op.drop_column('shopping_order_items', 'title')
    op.drop_constraint(None, 'meals', type_='foreignkey')
    op.drop_constraint(None, 'material_forecasts', type_='foreignkey')
    op.drop_constraint(None, 'material_forecasts', type_='foreignkey')
    op.create_index('ix_material_forecasts_diet_plan_item_id', 'material_forecasts', ['diet_plan_item_id'], unique=False)
    op.create_index('ix_material_forecasts_consumption_plan_item_id', 'material_forecasts', ['consumption_plan_item_id'], unique=False)
    op.drop_column('inventory_items', 'title')
    op.drop_constraint(None, 'consumption_plans', type_='foreignkey')
    op.drop_constraint(None, 'consumption_plan_items', type_='foreignkey')
    # ### end Alembic commands ###