"""This file is utilized for all back-end that does not pertain to authentication of a user account."""
import email
import re
import geocoder as geocoder
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from . import db, emails
from website.models import User, Appointments
from datetime import datetime, date
import json


views = Blueprint('views', __name__)


@views.route('/')
@login_required
def home():
    """Utilized to store back-end code for the websites home page."""
    weight_pounds = current_user.weight
    weight_kilograms = weight_pounds * .453592
    height_inches = current_user.height
    height_centimeters = height_inches * 2.54    
    bmi = weight_kilograms / (height_centimeters/100)**2
    appointments = Appointments.query.all()
    count = 0

    if bmi <= 18.4:
        range = 'You are underweight.'
    elif bmi <= 24.9:
        range = 'You are healthy.'
    elif bmi <= 29.9:
        range = 'You are over weight.'
    elif bmi <= 34.9:
        range = 'You are severely over weight.'
    elif bmi <= 39.9:
        range = 'You are obese.'
    else:
        range = 'You are severly obese.'

    for appointments in appointments:
        if appointments.user_id == current_user.patient_id:
            count += 1
        elif appointments.doctor == current_user.user_name:
            count += 1

    return render_template('home.html', user=current_user, appointments=appointments, count=count, bmi=bmi, range=range)


@views.route('/profile/appointments', methods=['GET', 'POST'])
@login_required
def profile():
    """Utilized to store back-end code for the profile page."""

    if request.method == 'POST':
        email = current_user.email
        first_name=current_user.first_name
        last_name=current_user.last_name
        doctor = request.form.get('primary-doctor')
        appointment_date = request.form.get('date')
        appointment_time = request.form.get('time')
        patient_concerns = request.form.get('yesAnswer')
        doctor_concerns = (' ')

        appointments = Appointments.query.all()

        for appointments in appointments:
            if appointments.doctor == doctor and appointments.date == appointment_date and appointments.time == appointment_time:
                        flash('This appointment slot is taken.', category='error')
                        return redirect(url_for('views.profile'))

        new_appointment = Appointments(email=email, doctor=doctor, date=appointment_date, time=appointment_time, 
        patient_concerns=patient_concerns, doctor_notes=doctor_concerns, user_id=current_user.patient_id,
        first_name=first_name, last_name=last_name)

        db.session.add(new_appointment)
        db.session.commit()
        flash('Appointment Created', category='success')
        try:
            emails.AppointmentCreation(doctor, appointment_date, appointment_time, first_name, last_name)
        except:
            flash('Account Creation email was not sent. Feel free to add your personal gmail information in emails.py', category='error')
        return redirect(url_for('views.profile'))


    return render_template('profile.html', user=current_user,
                           email=current_user.email.title(),
                           username=current_user.user_name,
                           first_name=current_user.first_name.title(),
                           last_name=current_user.last_name.title(), 
                           patient_id=current_user.patient_id, 
                           weight=current_user.weight, 
                           height=current_user.height, 
                           ethnicity=current_user.ethnicity, 
                           birthday=current_user.birthday, 
                           blood_type=current_user.blood)


@views.route('/doctor-profile/appointments', methods=['GET', 'POST'])
@login_required
def doctor_profile():
    """Utilized to store back-end code for the profile page."""

    first_name = current_user.first_name
    last_name = current_user.last_name
    user_name = current_user.user_name

    appointments = Appointments.query.all()

    return render_template('doctorprofile.html', first_name=first_name, last_name=last_name, user_name=user_name, email=email, date=date, appointments=appointments)


@views.route('/doctor-profile/patient-search', methods=['GET', 'POST'])
@login_required
def patient_search():
    """Utilized to store back-end code for the profile page."""
    if request.method == 'POST':
        id = request.form.get('id')
        patient = User.query.filter_by(patient_id=id).first()
        if patient:
            patient_id = patient.patient_id
            patient_email = patient.email
            patient_user_name = patient.user_name
            patient_first_name = patient.first_name
            patient_last_name = patient.last_name
            patient_weight = patient.weight
            patient_height = patient.height
            patient_ethnicity = patient.ethnicity
            patient_birthday = patient.birthday
            patient_age = patient.age
            patient_blood = patient.blood
            appointments = patient.appointments
            
            return render_template('patientsearch.html', first_name=current_user.first_name,
    last_name=current_user.last_name, patient_email=patient_email, patient_user_name=patient_user_name,
    patient_first_name=patient_first_name, patient_last_name=patient_last_name, patient_weight=patient_weight,
    patient_height=patient_height, patient_ethnicity=patient_ethnicity, patient_birthday=patient_birthday,
    patient_age=patient_age, patient_blood=patient_blood, patient_id=patient_id, appointments=appointments)

        else:
            flash('Patient doesn\'t exist', category='error')

    return render_template('patientsearch.html', first_name=current_user.first_name,
    last_name=current_user.last_name)


@views.route('/profile/health-data', methods=['GET', 'POST'])
@login_required
def health_data():
    """Utilized to store back-end code for the health-data page."""
    ip = geocoder.ip('me')
    location = ip.city

    return render_template('healthdata.html', user=current_user,
                           email=current_user.email.title(),
                           username=current_user.user_name,
                           first_name=current_user.first_name.title(),
                           last_name=current_user.last_name.title(), 
                           patient_id=current_user.patient_id, 
                           location=location, weight=current_user.weight, 
                           height=current_user.height, 
                           ethnicity=current_user.ethnicity, 
                           birthday=current_user.birthday, 
                           blood_type=current_user.blood, age=current_user.age)


@views.route('/settings/general')
@login_required
def general():
    """Utilized to store back-end code for the general page."""
    ip = geocoder.ip('me')
    location = ip.city

    return render_template('general.html',
                        user=current_user,
                           email=current_user.email.lower(),
                           username=current_user.user_name,
                           first_name=current_user.first_name.title(),
                           last_name=current_user.last_name.title(),
                           location=location)


@views.route('/settings/update-password', methods=['GET', 'POST'])
@login_required
def security_and_login():
    """Utilized to store back-end code for the security and login page. This allows the user to change their password."""
    if request.method == 'POST':
        password = request.form.get('password')
        password3 = request.form.get('password3')
        password4 = request.form.get('password4')

        reg = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{12,20}$"
        match_re = re.compile(reg)
        res = re.search(match_re, password3)

        if check_password_hash(current_user.password, password):
            if not res:
                flash('Password must have 12 characters, 1 uppercase, 1 lowercase, 1 number, '
                      'and 1 special character!', category='error')
            elif password3 != password4:
                flash('Passwords don\'t match.', category='error')
            elif password3 == password:
                flash('Password must differ from old password.', category='error')
            else:
                current_user.password = generate_password_hash(password3, method='sha256')
                db.session.commit()
                flash('Password Updated!', category='success')
        else:
            flash('Existing password is incorrect', category='error')

    return render_template('updatepassword.html', user=current_user)


@views.route('/settings/edit-username', methods=['GET', 'POST'])
@login_required
def edit_username():
    """Utilized to store back-end code for the edit username page. This allows the user to change their username."""
    if request.method == 'POST':
        username = request.form.get('username')
        username2 = request.form.get('username2')
        username3 = request.form.get('username3')
        user_name_lowercase = username2.lower()

        if current_user.user_name == username:
            if db.session.query(db.exists().where(User.user_name == username2)).scalar():
                flash('Username already exists. Please try again.', category='error')
            elif ' ' in username2:
                flash('Can\'t have space in username.', category='error')
            elif username2 != username3:
                flash('Usernames don\'t match.', category='error')
            elif username2 == username:
                flash('New username must differ from old.', category='error')
            else:
                current_user.user_name = user_name_lowercase
                db.session.commit()
                flash('Username updated!', category='success')
                return redirect(url_for('views.general'))
        else:
            flash('Current username is incorrect.', category='error')

    return render_template('updateusername.html', user=current_user)


@views.route('/settings/edit-email', methods=['GET', 'POST'])
@login_required
def edit_email():
    """Utilized to store back-end code for the edit email page. This allows the user to change their email."""
    if request.method == 'POST':
        email1 = request.form.get('email')
        email2 = request.form.get('email2')
        email3 = request.form.get('email3')

        if current_user.email == email1:
            if db.session.query(db.exists().where(User.email == email2)).scalar():
                flash('Email already exists. Please select a unique email.', category='error')
            elif email2 != email3:
                flash('Emails don\'t match.', category='error')
            elif email2 == email1:
                flash('New email must differ from old.', category='error')
            else:
                current_user.email = email2
                db.session.commit()
                flash('Email updated!', category='success')
                return redirect(url_for('views.general'))
        else:
            flash('Current email is incorrect.', category='error')

    return render_template('updateemail.html', user=current_user)


@views.route('/settings/edit-name', methods=['GET', 'POST'])
@login_required
def edit_name():
    """Utilized to store back-end code for the edit name page. This allows the user to change their name."""
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')

        if first_name == '':
            flash('First name can\'t be blank.', category='error')
        elif last_name == '':
            flash('Last name can\'t be blank.', category='error')
        else:
            current_user.first_name = first_name
            current_user.last_name = last_name
            db.session.commit()
            flash('Name updated!', category='success')
            return redirect(url_for('views.general'))

    return render_template('updatename.html', user=current_user)


@views.route('/profile/health-data/edit-weight', methods=['GET', 'POST'])
@login_required
def edit_weight():
    """Utilized to store back-end code for the edit name page. This allows the user to change their name."""

    if request.method == 'POST':
        new_weight = request.form.get('new-weight')
        current_user.weight = new_weight
        db.session.commit()
        flash('Weight updated!', category='success')
        return redirect(url_for('views.health_data'))

    return render_template('updateweight.html', first_name=current_user.first_name, last_name=current_user.last_name, weight=current_user.weight)


@views.route('/profile/health-data/edit-height', methods=['GET', 'POST'])
@login_required
def edit_height():
    """Utilized to store back-end code for the edit name page. This allows the user to change their name."""
    if request.method == 'POST':
        new_height = request.form.get('new-height')
        current_user.height = new_height
        db.session.commit()
        flash('Height updated!', category='success')
        return redirect(url_for('views.health_data'))

    return render_template('updateheight.html', first_name=current_user.first_name, last_name=current_user.last_name, height=current_user.height)


@views.route('/profile/health-data/edit-ethnicity', methods=['GET', 'POST'])
@login_required
def edit_ethnicity():
    """Utilized to store back-end code for the edit name page. This allows the user to change their name."""
    if request.method == 'POST':
        new_ethnicity = request.form.get('new-ethnicity')
        current_user.ethnicity = new_ethnicity
        db.session.commit()
        flash('Ethnicity updated!', category='success')
        return redirect(url_for('views.health_data'))

    return render_template('updateethnicity.html', first_name=current_user.first_name, last_name=current_user.last_name, ethnicity=current_user.ethnicity)


@views.route('/settings/delete-account', methods=['GET', 'POST'])
@login_required
def delete_account():
    """Utilized to store back-end code for the delete profile page. This allows the user to permanently delete their profile."""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if email == "":
            flash('Email can\'t be blank.', category='error')
        elif password != password2:
            flash('Passwords don\'t match', category='error')
        elif email != current_user.email:
            flash('Incorrect email.', category='error')
        elif not check_password_hash(user.password, password):
            flash('Incorrect password.', category='error')
        else:
            flash(f'Account for user {current_user.user_name} has been deleted! You are being '
                  f'directed to the Signup page.', category='success')
            db.session.delete(user)
            db.session.commit()
            return redirect(url_for('auth.sign_up'))

    return render_template('deleteaccount.html', user=current_user)


@views.route('/delete-appointments', methods=['POST'])
@login_required
def delete_appointments():
    appointments = json.loads(request.data)
    appointmentsId = appointments['appointmentsId']
    appointments = Appointments.query.get(appointmentsId)
    patient_name = f'{appointments.first_name} {appointments.last_name}'
    appointment_date = appointments.date
    appointment_time = appointments.time
    doctor = appointments.doctor
    patient_email = appointments.email

    if appointments:
        if appointments.user_id == current_user.patient_id:
            try:
                emails.AppointmentDelete(doctor, appointment_date, appointment_time, patient_name, patient_email)
            except:
                flash('Account Creation email was not sent. Feel free to add your personal gmail information in emails.py', category='error')
            db.session.delete(appointments)
            db.session.commit()
        elif appointments.doctor == current_user.user_name:
            try:
                emails.AppointmentDelete(doctor, appointment_date, appointment_time, patient_name, patient_email)
            except:
                flash('Account Creation email was not sent. Feel free to add your personal gmail information in emails.py', category='error')
            db.session.delete(appointments)
            db.session.commit()
            
    return jsonify({})