import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import streamlit as st

def send_attendance_email(name, punch_type, timestamp, receiver_email):
    config = st.secrets["email"]
    sender_email = config["sender_email"]
    app_password = config["app_password"]

    subject = f"📍 Attendance Recorded: {name} - {punch_type}"
    body = f"""
    <h3>Attendance Recorded</h3>
    <p><strong>Name:</strong> {name}</p>
    <p><strong>Type:</strong> {punch_type}</p>
    <p><strong>Time:</strong> {timestamp}</p>
    """

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, app_password)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        print(f" Email failed: {e}")
