"""empty message

Revision ID: ee7b1c4bc291
Revises: 3e02f72bec30
Create Date: 2018-05-28 17:24:52.328494

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ee7b1c4bc291'
down_revision = '3e02f72bec30'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('planing_period_templates')
    op.add_column('inventory_items', sa.Column('cp_day_in_month', sa.SmallInteger(), nullable=True))
    op.add_column('inventory_items', sa.Column('cp_end_date', sa.DateTime(timezone=True), nullable=True))
    op.add_column('inventory_items', sa.Column('cp_period', sa.SmallInteger(), nullable=True))
    op.add_column('inventory_items', sa.Column('cp_plan_date', sa.DateTime(timezone=True), nullable=True))
    op.add_column('inventory_items', sa.Column('cp_quantity', sa.Float(), nullable=True))
    op.add_column('inventory_items', sa.Column('cp_type', sa.SmallInteger(), nullable=False))
    op.add_column('inventory_items', sa.Column('cp_weekday', sa.SmallInteger(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('inventory_items', 'cp_weekday')
    op.drop_column('inventory_items', 'cp_type')
    op.drop_column('inventory_items', 'cp_quantity')
    op.drop_column('inventory_items', 'cp_plan_date')
    op.drop_column('inventory_items', 'cp_period')
    op.drop_column('inventory_items', 'cp_end_date')
    op.drop_column('inventory_items', 'cp_day_in_month')
    op.create_table('planing_period_templates',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('start_date', sa.DATE(), autoincrement=False, nullable=True),
    sa.Column('end_date', sa.DATE(), autoincrement=False, nullable=True),
    sa.Column('week_no', sa.SMALLINT(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='planing_period_templates_pkey')
    )
    # ### end Alembic commands ###