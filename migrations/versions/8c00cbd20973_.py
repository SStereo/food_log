"""empty message

Revision ID: 8c00cbd20973
Revises: 
Create Date: 2018-05-15 13:21:14.464174

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8c00cbd20973'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(op.f('ix_ingredients_food_id'), 'ingredients', ['food_id'], unique=False)
    op.create_index(op.f('ix_ingredients_meal_id'), 'ingredients', ['meal_id'], unique=False)
    op.create_index(op.f('ix_inventory_items_food_id'), 'inventory_items', ['food_id'], unique=False)
    op.create_index(op.f('ix_inventory_items_good_id'), 'inventory_items', ['good_id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_inventory_items_good_id'), table_name='inventory_items')
    op.drop_index(op.f('ix_inventory_items_food_id'), table_name='inventory_items')
    op.drop_index(op.f('ix_ingredients_meal_id'), table_name='ingredients')
    op.drop_index(op.f('ix_ingredients_food_id'), table_name='ingredients')
    # ### end Alembic commands ###
