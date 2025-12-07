# Login System - Python GUI Application

A modern login system built with Python's tkinter library and SQLite database. Features user registration, authentication, password hashing, and login history tracking.

## Features

✓ **User Registration** - Create new accounts with email validation and strong password requirements
✓ **User Login** - Secure authentication with SHA-256 password hashing
✓ **Dashboard** - User profile and account information display
✓ **Login History** - Track all login attempts (successful and failed)
✓ **Password Validation** - Enforces strong password policies
✓ **Email Validation** - Validates email format during registration
✓ **SQLite Database** - Persistent user data storage
✓ **GUI Interface** - Clean and intuitive tkinter-based interface

## Requirements

- Python 3.7 or higher
- tkinter (built-in with Python)
- sqlite3 (built-in with Python)

No external packages needed! All dependencies are built into Python.

## Installation

1. Clone or download the project:
```bash
cd e:\Backup\Tech_up
```

2. (Optional) Create a virtual environment:
```bash
python -m venv venv
venv\Scripts\activate
```

3. No additional packages required!

## Usage

### Start the Login Application

```bash
python login_app.py
```

### Run Test Script (Optional)

Populate the database with test users:

```bash
python test_login.py
```

Then select option `1` to create test users.

**Test Account Credentials:**
```
Username: demo
Password: Demo123

Username: testuser
Password: Test123

Username: admin
Password: Admin123
```

## File Structure

```
e:\Backup\Tech_up\
├── login_app.py          # Main login application
├── test_login.py         # Test/setup script
├── requirements.txt      # Project dependencies
├── README.md            # This file
└── users.db            # SQLite database (auto-created)
```

## How It Works

### 1. Registration
- User enters username, email, and password
- Password strength is validated:
  - Minimum 6 characters
  - Must contain uppercase letter
  - Must contain digit
- Email format is validated
- Password is hashed using SHA-256
- Data stored in SQLite database

### 2. Login
- User enters credentials
- Password is hashed and compared with stored hash
- Successful login updates `last_login` timestamp
- Login attempt is recorded in history (success/failed)
- User directed to dashboard

### 3. Dashboard
- Displays user information (username, email, creation date, last login)
- Shows login history with timestamps and status
- Logout button returns to login screen

### 4. Login History
- Tracks all login attempts
- Records timestamp and success/failure status
- Accessible from dashboard
- Limited to last 20 attempts displayed

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
)
```

### Login History Table
```sql
CREATE TABLE login_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT,
    FOREIGN KEY (username) REFERENCES users(username)
)
```

## Password Requirements

Passwords must meet these criteria:
- ✓ At least 6 characters long
- ✓ Contains at least one uppercase letter (A-Z)
- ✓ Contains at least one digit (0-9)

**Example valid passwords:**
- `Password123`
- `MyPass456`
- `Secure2024`

## Security Features

1. **Password Hashing** - SHA-256 hashing algorithm
2. **Email Validation** - Regex-based email format validation
3. **Username Uniqueness** - Prevents duplicate usernames
4. **Login Tracking** - Records all login attempts
5. **Input Validation** - Validates all user inputs

## Screenshots Explanation

### Login Screen
- Username and password input fields
- Login and Register buttons
- Responsive error messages

### Registration Screen
- Username, email, password fields
- Password confirmation field
- Real-time validation feedback

### Dashboard
- User information display
- Login history viewer
- Logout functionality

## Troubleshooting

### "No module named 'tkinter'"
- **Solution**: tkinter comes built-in with Python. If missing, reinstall Python with tkinter selected.

### "users.db not found"
- **Solution**: Normal behavior. Database is created automatically on first run.

### "Username already exists"
- **Solution**: Choose a different username or use the test script to reset the database.

### Password validation errors
- **Solution**: Ensure password has 6+ chars, 1 uppercase, and 1 digit.

## Customization Ideas

1. **Change Theme** - Modify colors in `show_login_frame()` and `show_dashboard()`
2. **Add Encryption** - Use `cryptography` library for better security
3. **Email Verification** - Add email confirmation on registration
4. **Password Recovery** - Implement forgot password feature
5. **2FA** - Add two-factor authentication
6. **User Roles** - Add admin and user role management

## Advanced Features to Add

```python
# Example: Add user profile picture
# Add remember me functionality
# Add email notifications
# Add password change feature
# Add account deletion
# Add user search (admin)
# Add session management
```

## License

Free to use and modify for educational and personal projects.

## Author Notes

- All data is stored locally in SQLite
- No internet connection required
- Great starter project for learning Python GUI and database concepts
- Easily extensible for larger applications

## Support

For issues or questions, review the code comments or test with the test script.

---

**Happy Coding!** 🎯
