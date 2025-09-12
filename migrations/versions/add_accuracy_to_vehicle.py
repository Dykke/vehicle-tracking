"""Add accuracy field to Vehicle model

Revision ID: add_accuracy_to_vehicle
Revises: add_route_column
Create Date: 2025-05-21 18:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_accuracy_to_vehicle'
down_revision = 'add_route_column'
branch_labels = None
depends_on = None


def upgrade():
    # Add accuracy column to vehicles table if it doesn't exist already
    op.add_column('vehicles', sa.Column('accuracy', sa.Float(), nullable=True), schema=None)


def downgrade():
    # Remove accuracy column from vehicles table
    op.drop_column('vehicles', 'accuracy', schema=None) 