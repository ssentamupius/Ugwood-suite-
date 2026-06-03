import streamlit as st
import subprocess
import os
import requests
import pandas as pd
import uuid
import base64
from datetime import datetime

# 1. PAGE INITIALIZATION & CONFIGURATION
st.set_page_config(page_title="Ugawood Post-Prod Master", page_icon="🎬", layout="wide")
st.title("🎬 Ugawood Production Suite Pro: Master Edition")
st.write("The ultimate all-in-one automation pipeline tailored for the Ugandan cinema ecosystem.")

# Initialize session state variables
if "user_token" not in st.session_state:
    st.session_state.user_token = str(uuid.uuid4())[:8]

# 2. SIDEBAR SETTINGS
st.sidebar.header("⚙️ Global Production Settings")
watermark_text = st.sidebar.text_input("Watermark / UFCB Rating Text", "PROPERTY OF UGAWOOD PROD - 16+")
video_quality = st.sidebar.selectbox("Target Output Quality", ["High-Quality Proxy (540p)", "WhatsApp Ultra-Compressed (480p)"])

# WhatsApp Notification Panel
st.sidebar.markdown("---")
st.sidebar.header("📱 WhatsApp Editor Alerts")
enable_whatsapp = st.sidebar.checkbox("Enable Completion Alerts", value=False)
phone_number = st.sidebar.text_input("Editor Phone (e.g., +256700000000)", "+256")
api_apikey = st.sidebar.text_input("CallMeBot API Key", type="password")

# Google Drive Cloud Configuration Panel
st.sidebar.markdown("---")
st.sidebar.header("☁️ Cloud Drive Sync")
google_script_url = st.sidebar.text_input("Google Web App URL", type="password")

# 3. DIRECTORY & FILE NAMING RULES
USER_DIR = f"workspace_{st.session_state.user_token}"
os.makedirs(USER_DIR, exist_ok=True)

INPUT_FILE = os.path.join(USER_DIR, "temp_input.mp4")
VIDEO_OUT = os.path.join(USER_DIR, "master_video_out.mp4")
AUDIO_OUT = os.path.join(USER_DIR, "master_audio_out.mp3")
LOG_FILE = "production_history.csv"

# 4. UTILITY HELPER FUNCTIONS
def send_whatsapp_alert(phone, key, message):
    try:
        url = f"https://callmebot.com{phone}&text={requests.utils.quote(message)}&apikey={key}"
        response = requests.get(url, timeout=10)
        return response.status_code == 200
    except Exception:
        return False

def log_production_run(filename, task_type, detail):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_data = pd.DataFrame([{
        "Timestamp": timestamp,
        "Original File": filename,
        "Task Completed": task_type,
        "Details": detail,
        "Status": "SUCCESS",
        "User Session": st.session_state.user_token
    }])
    if not os.path.exists(LOG_FILE):
        new_data.to_csv(LOG_FILE, index=False)
    else:
        new_data.to_csv(LOG_FILE, mode='a', header=False, index=False)

def upload_to_google_drive(file_path, filename, mime_type, endpoint_url):
    try:
        with open(file_path, "rb") as f:
            encoded_string = base64.b64encode(f.read()).decode("utf-8")
        payload = {
            "filename": filename,
            "mimeType": mime_type,
            "base64Data": encoded_string
        }
        res = requests.post(endpoint_url, json=payload, timeout=120)
        if res.status_code == 200 and res.json().get("status") == "success":
            return res.json().get("url")
        return None
    except Exception:
        return None

# 5. IMPORT ENGINE SECTION
uploaded_file = st.file_uploader("📥 IMPORT: Drag and drop your raw film file (.mp4)", type=["mp4"])

if uploaded_file is not None:
    with open(INPUT_FILE, "wb") as f:
        f.write(uploaded_file.read())
    st.success(f"🎥 Raw film file successfully loaded onto workspace session ({st.session_state.user_token})!")

    st.subheader("🚀 Production Automation Tasks")
    st.info("Choose the specific pipeline action you want to run on your file.")

    # Create three balanced columns for phone web layout
    btn_col1, btn_col2, btn_col3 = st.columns(3)

    # BUTTON 1: AUDIO EXTRACTION ONLY
    with btn_col1:
        if st.button("🎵 Extract Audio Only"):
            if os.path.exists(AUDIO_OUT): os.remove(AUDIO_OUT)
            status_audio = st.empty()
            status_audio.text("⏳ Stripping audio tracks...")
            try:
                audio_command = ['ffmpeg', '-y', '-i', INPUT_FILE, '-vn', '-acodec', 'mp3', AUDIO_OUT]
                result = subprocess.run(audio_command, capture_output=True, text=True)
                if result.returncode != 0: raise Exception(result.stderr)
                status_audio.text("✅ Audio Track Extracted!")
                st.toast("🎵 Audio conversion complete!", icon="🎵")
                log_production_run(uploaded_file.name, "Audio Extraction", "Extracted MP3 track")
            except Exception as e:
                st.error(f"❌ Failed: {e}")

    # BUTTON 2: CINEMATIC COLOR BOOST ONLY
    with btn_col2:
        if st.button("🎨 Color Boost Only"):
            if os.path.exists(VIDEO_OUT): os.remove(VIDEO_OUT)
            status_color = st.empty()
            status_color.text("⏳ Boosting contrast & saturation...")
            try:
                color_command = [
                    'ffmpeg', '-y', '-i', INPUT_FIL
