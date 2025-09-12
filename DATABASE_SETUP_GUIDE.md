# Database Setup Guide for Drive Monitoring System

## 🏠 Local Development (MySQL)

### 1. Update your `.env` file:
```bash
# Local MySQL Database
DATABASE_URL=mysql://root:root@localhost/transport_monitoring

# Flask Configuration
SECRET_KEY=your-secret-key-change-this
DEBUG=True
HOST=0.0.0.0
PORT=5000
```

### 2. Ensure your local MySQL server is running
- MySQL service should be active
- Port 3306 should be accessible
- User `root` with password `root` should exist
- Database `transport_monitoring` should exist

### 3. Test local connection:
```bash
mysql -u root -p -h localhost
# Enter password: root
# Then: USE transport_monitoring;
```

## 🚀 Production (Render - PostgreSQL)

### 1. Render will automatically set:
```bash
DATABASE_URL=postgresql://username:password@host:port/database
```

### 2. The app automatically handles:
- PostgreSQL connection pooling
- Connection retry logic
- Proper dialect configuration

## 🔧 Configuration Files

### `db_config.py` - Automatically handles:
- ✅ Local MySQL with `transport_monitoring` database
- ✅ Production PostgreSQL from Render
- ✅ Connection pooling and optimization
- ✅ Database type detection

### `app.py` - Automatically:
- ✅ Loads the correct database configuration
- ✅ Creates tables if they don't exist
- ✅ Handles both MySQL and PostgreSQL

## 🧪 Testing Your Setup

### 1. Start your Flask app:
```bash
py app.py
```

### 2. Check the logs for:
```
INFO - MySQL database detected: mysql://root:root@localhost/transport_monitoring
INFO - Updated local MySQL URL to include database: mysql://root:root@localhost/transport_monitoring
```

### 3. Add a driver and verify:
- Data should be saved to your local MySQL database
- Check the `vehicles` table in `transport_monitoring` schema
- Data should persist after server restart

## 🚨 Troubleshooting

### If data still isn't saving:
1. **Check MySQL connection**:
   ```bash
   mysql -u root -p -h localhost transport_monitoring
   ```

2. **Verify tables exist**:
   ```sql
   SHOW TABLES;
   DESCRIBE vehicles;
   ```

3. **Check Flask logs** for database connection errors

4. **Verify database permissions**:
   ```sql
   SHOW GRANTS FOR 'root'@'localhost';
   ```

### If you get connection errors:
1. **Start MySQL service**:
   ```bash
   # Windows
   net start mysql80
   
   # Or restart the service
   ```

2. **Check MySQL is listening**:
   ```bash
   netstat -an | findstr 3306
   ```

## 📝 Summary

- **Local**: Uses MySQL with `transport_monitoring` database
- **Production**: Uses PostgreSQL from Render automatically
- **No code changes needed** - just update your `.env` file
- **Data will persist** in both environments
