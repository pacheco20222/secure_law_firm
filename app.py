# app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import SessionLocal, close_tunnels, mongo_db  
from models.worker_model import Worker
from services.auth_service import verify_password, verify_2fa_code, hash_password, generate_2fa_secret, generate_qr_code
from forms import LoginForm, SignupForm
from models.case_model import Case
from models.client_model import Client
from forms import CaseForm
from sqlalchemy.exc import IntegrityError
import secrets
import os
from datetime import datetime
import base64
from services.digitalocean_space_service import upload_file_to_space, delete_file_from_space

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Default route
@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        db_session = SessionLocal()
        user = db_session.query(Worker).get(session['user'])

        # Retrieve cases based on user role
        if user.role == 'admin':
            cases = db_session.query(Case).all()
        elif user.role == 'lawyer':
            cases = db_session.query(Case).filter_by(worker_id=user.id).all()
        else:  # For assistants, show only their assigned cases
            cases = db_session.query(Case).join(Client, Case.client_id == Client.id).filter(Client.worker_id == user.id).all()
        
        db_session.close()
        return render_template('dashboard.html', current_user=user, cases=cases)
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    db_session = SessionLocal()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        two_factor_code = form.two_factor_code.data

        user = db_session.query(Worker).filter_by(email=email).first()
        if user and verify_password(user.hashed_password, password):
            if user.two_fa_enabled and verify_2fa_code(user.two_fa_secret, two_factor_code):
                session['user'] = user.id
                flash('Login successful!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid 2FA code.', 'danger')
        else:
            flash('Invalid email or password.', 'danger')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{field.capitalize()}: {error}", 'danger')

    db_session.close()
    return render_template('login.html', form=form, current_user=None)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        db_session = SessionLocal()
        try:
            hashed_password = hash_password(form.password.data)
            two_fa_secret = generate_2fa_secret()

            new_user = Worker(
                name=form.name.data,
                second_name=form.second_name.data,
                last_name=form.last_name.data,
                second_last_name=form.second_last_name.data,
                email=form.email.data,
                phone=form.phone.data,
                role=form.role.data,
                company_id=f"LR-{db_session.query(Worker).count() + 1:03d}",
                hashed_password=hashed_password,
                two_fa_secret=two_fa_secret,
                two_fa_enabled=True
            )

            db_session.add(new_user)
            db_session.commit()

            qr_code_path = generate_qr_code(form.email.data, "SecureLawFirm", two_fa_secret)
            relative_qr_code_path = f"qrcodes/{os.path.basename(qr_code_path)}"

            flash("User created successfully! Scan the QR code for 2FA setup.", "success")
            return render_template('display_qr.html', qr_code_path=relative_qr_code_path, current_user=None)

        except IntegrityError:
            db_session.rollback()
            flash("Error: Email or phone number already exists.", "danger")
        finally:
            db_session.close()
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{field.capitalize()}: {error}", 'danger')

    return render_template('signup.html', form=form, current_user=None)

# Logout route
@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

@app.route('/add_case', methods=['GET', 'POST'])
def add_case():
    form = CaseForm()
    db_session = SessionLocal()
    
    # Load workers for lawyer and assistant selection
    form.lawyer_id.choices = [(w.id, w.name) for w in db_session.query(Worker).filter_by(role='lawyer').all()]
    form.assistant_id.choices = [(0, 'None')] + [(w.id, w.name) for w in db_session.query(Worker).filter_by(role='assistant').all()]

    if form.validate_on_submit():
        try:
            # Check if client exists or create a new one
            client = db_session.query(Client).filter_by(email=form.client_email.data).first()
            if not client:
                client = Client(
                    name=form.client_name.data,
                    second_name=form.client_second_name.data,
                    last_name=form.client_last_name.data,
                    second_last_name=form.client_second_last_name.data,
                    email=form.client_email.data,
                    phone=form.client_phone.data,
                    address=form.client_address.data
                )
                db_session.add(client)
                db_session.commit()

            # Upload document to DigitalOcean Spaces
            uploaded_file = request.files.get("document")
            if uploaded_file:
                file_url = upload_file_to_space(uploaded_file)
            else:
                file_url = None

            # Insert document metadata into MongoDB
            document_data = {
                "case_id": None,  # Placeholder to update after MySQL insertion
                "client_id": client.id,
                "worker_id": form.lawyer_id.data,
                "document_title": form.document_title.data,
                "document_description": form.document_description.data,
                "file_url": file_url,
                "uploaded_by": "Admin",
                "uploaded_at": datetime.utcnow(),
                "last_modified": datetime.utcnow(),
                "file_type": uploaded_file.content_type if uploaded_file else "application/octet-stream",
                "document_tags": ["tag1", "tag2"]
            }
            document_id = mongo_db.documents.insert_one(document_data).inserted_id

            # Create the case entry in MySQL and link it with MongoDB document
            new_case = Case(
                client_id=client.id,
                worker_id=form.lawyer_id.data,
                case_title=form.case_title.data,
                case_description=form.case_description.data,
                case_type=form.case_type.data,
                court_date=form.court_date.data,
                judge_name=form.judge_name.data
            )
            db_session.add(new_case)
            db_session.commit()

            # Update MongoDB document with the actual MySQL case_id
            mongo_db.documents.update_one(
                {"_id": document_id},
                {"$set": {"case_id": new_case.id}}
            )

            flash("Case created successfully and linked with document in DigitalOcean Spaces.", "success")
            return redirect(url_for('dashboard'))

        except Exception as e:
            db_session.rollback()
            flash(f"Error creating case: {e}", "danger")
        finally:
            db_session.close()
    
    return render_template('add_case.html', form=form)


from bson.objectid import ObjectId  # Import to handle ObjectId conversion

@app.route('/edit_document/<document_id>', methods=['GET', 'POST'])
def edit_document(document_id):
    db_session = SessionLocal()
    user = db_session.query(Worker).get(session['user'])

    # Convert document_id to ObjectId
    document = mongo_db.documents.find_one({"_id": ObjectId(document_id)})
    if not document:
        flash("Document not found.", "danger")
        return redirect(url_for('dashboard'))

    # Ensure the user has permission
    if user.role != 'admin' and document['worker_id'] != user.id:
        flash("You do not have permission to edit this document.", "danger")
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        # Get updated values from the form
        updated_title = request.form.get('document_title')
        updated_description = request.form.get('document_description')
        updated_tags = request.form.get('document_tags').split(',')

        # Update the document in MongoDB
        mongo_db.documents.update_one(
            {"_id": ObjectId(document_id)},
            {"$set": {
                "document_title": updated_title,
                "document_description": updated_description,
                "document_tags": [tag.strip() for tag in updated_tags],
                "last_modified": datetime.utcnow()
            }}
        )
        flash("Document updated successfully.", "success")
        return redirect(url_for('view_case_details', case_id=document['case_id']))

    db_session.close()
    return render_template('edit_document.html', document=document)


@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/delete_case')
def delete_case():
    return render_template('delete_case.html')

# Close session and SSH tunnel on teardown
@app.teardown_appcontext
def shutdown_session(exception=None):
    close_tunnels()  # Corrected function call to close_tunnels

if __name__ == "__main__":
    app.run(debug=True)
