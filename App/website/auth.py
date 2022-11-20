"""Utilized to manipulate the back-end of all authentication views."""
from datetime import datetime, date
import re
from sys import breakpointhook
import geocoder
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User, FailedAttempts
from . import db, emails
import socket


auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    """Back-end portion of login.html found in the templates folder."""
    if request.method == 'POST':
        if request.form['action'] == 'login':
            email = request.form.get('email')
            password = request.form.get('password')
            current_date = datetime.now()
            format_date = current_date.strftime("%d/%m/%Y %H:%M:%S")
            
            user = User.query.filter_by(email=email).first()

            if user:
                if check_password_hash(user.password, password):
                    login_user(user, remember=True)
                    flash(f'Welcome {current_user.user_name}!', category='success')
                    return redirect(url_for('views.home'))
                else:
                    hostname = socket.gethostname()
                    user_ip = socket.gethostbyname(hostname)
                    ip = geocoder.ip('me')
                    location = ip.city
                    failure = FailedAttempts(email=email, ip=user_ip, date=format_date,
                                         location=location)
                    db.session.add(failure)
                    db.session.commit()
                    flash('Incorrect email and/or password.', category='error')
            else:
                flash('Incorrect email and/or password. test', category='error')
            
    return render_template('login.html', user=current_user)


@auth.route('/logout')
@login_required
def logout():
    """Utilized to logout the current user. They will then be redirected back to the login/signup pages."""
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/signup', methods=['GET', 'POST'])
def sign_up():
    """Back-end portion of signup.html found in the templates folder."""
    if request.method == 'POST':
        userDetails = request.form
        email = request.form.get('email')
        user_name = request.form.get('userName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        weight = request.form.get('weight')
        height = request.form.get('height')
        ethnicity = userDetails['ethnicity']
        birth_month = userDetails['dob-month']
        birth_year = userDetails['dob-year']
        birth_day = userDetails['dob-day']
        blood_type = userDetails['blood-type']

        if birth_month == '01':
            month = 'January'
        elif birth_month == '02':
            month = 'February'
        elif birth_month == '03':
            month = 'March'
        elif birth_month == '04':
            month = 'April'
        elif birth_month == '05':
            month = 'May'
        elif birth_month == '06':
            month = 'June'
        elif birth_month == '07':
            month = 'July'
        elif birth_month == '08':
            month = 'August'
        elif birth_month == '09':
            month = 'September'
        elif birth_month == '10':
            month = 'October'
        elif birth_month == '11':
            month = 'November'
        elif birth_month == '12':
            month = 'December'

        reg = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{12,20}$"
        match_re = re.compile(reg)
        res = re.search(match_re, password1)
        user_name_lowercase = user_name.lower()
        user = User.query.filter_by(email=email).first()
        patient_id = 1

        dob = month + " " + birth_day + ", " + birth_year
        today = date.today()
        birthday_month = int(birth_month)
        birthday_day = int(birth_day)
        birthday_year = int(birth_year)
        one_or_zero = ((today.month, today.day) < (birthday_month, birthday_day))
        year_difference = today.year - birthday_year
        age = year_difference - one_or_zero

        if user:
            flash('User already exists', category='error')
        elif db.session.query(db.exists().where(User.user_name == user_name_lowercase)).scalar():
            flash('Username already exists. Please try again.', category='error')
        elif ' ' in user_name:
            flash('Can\'t have space in username.', category='error')
        elif not res:
            flash('Password must have 12 characters, 1 uppercase, 1 lowercase, 1 number, '
                  'and 1 special character!', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        else:
            new_user = User(patient_id = patient_id, email=email, user_name=user_name_lowercase, password=generate_password_hash(
                password1, method='sha256'), first_name=first_name.title(), last_name=last_name.title(), weight=weight, height=height, ethnicity=ethnicity.title(), birthday=dob, blood=blood_type, age=age)
            
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            current_user.patient_id = 10000000 + current_user.id
            db.session.commit()
            flash('Account Created', category='success')
            try:
                emails.AccountCreationEmail()
            except:
                flash('Account Creation email was not sent. Feel free to add your personal gmail information in emails.py', category='error')
            return redirect(url_for('views.home'))

    return render_template('signup.html', user=current_user)
