"""Add accuracy field to User, Vehicle, and LocationLog models

Revision ID: add_accuracy_field
Revises: 
Create Date: 2024-03-10 06:55:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_accuracy_field'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add accuracy column to users table
    op.add_column('users', sa.Column('accuracy', sa.Float(), nullable=True))
    
    # Add accuracy column to vehicles table
    op.add_column('vehicles', sa.Column('accuracy', sa.Float(), nullable=True))
    
    # Add accuracy column to location_logs table
    op.add_column('location_logs', sa.Column('accuracy', sa.Float(), nullable=True))


def downgrade():
    # Remove accuracy column from users table
    op.drop_column('users', 'accuracy')
    
    # Remove accuracy column from vehicles table
    op.drop_column('vehicles', 'accuracy')
    
    # Remove accuracy column from location_logs table
    op.drop_column('location_logs', 'accuracy') 