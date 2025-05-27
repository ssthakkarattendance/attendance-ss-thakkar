import streamlit as st
import os
import base64
import pandas as pd
from datetime import datetime
from utils.geo_utils import is_within_radius
from utils.email_utils import send_attendance_email

# --- Constants ---
OFFICE_LAT = 22.95737828393304
OFFICE_LON = 72.65556970977924
EXCEL_FILE = "data/attendance_log.xlsx"
PHOTO_FOLDER = "photos"
ADMIN_USERNAME = st.secrets["admin"]["username"]
ADMIN_PASSWORD = st.secrets["admin"]["password"]

# --- Utility ---
def save_photo(photo_data, username):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    user_folder = os.path.join(PHOTO_FOLDER, username)
    os.makedirs(user_folder, exist_ok=True)
    file_path = os.path.join(user_folder, f"{timestamp}.jpg")
    with open(file_path, "wb") as f:
        f.write(photo_data)
    return file_path

def log_attendance(username, punch_type, lat, lon, photo_path):
    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")
    new_data = pd.DataFrame([[date, time, username, punch_type, lat, lon, photo_path]],
                            columns=["Date", "Time", "Name", "Punch Type", "Latitude", "Longitude", "Photo Path"])

    if os.path.exists(EXCEL_FILE):
        df = pd.read_excel(EXCEL_FILE)
        df = pd.concat([df, new_data], ignore_index=True)
    else:
        df = new_data
    df.to_excel(EXCEL_FILE, index=False)

def has_already_punched(username, punch_type):
    if not os.path.exists(EXCEL_FILE):
        return False
    df = pd.read_excel(EXCEL_FILE)
    today = datetime.now().strftime("%Y-%m-%d")
    return ((df['Date'] == today) & (df['Name'] == username) & (df['Punch Type'] == punch_type)).any()

# --- App Start ---
st.set_page_config(page_title="📍 Staff Attendance", layout="centered")

query_params = st.experimental_get_query_params()
username = query_params.get("user", [None])[0]
admin_param = query_params.get("admin", [None])[0]

# --- Admin Panel ---
if admin_param == ADMIN_USERNAME:
    st.title("🧑‍💼 Admin Dashboard")
    password = st.text_input("Enter admin password", type="password")
    if password == ADMIN_PASSWORD:
        if os.path.exists(EXCEL_FILE):
            df = pd.read_excel(EXCEL_FILE)
            st.dataframe(df)
            st.download_button("Download Excel", data=df.to_excel(index=False), file_name="attendance_log.xlsx")
        else:
            st.info("No attendance records yet.")
    else:
        st.warning("Invalid admin password.")
    st.stop()

# --- Employee Panel ---
if not username:
    st.error("No user specified in URL. Please use your unique link.")
    st.stop()

st.title(f"📍 Attendance - {username}")

with st.form("location_form"):
    st.markdown("**Step 1:** Share your live location")
    lat = st.text_input("Latitude")
    lon = st.text_input("Longitude")
    submit_loc = st.form_submit_button("Submit Location")

if submit_loc:
    try:
        user_lat = float(lat)
        user_lon = float(lon)
    except ValueError:
        st.error("Invalid latitude/longitude")
        st.stop()

    if not is_within_radius(user_lat, user_lon, OFFICE_LAT, OFFICE_LON):
        st.error("⛔ You are outside the allowed 100m office radius.")
        st.stop()

    st.success("✅ Location accepted.")

    st.markdown("**Step 2:** Take a live photo")
    photo = st.camera_input("Take a selfie to continue")

    if photo:
        st.success("✅ Photo captured.")

        # --- Punch Logic ---
        punch_type = None
        if not has_already_punched(username, "Punch In"):
            punch_type = "Punch In"
        elif not has_already_punched(username, "Punch Out"):
            punch_type = "Punch Out"
        else:
            st.info("You have already marked both Punch In and Punch Out today.")
            st.stop()

        photo_bytes = photo.getvalue()
        photo_path = save_photo(photo_bytes, username)
        log_attendance(username, punch_type, user_lat, user_lon, photo_path)
        send_attendance_email(username, punch_type, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), st.secrets["email"]["sender_email"])
        st.success(f"🎉 {punch_type} recorded successfully!")

        st.markdown(f"Photo saved at: `{photo_path}`")
    else:
        st.warning("📸 Please take a photo to continue.")
