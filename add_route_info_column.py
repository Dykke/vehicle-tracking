import os
import sys
from flask import Flask
from models import db
from sqlalchemy import text, exc
from dotenv import load_dotenv
import time

load_dotenv()

print("Starting route_info column migration...")
print(f"Current working directory: {os.getcwd()}")

# Create a minimal Flask app for migrations
app = Flask(__name__)

# Get the database URL from environment
db_url = os.environ.get('DATABASE_URL')
if not db_url:
    print("ERROR: DATABASE_URL environment variable not set!")
    sys.exit(1)

print(f"Database URL: {db_url[:10]}***")  # Print first 10 chars for security

# Handle Render's postgres:// URLs (convert to postgresql://)
if db_url.startswith('postgres://'):
    db_url = db_url.replace('postgres://', 'postgresql://', 1)
    print("Converted postgres:// to postgresql://")

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db.init_app(app)

def add_route_info_column():
    """Add route_info column to the vehicles table."""
    print("Starting migration...")
    
    with app.app_context():
        try:
            # Try a basic query to test connection
            try:
                db.session.execute(text("SELECT 1"))
                db.session.commit()
                print("Database connection successful")
            except Exception as e:
                print(f"ERROR: Could not connect to database: {str(e)}")
                return
            
            # Check if the column already exists
            try:
                exists_query = text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='vehicles' AND column_name='route_info'
                """)
                result = db.session.execute(exists_query).fetchone()
                
                if not result:
                    print("Adding route_info column to vehicles table...")
                    
                    # Add the route_info column as JSONB
                    try:
                        db.session.execute(text("""
                            ALTER TABLE vehicles 
                            ADD COLUMN route_info JSONB DEFAULT NULL
                        """))
                        db.session.commit()
                        print("route_info column added successfully!")
                    except exc.SQLAlchemyError as e:
                        print(f"Error adding column: {str(e)}")
                        db.session.rollback()
                        # Try a different approach if the first one fails
                        try:
                            print("Trying alternative approach to add column...")
                            db.session.execute(text("""
                                ALTER TABLE vehicles 
                                ADD COLUMN IF NOT EXISTS route_info JSON
                            """))
                            db.session.commit()
                            print("route_info column added using alternative approach!")
                        except exc.SQLAlchemyError as alt_err:
                            print(f"Error with alternative approach: {str(alt_err)}")
                            db.session.rollback()
                            raise
                else:
                    print("route_info column already exists.")
                
                # Wait a bit to ensure the column is fully added
                time.sleep(2)
                
                print("Checking for existing routes to populate route_info...")
                # Get all vehicles with routes but no route_info
                vehicles = db.session.execute(text("""
                    SELECT id, route 
                    FROM vehicles 
                    WHERE route IS NOT NULL
                """)).fetchall()
                
                # For each vehicle with a route, parse it and update route_info
                updated_count = 0
                for vehicle in vehicles:
                    route = vehicle.route
                    vehicle_id = vehicle.id
                    
                    # Skip if no route information
                    if not route:
                        continue
                    
                    # Check if route follows our "A to B" format
                    route_parts = route.split(" to ")
                    if len(route_parts) == 2:
                        route_info = {
                            "route_name": route,
                            "origin": route_parts[0],
                            "destination": route_parts[1]
                        }
                        
                        # We need to check if route_info column exists again for safety
                        try:
                            # Update the route_info column
                            db.session.execute(text("""
                                UPDATE vehicles 
                                SET route_info = :route_info::jsonb 
                                WHERE id = :id
                            """), {"route_info": str(route_info).replace("'", '"'), "id": vehicle_id})
                            updated_count += 1
                            print(f"Updated route_info for vehicle {vehicle_id} with route: {route}")
                        except exc.SQLAlchemyError as e:
                            print(f"Error updating vehicle {vehicle_id}: {str(e)}")
                            # Continue with other vehicles even if this one fails
                
                db.session.commit()
                print(f"Migration completed successfully! Updated {updated_count} vehicles.")
            except exc.SQLAlchemyError as e:
                print(f"Error during migration: {str(e)}")
                db.session.rollback()
                raise
                
        except Exception as e:
            print(f"ERROR: Unhandled exception: {str(e)}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    try:
        add_route_info_column()
        print("Migration script completed successfully!")
    except Exception as e:
        print(f"ERROR: Migration failed: {str(e)}")
        sys.exit(1) 