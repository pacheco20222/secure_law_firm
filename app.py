from flask import Flask, render_template, request, redirect, url_for, session, flash
from dotenv import load_dotenv
import os
from flask_wtf import CSRFProtect
import pyotp  # For 2FA verification
from hashlib import sha256  # For password hashing
from forms import LoginForm  # Import the form class
from config import mysql_connection, ssh_tunnel  # Import tunnel functions from config.py

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

# Check if the secret key is loaded properly (for debugging)
if not app.secret_key:
    raise RuntimeError("SECRET_KEY is not set. Please check your .env file.")

csrf = CSRFProtect(app)

# Function to verify the password (hashed)
def verify_password(stored_password, provided_password):
    return stored_password == sha256(provided_password.encode('utf-8')).hexdigest()

@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', current_user=session['user'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        two_factor_code = form.two_factor_code.data  # Get the 2FA code from the form

        # Start the SSH tunnel using the existing function
        tunnel = ssh_tunnel()
        tunnel.start()

        # Use the existing MySQL connection function via SSH tunnel
        connection = mysql_connection(tunnel)
        cursor = connection.cursor()

        # Query to fetch the user details from the database
        query = "SELECT email, hashed_password, 2fa_secret, 2fa_enabled, name FROM workers WHERE email = %s"
        cursor.execute(query, (email,))
        user = cursor.fetchone()  # Fetch the user record

        if user:
            # Unpack user details
            db_email, db_password, db_2fa_secret, db_2fa_enabled, db_name = user

            # Verify the password
            if verify_password(db_password, password):
                if db_2fa_enabled:  # If 2FA is enabled, verify the 2FA code
                    totp = pyotp.TOTP(db_2fa_secret)
                    if totp.verify(two_factor_code):
                        # Successful login, store session
                        session['user'] = {'name': db_name, 'email': db_email}
                        tunnel.stop()  # Stop the SSH tunnel
                        return redirect(url_for('dashboard'))
                    else:
                        flash('Invalid 2FA code', 'danger')
                else:
                    # Login without 2FA
                    session['user'] = {'name': db_name, 'email': db_email}
                    tunnel.stop()  # Stop the SSH tunnel
                    return redirect(url_for('dashboard'))
            else:
                flash('Invalid password', 'danger')
        else:
            flash('Invalid email or password', 'danger')

        # Close the connection and stop the tunnel
        cursor.close()
        connection.close()
        tunnel.stop()

    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))


@app.route('/add_case', methods=['GET', 'POST'])
def add_case():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('add_case.html')


@app.route('/edit_case', methods=['GET', 'POST'])
def edit_case():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('edit_case.html')


@app.route('/delete_case', methods=['GET', 'POST'])
def delete_case():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('delete_case.html')


@app.route('/view_case', methods=['GET', 'POST'])
def view_case():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('view_case.html')



if __name__ == "__main__":
    app.run(debug=True)