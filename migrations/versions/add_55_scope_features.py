"""Add 55% scope features migration

Revision ID: add_55_scope_features
Revises: add_route_column
Create Date: 2023-06-20 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text


# revision identifiers, used by Alembic.
revision = 'add_55_scope_features'
down_revision = 'add_route_column'
branch_labels = None
depends_on = None


def upgrade():
    # Add new fields to users table
    op.add_column('users', sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('users', sa.Column('profile_image_url', sa.String(500), nullable=True))
    
    # Add new fields to vehicles table
    op.add_column('vehicles', sa.Column('occupancy_status', sa.String(20), nullable=True, server_default='vacant'))
    op.add_column('vehicles', sa.Column('last_speed_kmh', sa.Float(), nullable=True))
    
    # Create driver_action_logs table
    op.create_table('driver_action_logs',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('driver_id', sa.Integer(), nullable=False),
        sa.Column('vehicle_id', sa.Integer(), nullable=True),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['driver_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['vehicle_id'], ['vehicles.id'], ),
    )
    
    # Create trips table
    op.create_table('trips',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('vehicle_id', sa.Integer(), nullable=False),
        sa.Column('driver_id', sa.Integer(), nullable=False),
        sa.Column('route_name', sa.String(255), nullable=True),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('end_time', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='active'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['vehicle_id'], ['vehicles.id'], ),
        sa.ForeignKeyConstraint(['driver_id'], ['users.id'], ),
    )
    
    # Create passenger_events table
    op.create_table('passenger_events',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('trip_id', sa.Integer(), nullable=False),
        sa.Column('event_type', sa.String(20), nullable=False),
        sa.Column('count', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['trip_id'], ['trips.id'], ),
    )
    
    # Create indexes for better performance
    op.create_index('idx_driver_action_logs_driver_id', 'driver_action_logs', ['driver_id'])
    op.create_index('idx_driver_action_logs_vehicle_id', 'driver_action_logs', ['vehicle_id'])
    op.create_index('idx_driver_action_logs_created_at', 'driver_action_logs', ['created_at'])
    
    op.create_index('idx_trips_vehicle_id', 'trips', ['vehicle_id'])
    op.create_index('idx_trips_driver_id', 'trips', ['driver_id'])
    op.create_index('idx_trips_status', 'trips', ['status'])
    op.create_index('idx_trips_created_at', 'trips', ['created_at'])
    
    op.create_index('idx_passenger_events_trip_id', 'passenger_events', ['trip_id'])
    op.create_index('idx_passenger_events_created_at', 'passenger_events', ['created_at'])
    
    # Add constraints
    op.create_check_constraint(
        'chk_action_type', 'driver_action_logs',
        "action IN ('occupancy_change', 'trip_start', 'trip_end', 'passenger_event', 'password_change', 'driver_activated', 'driver_deactivated')"
    )
    
    op.create_check_constraint(
        'chk_event_type', 'passenger_events',
        "event_type IN ('board', 'alight')"
    )
    
    op.create_check_constraint(
        'chk_trip_status', 'trips',
        "status IN ('active', 'completed', 'cancelled')"
    )
    
    # Update existing data to set default values
    op.execute("UPDATE users SET is_active = TRUE WHERE is_active IS NULL")
    op.execute("UPDATE vehicles SET occupancy_status = 'vacant' WHERE occupancy_status IS NULL")


def downgrade():
    # Drop constraints
    op.drop_constraint('chk_trip_status', 'trips', type_='check')
    op.drop_constraint('chk_event_type', 'passenger_events', type_='check')
    op.drop_constraint('chk_action_type', 'driver_action_logs', type_='check')
    
    # Drop indexes
    op.drop_index('idx_passenger_events_created_at', table_name='passenger_events')
    op.drop_index('idx_passenger_events_trip_id', table_name='passenger_events')
    
    op.drop_index('idx_trips_created_at', table_name='trips')
    op.drop_index('idx_trips_status', table_name='trips')
    op.drop_index('idx_trips_driver_id', table_name='trips')
    op.drop_index('idx_trips_vehicle_id', table_name='trips')
    
    op.drop_index('idx_driver_action_logs_created_at', table_name='driver_action_logs')
    op.drop_index('idx_driver_action_logs_vehicle_id', table_name='driver_action_logs')
    op.drop_index('idx_driver_action_logs_driver_id', table_name='driver_action_logs')
    
    # Drop tables
    op.drop_table('passenger_events')
    op.drop_table('trips')
    op.drop_table('driver_action_logs')
    
    # Drop columns from vehicles table
    op.drop_column('vehicles', 'last_speed_kmh')
    op.drop_column('vehicles', 'occupancy_status')
    
    # Drop columns from users table
    op.drop_column('users', 'profile_image_url')
    op.drop_column('users', 'is_active')
