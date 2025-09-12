"""Add route column to Vehicle model

Revision ID: add_route_column
Revises: add_accuracy_field
Create Date: 2025-05-21 08:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_route_column'
down_revision = 'add_accuracy_field'
branch_labels = None
depends_on = None


def upgrade():
    # Add route column to vehicles table
    op.add_column('vehicles', sa.Column('route', sa.String(255), nullable=True))
    
    # Also add route_info column to vehicles table (for storing JSON data)
    op.add_column('vehicles', sa.Column('route_info', sa.JSON(), nullable=True))


def downgrade():
    # Remove route_info column from vehicles table
    op.drop_column('vehicles', 'route_info')
    
    # Remove route column from vehicles table
    op.drop_column('vehicles', 'route') 