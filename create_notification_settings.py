from app import app, db
from models.user import User
from models.notification import NotificationSetting

def create_notification_settings():
    with app.app_context():
        # Get all users
        users = User.query.all()
        count = 0
        
        for user in users:
            # Check if user already has notification settings
            existing_settings = NotificationSetting.query.filter_by(user_id=user.id).first()
            
            if not existing_settings:
                # Create notification settings for the user
                notification_settings = NotificationSetting(
                    user_id=user.id,
                    enabled=True,
                    notification_radius=200,  # Default 200 meters (smaller for testing)
                    notify_specific_routes=False,
                    routes=[],
                    notification_cooldown=30  # Default 30 seconds (shorter for testing)
                )
                db.session.add(notification_settings)
                count += 1
            else:
                # Update existing settings for testing
                existing_settings.notification_radius = 200  # 200 meters
                existing_settings.notification_cooldown = 30  # 30 seconds
                existing_settings.enabled = True
                count += 1
        
        if count > 0:
            db.session.commit()
            print(f"Created or updated notification settings for {count} users.")
        else:
            print("All users already have notification settings.")

if __name__ == "__main__":
    create_notification_settings() 