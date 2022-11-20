from email.message import EmailMessage
import smtplib
import ssl
from flask_login import current_user
from .models import Appointments


def AccountCreationEmail():
    email = current_user.email
    username = current_user.user_name
    first_name = current_user.first_name
    last_name = current_user.last_name

    email_sender = 'lucedeveloper@gmail.com'
    email_password = '' # For security reasons I have removed my personal password. Please feel free to add your information to send emails.

    subject = 'Cap5 Scheduling Account Creation'

    body = f'Dear {first_name} {last_name},\n\nThank you for signing up and creating an account!\n\nYour username is {username}.\n\nRespectfully,\n\nCapstone Team 5 '

    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email
    em['Subject'] = subject
    em.set_content(body)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email, em.as_string())


def AppointmentCreation(doctor, appointment_date, appointment_time, first_name, last_name):
    email = current_user.email
    first_name = first_name
    last_name = last_name
    doctor = doctor
    appointment_date = appointment_date

    email_sender = 'lucedeveloper@gmail.com'
    email_password = '' # For security reasons I have removed my personal password. Please feel free to add your information to send emails.

    subject = 'Appointment Creation'

    body = f'Dear {first_name} {last_name},\n\nThank you for scheduling an appointment with {doctor}. \n\nYour appointment is scheduled for {appointment_date} @ {appointment_time}.\n\nWe look forward to seeing you.\
         \n\nRespectfully,\n\nCapstone Team 5 '

    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email
    em['Subject'] = subject
    em.set_content(body)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email, em.as_string())


def AppointmentDelete(doctor, appointment_date, appointment_time, patient_name, patient_email):
    
    email = patient_email
    email_sender = 'lucedeveloper@gmail.com'
    email_password = '' # For security reasons I have removed my personal password. Please feel free to add your information to send emails.

    subject = 'Appointment Deletion'

    body = f'Dear {patient_name},\n\nYour appointment with {doctor} on {appointment_date} @ {appointment_time} has been canceled.\
    \n\nRespectfully,\n\nCapstone Team 5 '

    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email
    em['Subject'] = subject
    em.set_content(body)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email, em.as_string())
