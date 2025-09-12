from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy(session_options={
    'expire_on_commit': False,
    'autoflush': False
})

# Import models to ensure they're registered with SQLAlchemy
from .user import User
from .vehicle import Vehicle
from .location_log import LocationLog
from .notification import Notification, NotificationSetting 