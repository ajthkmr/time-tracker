import streamlit as st
import time
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import matplotlib.pyplot as plt

# Load Google Sheets credentials from Streamlit secrets
scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
credentials = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scopes)
client = gspread.authorize(credentials)

# Open the Google Sheet
SHEET_NAME = "Time-Tracker"  # Change this to your Google Sheet name
sheet = client.open(SHEET_NAME).sheet1

# Initialize session state
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "elapsed_time" not in st.session_state:
    st.session_state.elapsed_time = 0
if "running" not in st.session_state:
    st.session_state.running = False

# Retrieve the last active session from Google Sheets
def get_last_session():
    records = sheet.get_all_records()
    if records:
        last_entry = records[-1]  # Get last row
        if last_entry.get("Status") == "Running":
            return last_entry["Start Time"]
    return None

# Save session to Google Sheets
def save_work_session(status):
    date = pd.Timestamp.now().date()
    duration_minutes = round(st.session_state.elapsed_time / 60, 2)
    
    if status == "Running":
        sheet.append_row([str(date), duration_minutes, time.time(), "Running"])
    else:
        sheet.append_row([str(date), duration_minutes, "-", "Stopped"])

# Start timer
def start_timer():
    last_start_time = get_last_session()
    if last_start_time:
        st.session_state.start_time = float(last_start_time)  # Resume tracking
        st.session_state.running = True
    else:
        st.session_state.start_time = time.time()
        st.session_state.running = True
        save_work_session("Running")

# Pause timer
def pause_timer():
    if st.session_state.running:
        st.session_state.elapsed_time += time.time() - st.session_state.start_time
        st.session_state.running = False
        save_work_session("Stopped")

# Stop timer & save data
def stop_timer():
    if st.session_state.start_time:
        st.session_state.elapsed_time += time.time() - st.session_state.start_time
    st.session_state.running = False
    save_work_session("Stopped")
    st.session_state.start_time = None
    st.session_state.elapsed_time = 0

# Streamlit UI
st.title("⏳Time Tracker")

# Display elapsed time dynamically
if st.session_state.running:
    elapsed = time.time() - st.session_state.start_time + st.session_state.elapsed_time
else:
    elapsed = st.session_state.elapsed_time

st.subheader(f"Elapsed Time: {round(elapsed / 60, 2)} minutes")

col1, col2, col3, col4 = st.columns(4)

# Buttons
with col1:
    if st.button("Start", use_container_width=True):
        start_timer()
with col2:
    if st.button("Pause", use_container_width=True):
        pause_timer()
with col3:
    if st.button("Resume", use_container_width=True):
        start_timer()
with col4:
    if st.button("Stop", use_container_width=True):
        stop_timer()