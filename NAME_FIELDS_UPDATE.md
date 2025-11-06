# Driver Name Fields Update

## Summary of Changes

This update adds support for **first name**, **middle name**, and **last name** fields to the driver information in the Drive Monitoring System.

## Changes Made

### 1. Database Model (`models/user.py`)
- Added three new columns to the `User` model:
  - `first_name` (VARCHAR 100, nullable)
  - `middle_name` (VARCHAR 100, nullable)
  - `last_name` (VARCHAR 100, nullable)
- Added `get_full_name()` method that returns the full name (combines first, middle, last names)
- Updated `to_dict()` method to include the new fields and full name

### 2. Backend Routes

#### `routes/operator.py`
- Updated `add_driver()` endpoint to accept name fields
- Updated driver response objects to include name information
- Modified GET endpoints to return full name information

#### `routes/auth.py`
- Updated `register()` endpoint to capture name fields from registration form
- Names are stored when new commuter/driver accounts are created

### 3. Frontend Templates

#### `templates/auth/register.html`
- Added three input fields for first name, middle name, and last name
- Fields are optional but appear before username field

#### `templates/operator/manage_drivers.html`
- Added name input fields to the "Add Driver" modal
- Updated JavaScript to send name data to backend
- Modified driver table to show full name in first column
- Added "Name" column to driver list table

### 4. Database Migration
- Created `add_name_fields_to_users.py` migration script
- Supports SQLite, PostgreSQL, and MySQL databases
- Safely adds columns if they don't already exist

## How to Apply the Changes

### Step 1: Run the Migration Script

**Important:** Before running the server, you must run the database migration to add the new columns.

```bash
# Make sure you're in the project directory
cd drive-monitoring

# Activate your virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Run the migration script
python add_name_fields_to_users.py
```

The migration script will:
1. Connect to your database (SQLite or PostgreSQL based on environment)
2. Check if the name columns already exist
3. Add the columns if they don't exist
4. Confirm successful migration

### Step 2: Start the Server

After running the migration, start your server normally:

```bash
python run_migration_and_server.py
```

Or:

```bash
python app.py
```

## Features

### For Operators
When creating a new driver, operators can now:
- Enter the driver's first name
- Enter the driver's middle name (optional)
- Enter the driver's last name
- The full name will be displayed in the driver list

### For Commuters (Registration)
When registering a new account, users can:
- Enter their first name
- Enter their middle name (optional)
- Enter their last name
- Names are optional but recommended

### Display
- **Driver List**: Shows full name instead of just username
- **API Responses**: Include `full_name` field in driver data
- **get_full_name() method**: Returns formatted full name, falls back to username if no name provided

## Data Structure

The `get_full_name()` method works as follows:
```python
# If all name parts are provided:
"John Michael Doe"

# If only first and last name:
"John Doe"

# If no name parts provided:
"username" (falls back to username)
```

## Backwards Compatibility

✅ **Fully backwards compatible**
- Existing drivers without names will continue to work
- The `get_full_name()` method returns username if no name is set
- Name fields are optional in all forms
- No existing functionality is broken

## Testing Checklist

After applying the migration:

- [ ] Run migration script successfully
- [ ] Start the server without errors
- [ ] Register a new commuter account with name fields
- [ ] Login as operator
- [ ] Create a new driver with name fields
- [ ] Verify driver list shows full names
- [ ] Verify existing drivers still appear (with username as fallback)
- [ ] Check API responses include name fields

## Troubleshooting

### Migration Fails
If the migration script fails:
1. Check your database connection
2. Verify DATABASE_URL environment variable is set correctly
3. Ensure you have write permissions to the database
4. Check the error message for specific issues

### Server Won't Start
If server fails after migration:
1. Verify migration completed successfully
2. Check `app.log` for error messages
3. Try restarting with debug mode: `DEBUG=True python app.py`

### Names Not Showing
If names aren't appearing:
1. Clear browser cache
2. Hard refresh (Ctrl+F5 or Cmd+Shift+R)
3. Check browser console for JavaScript errors
4. Verify the migration added the columns correctly

## Rollback (If Needed)

If you need to remove the name fields:

```sql
-- For SQLite:
-- (SQLite doesn't support DROP COLUMN, would need to recreate table)

-- For PostgreSQL:
ALTER TABLE users DROP COLUMN first_name;
ALTER TABLE users DROP COLUMN middle_name;
ALTER TABLE users DROP COLUMN last_name;

-- For MySQL:
ALTER TABLE users DROP COLUMN first_name;
ALTER TABLE users DROP COLUMN middle_name;
ALTER TABLE users DROP COLUMN last_name;
```

## Support

If you encounter any issues:
1. Check the logs in `logs/app.log`
2. Review this documentation
3. Verify all files were updated correctly
4. Check that the migration ran successfully

---

**Version**: 1.0  
**Date**: October 8, 2025  
**Author**: Drive Monitoring System Development Team

