from flask import Flask, render_template, request, redirect, url_for, session, flash
import secrets  # For generating secret key
from dotenv import load_dotenv
import os
from flask_wtf import CSRFProtect
import pyotp  # For 2FA verification
from hashlib import sha256  # For password hashing
from forms import LoginForm, CreateUserForm
from config import mysql_connection, ssh_tunnel
from models.worker_model import WorkerModel
from functools import wraps  # For fixing route decorator issues
import qrcode

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
csrf = CSRFProtect(app)

# Function to verify hashed password
def verify_password(stored_password, provided_password):
    return stored_password == sha256(provided_password.encode('utf-8')).hexdigest()

# Decorator to ensure user is authenticated
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
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', current_user=session['user'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        print("Login form submitted.")  # Debug
        if form.validate_on_submit():
            print("Form validated successfully.")  # Debug
            email = form.email.data
            password = form.password.data
            two_factor_code = form.two_factor_code.data

            # Start the SSH tunnel
            tunnel = ssh_tunnel()
            tunnel.start()
            print("SSH tunnel started.")  # Debug

            # Connect to MySQL
            connection = mysql_connection(tunnel)
            cursor = connection.cursor()
            print("Connected to MySQL.")  # Debug

            # Query user details
            query = "SELECT email, hashed_password, 2fa_secret, 2fa_enabled, name, role FROM workers WHERE email = %s"
            cursor.execute(query, (email,))
            user = cursor.fetchone()
            print("User query executed.")  # Debug

            if user:
                db_email, db_password, db_2fa_secret, db_2fa_enabled, db_name, db_role = user
                print(f"User found: {db_email}, Role: {db_role}")  # Debug

                # Verify password
                if verify_password(db_password, password):
                    print("Password verified.")  # Debug
                    if db_2fa_enabled:
                        totp = pyotp.TOTP(db_2fa_secret)
                        expected_code = totp.now()
                        print(f"2FA Secret in DB: {db_2fa_secret}")  # Log 2FA Secret
                        print(f"Expected 2FA code: {expected_code}")  # Log expected code
                        print(f"User-entered 2FA code: {two_factor_code}")  # Log entered code
                        if totp.verify(two_factor_code):
                            print("2FA code verified.") # Debug
                            # Set session
                            session['user'] = {
                                'name': db_name,
                                'email': db_email,
                                'role': db_role
                            }
                            print("Session set.")  # Debug
                            tunnel.stop()
                            return redirect(url_for('dashboard'))
                        else:
                            print("Invalid 2FA code.")  # Debug
                            flash('Invalid 2FA code', 'danger')
                    else:
                        flash('2FA is required for login.', 'danger')
                else:
                    print("Invalid password.")  # Debug
                    flash('Invalid password', 'danger')
            else:
                print("No user found with that email.")  # Debug
                flash('Invalid email or password', 'danger')

            cursor.close()
            connection.close()
            tunnel.stop()
        else:
            print("Form validation failed.")  # Debug
            print("Form errors:", form.errors)  # Debug
            flash('Form validation failed. Please check the input fields.', 'danger')

    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
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
            # Generate 2FA secret and QR code
            new_user_2fa_secret = worker_model.generate_2fa_secret()
            print(f"Generated 2FA secret for {data['email']}: {new_user_2fa_secret}")

            # Save 2FA secret in session to retrieve on login verification
            session['temp_2fa_secret'] = new_user_2fa_secret
            otp_uri = pyotp.TOTP(new_user_2fa_secret).provisioning_uri(name=data['email'], issuer_name="SecureLawFirm")

            # Define QR code path
            qr_code_dir = os.path.join(app.root_path, 'static', 'qrcodes')
            os.makedirs(qr_code_dir, exist_ok=True)
            qr_code_path = os.path.join(qr_code_dir, f"{data['email']}_2fa_qr.png")
            qr_code_img = qrcode.make(otp_uri)
            qr_code_img.save(qr_code_path)

            flash('User created successfully! Scan the QR code with Google Authenticator.', 'success')
            return render_template('display_qr.html', qr_code_path=f"/static/qrcodes/{data['email']}_2fa_qr.png")
        else:
            flash('Error creating user.', 'danger')

    return render_template('signup.html', form=form)

@app.route('/verify_2fa', methods=['GET', 'POST'])
def verify_2fa():
    if request.method == 'POST':
        two_factor_code = request.form.get('two_factor_code')

        # Retrieve temporary 2FA secret and user data
        new_user_2fa_secret = session.get('temp_2fa_secret')
        if new_user_2fa_secret:
            totp = pyotp.TOTP(new_user_2fa_secret)
            if totp.verify(two_factor_code):
                # Clear temporary 2FA secret from session
                session.pop('temp_2fa_secret', None)
                flash('Account created successfully. You can now log in.', 'success')
                return redirect(url_for('login'))
            else:
                flash('Invalid 2FA code. Please try again.', 'danger')

    return render_template('verify_2fa.html')

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
