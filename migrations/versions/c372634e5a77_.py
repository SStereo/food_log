"""empty message

Revision ID: c372634e5a77
Revises: cbc7ddbf5d85
Create Date: 2018-06-26 15:51:50.061197

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'c372634e5a77'
down_revision = 'cbc7ddbf5d85'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('shopping_orders', sa.Column('plan_forecast_days', sa.SmallInteger(), nullable=False))
    op.alter_column('shopping_orders', 'status',
               existing_type=sa.SMALLINT(),
               nullable=False)
    op.drop_column('shopping_orders', 'plan_date_start')
    op.drop_column('shopping_orders', 'plan_date_end')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('shopping_orders', sa.Column('plan_date_end', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True))
    op.add_column('shopping_orders', sa.Column('plan_date_start', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True))
    op.alter_column('shopping_orders', 'status',
               existing_type=sa.SMALLINT(),
               nullable=True)
    op.drop_column('shopping_orders', 'plan_forecast_days')
    # ### end Alembic commands ###
