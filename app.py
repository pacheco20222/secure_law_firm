from flask import Flask, render_template, request, redirect, url_for, session, flash
import secrets  # Import the secrets module
from dotenv import load_dotenv
import os
from flask_wtf import CSRFProtect
import pyotp  # For 2FA verification
from hashlib import sha256  # For password hashing
from forms import LoginForm, CreateUserForm  # Import the form class
from config import mysql_connection, ssh_tunnel  # Import tunnel functions from config.py
from models.worker_model import WorkerModel  # Import the create_worker function from worker_model.py
from functools import wraps  # Import wraps to fix route decorator issues

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

csrf = CSRFProtect(app)

# Function to verify the password (hashed)
def verify_password(stored_password, provided_password):
    return stored_password == sha256(provided_password.encode('utf-8')).hexdigest()

# Ensure authentication with correct function name preservation
def login_required(route_func):
    @wraps(route_func)
    def wrapper(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return route_func(*args, **kwargs)
    return wrapper

@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('dashboard'))  # If user is logged in, go to dashboard
    else:
        return redirect(url_for('login'))  # Otherwise, go to login page

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', current_user=session['user'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        two_factor_code = form.two_factor_code.data

        # Start the SSH tunnel
        tunnel = ssh_tunnel()
        tunnel.start()

        # Connect to MySQL
        connection = mysql_connection(tunnel)
        cursor = connection.cursor()

        # Query user details
        query = "SELECT email, hashed_password, 2fa_secret, 2fa_enabled, name, role FROM workers WHERE email = %s"
        cursor.execute(query, (email,))
        user = cursor.fetchone()

        if user:
            db_email, db_password, db_2fa_secret, db_2fa_enabled, db_name, db_role = user

            # Verify password and enforce 2FA
            if verify_password(db_password, password):
                if db_2fa_enabled:
                    totp = pyotp.TOTP(db_2fa_secret)
                    if totp.verify(two_factor_code):
                        session['user'] = {
                            'name': db_name,
                            'email': db_email,
                            'role': db_role  # Ensure 'role' is included
                        }
                        tunnel.stop()
                        return redirect(url_for('dashboard'))
                    else:
                        flash('Invalid 2FA code', 'danger')
                else:
                    flash('2FA is required for login.', 'danger')
            else:
                flash('Invalid password', 'danger')
        else:
            flash('Invalid email or password', 'danger')

        cursor.close()
        connection.close()
        tunnel.stop()

    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    session.clear()  # Clear session upon logout
    return redirect(url_for('login'))

# Protecting routes with login_required decorator
@app.route('/create_user', methods=['GET', 'POST'])
@login_required
def create_user():
    # Ensure the user is an admin
    if session['user']['role'] != 'admin':
        return redirect(url_for('dashboard'))

    form = CreateUserForm()
    if request.method == 'POST' and form.validate_on_submit():
        # Collect form data
        data = {
            'name': form.name.data,
            'second_name': form.second_name.data,
            'last_name': form.last_name.data,
            'second_last_name': form.second_last_name.data,
            'email': form.email.data,
            'phone': form.phone.data,
            'role': form.role.data,
            'password': form.password.data
        }

        # Create a worker using the WorkerModel class
        worker_model = WorkerModel()
        if worker_model.create_worker(data):
            flash('User created successfully!', 'success')
        else:
            flash('Error creating user.', 'danger')

        return redirect(url_for('dashboard'))

    return render_template('create_user.html', form=form)

@app.route('/add_case', methods=['GET', 'POST'])
@login_required
def add_case():
    return render_template('add_case.html')

@app.route('/edit_case', methods=['GET', 'POST'])
@login_required
def edit_case():
    return render_template('edit_case.html')

@app.route('/delete_case', methods=['GET', 'POST'])
@login_required
def delete_case():
    return render_template('delete_case.html')

@app.route('/view_case', methods=['GET', 'POST'])
@login_required
def view_case():
    return render_template('view_case.html')

if __name__ == "__main__":
    app.run(debug=True)