import os
import time
import speech_recognition as sr
from flask import Flask, jsonify, render_template, request
import google.generativeai as genai
import threading
import pyautogui

# Configure the Gemini API key
API_KEY = ""  # Replace with your actual Gemini API key
genai.configure(api_key=API_KEY)

app = Flask(__name__)

# Audio file path
AUDIO_FILE = 'recorded_audio.wav'

# Flags and transcript storage
recording_done = False
is_recording = False  # Flag to control audio recording
transcript_text = ""  # Will store the recognized text

# Function to simulate joining Google Meet and recording audio
def join_meet_and_record(link):
    pyautogui.hotkey('ctrl', 't')  # Open a new tab
    pyautogui.write(link)         # Write the Google Meet link
    pyautogui.press('enter')
    time.sleep(5)                 # Wait for the page to load
    # Simulate joining the meet
    pyautogui.click(x=500, y=500)   # Example: click "Join" button location (update with actual coords)
    # Start recording audio after joining the meet
    record_audio()

# Function to record audio
def record_audio():
    global is_recording, recording_done
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        print("Recording...")
        is_recording = True
        try:
            audio_data = recognizer.listen(source, timeout=60)
            with open(AUDIO_FILE, "wb") as file:
                file.write(audio_data.get_wav_data())
            print("Audio recorded.")
        except Exception as e:
            print("Error during recording:", e)
        finally:
            recording_done = True

# Endpoint to stop recording (called when the Meeting Ended button is pressed)
@app.route('/end_meeting', methods=['POST'])
def end_meeting():
    global is_recording
    is_recording = False  # This flag could be used to break out of a recording loop if you implement continuous recording
    return jsonify({"status": "stopped"})

# Function to convert speech to text
def audio_to_text():
    global transcript_text
    # Wait until recording is finished
    while not recording_done:
        time.sleep(1)
    if not os.path.exists(AUDIO_FILE):
        return "Audio file not found. Please try again later."
    recognizer = sr.Recognizer()
    with sr.AudioFile(AUDIO_FILE) as source:
        audio = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio)
            print("Text from audio:", text)
            transcript_text = text
            return text
        except sr.UnknownValueError:
            return "Could not understand audio"
        except sr.RequestError as e:
            return f"Error with the speech recognition service: {e}"

# Function to generate a summary using the Gemini API
def summarize_text(text):
    prompt = f"Summarize the following text: {text}"
    try:
        # Create a GenerativeModel instance with the appropriate model name.
        # The generate_content() method is used for generating completions.
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        summary = response.text.strip()
        print("Summary:", summary)
        return summary
    except Exception as e:
        print("Error generating summary:", e)
         return "Error with summarization."

# API endpoint to start the process (join meeting and start recording)
@app.route('/start_process', methods=['POST'])
def start_process():
    meet_link = "https://meet.google.com/kft-xkxa-rjs"  # Example link; replace with your actual link
    threading.Thread(target=join_meet_and_record, args=(meet_link,)).start()
    return jsonify({"status": "started"})

# API endpoint to get the transcript and summary
@app.route('/get_transcript_and_summary', methods=['GET'])
def get_transcript_and_summary():
    transcript = audio_to_text()
    # If the transcript indicates an error, do not attempt summarization.
    if transcript.startswith("Error") or transcript in ["Could not understand audio", "Audio file not found. Please try again later."]:
        summary = "Summary not generated due to transcript error."
    else:
        summary = summarize_text(transcript)
    return jsonify({"transcript": transcript, "summary": summary})

# Home route to serve the frontend
@app.route('/')
def home():
    return render_template('video.html')

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)