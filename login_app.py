"""
Modern Login System with GUI using tkinter and SQLite
Features: User registration, login, password hashing, dashboard
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import hashlib
import re
from datetime import datetime
import os

class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Login System")
        self.root.geometry("500x600")
        self.root.resizable(False, False)
        self.root.configure(bg='#f0f0f0')
        
        # Center window on screen
        self.center_window()
        
        # Initialize database
        self.init_database()
        
        # Current user
        self.current_user = None
        
        # Show login frame
        self.show_login_frame()
    
    def center_window(self):
        """Center window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def init_database(self):
        """Initialize SQLite database"""
        self.conn = sqlite3.connect('users.db')
        self.cursor = self.conn.cursor()
        
        # Create users table if not exists
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')
        
        # Create login history table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS login_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT,
                FOREIGN KEY (username) REFERENCES users(username)
            )
        ''')
        
        self.conn.commit()
    
    def clear_widgets(self):
        """Clear all widgets from root"""
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def validate_email(self, email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def validate_password(self, password):
        """Validate password strength"""
        if len(password) < 6:
            return False, "Password must be at least 6 characters long"
        if not any(char.isupper() for char in password):
            return False, "Password must contain at least one uppercase letter"
        if not any(char.isdigit() for char in password):
            return False, "Password must contain at least one digit"
        return True, "Password is strong"
    
    def show_login_frame(self):
        """Display login frame"""
        self.clear_widgets()
        
        # Title
        title_label = tk.Label(
            self.root, text="Login System", font=("Arial", 24, "bold"),
            bg='#f0f0f0', fg='#333'
        )
        title_label.pack(pady=30)
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Username
        ttk.Label(main_frame, text="Username:", font=("Arial", 10)).pack(anchor=tk.W, pady=(0, 5))
        self.login_username = ttk.Entry(main_frame, font=("Arial", 10), width=40)
        self.login_username.pack(fill=tk.X, pady=(0, 15))
        self.login_username.focus()
        
        # Password
        ttk.Label(main_frame, text="Password:", font=("Arial", 10)).pack(anchor=tk.W, pady=(0, 5))
        self.login_password = ttk.Entry(main_frame, font=("Arial", 10), width=40, show="•")
        self.login_password.pack(fill=tk.X, pady=(0, 20))
        
        # Bind Enter key to login
        self.login_password.bind('<Return>', lambda e: self.perform_login())
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        # Login button
        login_btn = ttk.Button(
            button_frame, text="Login", command=self.perform_login,
            width=15
        )
        login_btn.pack(side=tk.LEFT, padx=5)
        
        # Register button
        register_btn = ttk.Button(
            button_frame, text="Register", command=self.show_register_frame,
            width=15
        )
        register_btn.pack(side=tk.LEFT, padx=5)
        
        # Status label
        self.status_label = tk.Label(main_frame, text="", font=("Arial", 9), fg="red", bg='#f0f0f0')
        self.status_label.pack(pady=20)
    
    def perform_login(self):
        """Perform login action"""
        username = self.login_username.get().strip()
        password = self.login_password.get()
        
        if not username or not password:
            self.status_label.config(text="Please enter both username and password", fg="red")
            return
        
        try:
            self.cursor.execute('SELECT password FROM users WHERE username = ?', (username,))
            result = self.cursor.fetchone()
            
            if result and result[0] == self.hash_password(password):
                # Login successful
                self.current_user = username
                self.cursor.execute(
                    'UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE username = ?',
                    (username,)
                )
                self.cursor.execute(
                    'INSERT INTO login_history (username, status) VALUES (?, ?)',
                    (username, 'SUCCESS')
                )
                self.conn.commit()
                self.show_dashboard()
            else:
                self.cursor.execute(
                    'INSERT INTO login_history (username, status) VALUES (?, ?)',
                    (username, 'FAILED')
                )
                self.conn.commit()
                self.status_label.config(text="Invalid username or password", fg="red")
                self.login_password.delete(0, tk.END)
        except Exception as e:
            self.status_label.config(text=f"Login error: {str(e)}", fg="red")
    
    def show_register_frame(self):
        """Display register frame"""
        self.clear_widgets()
        
        # Title
        title_label = tk.Label(
            self.root, text="Create Account", font=("Arial", 24, "bold"),
            bg='#f0f0f0', fg='#333'
        )
        title_label.pack(pady=30)
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Username
        ttk.Label(main_frame, text="Username:", font=("Arial", 10)).pack(anchor=tk.W, pady=(0, 5))
        self.reg_username = ttk.Entry(main_frame, font=("Arial", 10), width=40)
        self.reg_username.pack(fill=tk.X, pady=(0, 10))
        self.reg_username.focus()
        
        # Email
        ttk.Label(main_frame, text="Email:", font=("Arial", 10)).pack(anchor=tk.W, pady=(0, 5))
        self.reg_email = ttk.Entry(main_frame, font=("Arial", 10), width=40)
        self.reg_email.pack(fill=tk.X, pady=(0, 10))
        
        # Password
        ttk.Label(main_frame, text="Password:", font=("Arial", 10)).pack(anchor=tk.W, pady=(0, 5))
        self.reg_password = ttk.Entry(main_frame, font=("Arial", 10), width=40, show="•")
        self.reg_password.pack(fill=tk.X, pady=(0, 10))
        
        # Confirm Password
        ttk.Label(main_frame, text="Confirm Password:", font=("Arial", 10)).pack(anchor=tk.W, pady=(0, 5))
        self.reg_confirm = ttk.Entry(main_frame, font=("Arial", 10), width=40, show="•")
        self.reg_confirm.pack(fill=tk.X, pady=(0, 20))
        self.reg_confirm.bind('<Return>', lambda e: self.perform_register())
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        # Register button
        register_btn = ttk.Button(
            button_frame, text="Register", command=self.perform_register,
            width=15
        )
        register_btn.pack(side=tk.LEFT, padx=5)
        
        # Back button
        back_btn = ttk.Button(
            button_frame, text="Back to Login", command=self.show_login_frame,
            width=15
        )
        back_btn.pack(side=tk.LEFT, padx=5)
        
        # Status label
        self.status_label = tk.Label(main_frame, text="", font=("Arial", 9), fg="red", bg='#f0f0f0')
        self.status_label.pack(pady=20)
    
    def perform_register(self):
        """Perform registration"""
        username = self.reg_username.get().strip()
        email = self.reg_email.get().strip()
        password = self.reg_password.get()
        confirm = self.reg_confirm.get()
        
        # Validation
        if not username or not email or not password or not confirm:
            self.status_label.config(text="All fields are required", fg="red")
            return
        
        if len(username) < 3:
            self.status_label.config(text="Username must be at least 3 characters", fg="red")
            return
        
        if not self.validate_email(email):
            self.status_label.config(text="Invalid email format", fg="red")
            return
        
        is_strong, msg = self.validate_password(password)
        if not is_strong:
            self.status_label.config(text=msg, fg="red")
            return
        
        if password != confirm:
            self.status_label.config(text="Passwords do not match", fg="red")
            return
        
        try:
            hashed_password = self.hash_password(password)
            self.cursor.execute(
                'INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                (username, email, hashed_password)
            )
            self.conn.commit()
            self.status_label.config(text="Registration successful! Please login.", fg="green")
            self.root.after(1500, self.show_login_frame)
        except sqlite3.IntegrityError:
            self.status_label.config(text="Username or email already exists", fg="red")
        except Exception as e:
            self.status_label.config(text=f"Registration error: {str(e)}", fg="red")
    
    def show_dashboard(self):
        """Display dashboard after successful login"""
        self.clear_widgets()
        
        # Header
        header_frame = tk.Frame(self.root, bg='#333', height=60)
        header_frame.pack(fill=tk.X)
        
        header_label = tk.Label(
            header_frame, text=f"Welcome, {self.current_user}!",
            font=("Arial", 16, "bold"), bg='#333', fg='white'
        )
        header_label.pack(pady=10)
        
        # Main content
        main_frame = ttk.Frame(self.root, padding="30")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # User info
        user_info_label = tk.Label(
            main_frame, text="User Information",
            font=("Arial", 14, "bold"), bg='#f0f0f0'
        )
        user_info_label.pack(anchor=tk.W, pady=(0, 15))
        
        # Fetch user data
        self.cursor.execute(
            'SELECT username, email, created_at, last_login FROM users WHERE username = ?',
            (self.current_user,)
        )
        user_data = self.cursor.fetchone()
        
        if user_data:
            info_text = f"""
Username: {user_data[0]}
Email: {user_data[1]}
Account Created: {user_data[2]}
Last Login: {user_data[3] or 'Never'}
            """
            info_label = tk.Label(
                main_frame, text=info_text, font=("Arial", 10),
                bg='#f0f0f0', justify=tk.LEFT
            )
            info_label.pack(anchor=tk.W, pady=10)
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=30)
        
        # View history button
        history_btn = ttk.Button(
            button_frame, text="View Login History",
            command=self.show_login_history, width=20
        )
        history_btn.pack(side=tk.LEFT, padx=5)
        
        # Logout button
        logout_btn = ttk.Button(
            button_frame, text="Logout",
            command=self.logout, width=20
        )
        logout_btn.pack(side=tk.LEFT, padx=5)
    
    def show_login_history(self):
        """Show login history in a new window"""
        history_window = tk.Toplevel(self.root)
        history_window.title(f"Login History - {self.current_user}")
        history_window.geometry("600x400")
        
        # Title
        title_label = tk.Label(
            history_window, text="Your Login History",
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=10)
        
        # Treeview
        columns = ('Login Time', 'Status')
        tree = ttk.Treeview(history_window, columns=columns, height=15)
        tree.column('#0', width=0, stretch=tk.NO)
        tree.column('Login Time', anchor=tk.W, width=400)
        tree.column('Status', anchor=tk.CENTER, width=100)
        
        tree.heading('#0', text='', anchor=tk.W)
        tree.heading('Login Time', text='Login Time', anchor=tk.W)
        tree.heading('Status', text='Status', anchor=tk.CENTER)
        
        # Fetch history
        self.cursor.execute(
            'SELECT login_time, status FROM login_history WHERE username = ? ORDER BY login_time DESC LIMIT 20',
            (self.current_user,)
        )
        
        for idx, (login_time, status) in enumerate(self.cursor.fetchall()):
            status_color = 'green' if status == 'SUCCESS' else 'red'
            tree.insert(parent='', index='end', iid=idx, text='',
                       values=(login_time, status),
                       tags=(status,))
        
        tree.tag_configure('SUCCESS', foreground='green')
        tree.tag_configure('FAILED', foreground='red')
        
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def logout(self):
        """Logout user"""
        self.current_user = None
        self.show_login_frame()


def main():
    root = tk.Tk()
    app = LoginApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
