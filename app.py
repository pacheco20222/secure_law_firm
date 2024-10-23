from flask import Flask, render_template, request, redirect, url_for, session, flash
from dotenv import load_dotenv
import os
from flask_wtf import CSRFProtect
from forms import LoginForm  # Import the form class

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')  # Get secret key from .env file

csrf = CSRFProtect(app)


# Dummy user data for demonstration
users = {
    'admin@example.com': {
        'password': 'admin123',
        'name': 'Admin User',
        '2fa_enabled': True,
        '2fa_code': '123456'  # Example 2FA code, normally this would be dynamic
    }
}

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
        two_factor_code = request.form.get('2fa_code')

        user = users.get(email)
        if user and user['password'] == password:
            if user['2fa_enabled']:
                if user['2fa_code'] == two_factor_code:
                    session['user'] = {'name': user['name'], 'email': email}
                    return redirect(url_for('dashboard'))
                else:
                    flash('Invalid 2FA code', 'danger')
            else:
                session['user'] = {'name': user['name'], 'email': email}
                return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'danger')
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


if __name__ == '__main__':
    csrf.init_app(app)  # Enable CSRF protection
    app.run(debug=True)