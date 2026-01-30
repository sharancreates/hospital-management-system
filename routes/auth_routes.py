from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from models import User
from forms import LoginForm, RequestResetForm
from extensions import db
from forms import ResetPasswordForm

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin.admin_dashboard'))
        elif current_user.role == 'doctor':
            return redirect(url_for('doctor.doctor_dashboard'))
        elif current_user.role == 'patient':
            return redirect(url_for('patient.patient_dashboard'))
        
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash('Logged in successfully.', 'success')
            
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
            
    return render_template('login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        token = user.get_reset_token()
        
        reset_url = url_for('auth.reset_token', token=token, _external=True)
        
        flash(f'''
            <span class="font-bold">DEMO MODE:</span> 
            No email server configured. 
            <a href="{reset_url}" class="underline text-blue-400 font-bold hover:text-blue-300">
                Click here to Reset Password
            </a>
        ''', 'info')
        
        return redirect(url_for('auth.login'))
        
    return render_template('forgot_password.html', title='Reset Password', form=form)


@auth_bp.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_token(token)
    
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('auth.reset_request'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user.password_hash = hashed_password
        db.session.commit()
        flash('Your password has been updated! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('reset_token.html', title='Reset Password', form=form)