from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash # Ensure you use this for secure password checking
from models import User
from forms import LoginForm
from extensions import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # 1. FIX: Redirect if user is already logged in
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin.admin_dashboard'))
        elif current_user.role == 'doctor':
            return redirect(url_for('doctor.doctor_dashboard'))
        elif current_user.role == 'patient':
            return redirect(url_for('patient.patient_dashboard'))
        
    # 2. FIX: Use the Flask-WTF Form
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        # 3. FIX: Secure password check
        # Note: If your User model has a method check_password(), use user.check_password(form.password.data)
        # Otherwise, use check_password_hash(user.password_hash, form.password.data)
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash('Logged in successfully.', 'success')
            
            # Role-based Redirect
            if user.role == 'admin':
                return redirect(url_for('admin.admin_dashboard'))
            elif user.role == 'doctor':
                return redirect(url_for('doctor.doctor_dashboard'))
            elif user.role == 'patient':
                return redirect(url_for('patient.patient_dashboard'))
            else:
                return redirect(url_for('index'))
        else:
            flash('Invalid email or password.', 'danger')
            
    # 4. FIX: Pass the form to the template
    return render_template('login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))