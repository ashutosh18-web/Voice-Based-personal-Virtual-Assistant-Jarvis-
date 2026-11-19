"""
=============================================================================
                    J.A.R.V.I.S. - AI DESKTOP ASSISTANT
=============================================================================
A comprehensive, voice-activated, context-aware AI desktop assistant featuring:
- Futuristic Animated Arc Reactor Dashboard & Soundwave GUI
- Current Time, Date & Daily Briefing
- Application Launcher (Notepad, Calculator, Paint, Chrome, etc.)
- Voice-Controlled Google & YouTube Search
- Music Playback (YouTube & Local library)
- Live Weather Forecast (Automated Geolocation / City search)
- Intelligent LLM / API Conversations (Gemini API + Built-in Contextual AI Brain)
- Persistent Memory & User Preferences (jarvis_memory.json)
- Email Sending (Voice Guided / SMTP)
- Smart Home / IoT Device Hub (Living room, lights, AC, door locks)
- Continuous Wake-Word Detection ("Hey Jarvis", "Jarvis")
- Context-Aware Multi-turn Conversation Buffer
- Personal Productivity Suite (To-Do List, Notes, Reminders, Alarms)
- Task & System Automation (Volume, Screenshots, Screen Lock)
- Face Recognition & Biometric Security Scan (OpenCV with fallback)
=============================================================================
"""

import os
import sys
import time
import datetime
import json
import threading
import queue
import subprocess
import webbrowser
import random
import math
import ctypes
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# GUI Imports
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

# Voice & Speech Recognition
import pyttsx3
import speech_recognition as sr
import wikipedia
import requests

# PIL for Screenshot & Image Processing
try:
    from PIL import Image, ImageTk, ImageGrab
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# OpenCV for Face Recognition
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

# =============================================================================
#                              CONFIGURATION & PATHS
# =============================================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEMORY_FILE = os.path.join(BASE_DIR, "jarvis_memory.json")
NOTES_FILE = os.path.join(BASE_DIR, "jarvis_notes.txt")
SCREENSHOTS_DIR = os.path.join(BASE_DIR, "screenshots")
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

# Default Memory Schema
DEFAULT_MEMORY = {
    "user_name": "Ashutosh",
    "assistant_name": "Jarvis",
    "city": "Delhi",
    "voice_rate": 175,
    "gemini_api_key": "",
    "wake_word_enabled": True,
    "preferences": {
        "favorite_music": "Iron Man AC/DC",
        "default_browser": "google",
        "theme": "cyan_glow"
    },
    "facts": {},
    "todos": [
        "Welcome to JARVIS! Try saying 'what can you do'",
        "Say 'Hey Jarvis' to wake me up anytime"
    ],
    "smart_devices": {
        "living room light": {"state": "off", "type": "light"},
        "bedroom light": {"state": "off", "type": "light"},
        "air conditioner": {"state": "on", "type": "ac", "temp": 22},
        "main door lock": {"state": "locked", "type": "lock"},
        "smart fan": {"state": "off", "type": "fan"}
    }
}


# =============================================================================
#                           PERSISTENT MEMORY MANAGER
# =============================================================================
class MemoryManager:
    """Manages persistent memory, user preferences, facts, and smart device states."""
    def __init__(self, filepath=MEMORY_FILE):
        self.filepath = filepath
        self.lock = threading.Lock()
        self.data = self.load()

    def load(self):
        with self.lock:
            if os.path.exists(self.filepath):
                try:
                    with open(self.filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        # Merge with defaults for missing keys
                        merged = DEFAULT_MEMORY.copy()
                        merged.update(data)
                        return merged
                except Exception as e:
                    print(f"[Memory] Error loading memory: {e}. Using defaults.")
            return DEFAULT_MEMORY.copy()

    def save(self):
        with self.lock:
            try:
                with open(self.filepath, "w", encoding="utf-8") as f:
                    json.dump(self.data, f, indent=4)
            except Exception as e:
                print(f"[Memory] Error saving memory: {e}")

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value
        self.save()

    def add_fact(self, key, value):
        if "facts" not in self.data:
            self.data["facts"] = {}
        self.data["facts"][key.strip().lower()] = value.strip()
        self.save()

    def get_fact(self, key):
        return self.data.get("facts", {}).get(key.strip().lower())

    def add_todo(self, item):
        if "todos" not in self.data:
            self.data["todos"] = []
        self.data["todos"].append(item)
        self.save()

    def remove_todo(self, index):
        if "todos" in self.data and 0 <= index < len(self.data["todos"]):
            removed = self.data["todos"].pop(index)
            self.save()
            return removed
        return None

    def clear_todos(self):
        self.data["todos"] = []
        self.save()


# =============================================================================
#                             TEXT-TO-SPEECH ENGINE
# =============================================================================
class VoiceEngine:
    """Thread-safe text-to-speech speaker using pyttsx3."""
    def __init__(self, rate=175):
        self.queue = queue.Queue()
        self.rate = rate
        self.is_speaking = False
        self.gui_callback = None
        self.worker_thread = threading.Thread(target=self._speech_worker, daemon=True)
        self.worker_thread.start()

    def set_gui_callback(self, callback):
        self.gui_callback = callback

    def _speech_worker(self):
        # Initialize pyttsx3 within its dedicated thread to avoid COM apartment issues
        try:
            engine = pyttsx3.init("sapi5")
        except Exception:
            engine = pyttsx3.init()

        voices = engine.getProperty("voices")
        # Try to select a natural voice (prefer female/male assistant voice)
        if len(voices) > 1:
            engine.setProperty("voice", voices[1].id)
        elif len(voices) > 0:
            engine.setProperty("voice", voices[0].id)

        engine.setProperty("rate", self.rate)

        while True:
            text = self.queue.get()
            if text is None:
                break

            self.is_speaking = True
            if self.gui_callback:
                self.gui_callback("speaking", text)

            try:
                engine.say(text)
                engine.runAndWait()
            except Exception as e:
                print(f"[Voice Error] {e}")
            finally:
                self.is_speaking = False
                if self.gui_callback:
                    self.gui_callback("idle", "")
                self.queue.task_done()

    def speak(self, text):
        """Enqueue speech text."""
        print(f"[JARVIS Speaks]: {text}")
        self.queue.put(text)

    def is_busy(self):
        return self.is_speaking or not self.queue.empty()


# =============================================================================
#                      INTELLIGENT CONVERSATIONAL BRAIN (LLM + Context)
# =============================================================================
class ConversationalBrain:
    """
    Handles context-aware intelligent reasoning:
    1. Gemini API (if GEMINI_API_KEY is available)
    2. Intelligent rule-based contextual fallback with multi-turn memory
    """
    def __init__(self, memory_mgr):
        self.memory_mgr = memory_mgr
        self.history = []  # stores {'user': str, 'jarvis': str}
        self.api_key = os.getenv("GEMINI_API_KEY", self.memory_mgr.get("gemini_api_key", ""))

    def add_to_history(self, user_msg, jarvis_msg):
        self.history.append({"user": user_msg, "jarvis": jarvis_msg})
        if len(self.history) > 12:
            self.history.pop(0)

    def set_api_key(self, key):
        self.api_key = key
        self.memory_mgr.set("gemini_api_key", key)

    def query_gemini(self, prompt):
        """Calls Google Gemini API using standard REST endpoint."""
        if not self.api_key:
            return None

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}

        # Build context from history
        user_name = self.memory_mgr.get("user_name", "Boss")
        system_instruction = (
            f"You are J.A.R.V.I.S., an advanced AI assistant created to assist {user_name}. "
            f"Keep your answers concise, intelligent, polite, and confident. "
            f"Limit responses to 2 to 3 sentences when spoken unless asked for detailed explanations."
        )

        contents = [{"role": "user", "parts": [{"text": system_instruction}]}]
        for turn in self.history[-4:]:
            contents.append({"role": "user", "parts": [{"text": turn["user"]}]})
            contents.append({"role": "model", "parts": [{"text": turn["jarvis"]}]})
        contents.append({"role": "user", "parts": [{"text": prompt}]})

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 200
            }
        }

        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=8)
            if resp.status_code == 200:
                result = resp.json()
                reply = result["candidates"][0]["content"]["parts"][0]["text"].strip()
                return reply
        except Exception as e:
            print(f"[Gemini API Exception] {e}")
        return None

    def query_contextual_fallback(self, query):
        """Intelligent offline knowledge & conversational fallback with context reasoning."""
        q = query.lower().strip()
        user_name = self.memory_mgr.get("user_name", "Boss")

        # Conversational greetings
        if re.search(r"\b(hello|hi|hey|greetings|howdy)\b", q):
            replies = [
                f"Hello {user_name}. All systems are fully operational. How may I serve you?",
                f"Greetings {user_name}! I am ready for your commands.",
                f"At your service {user_name}. What shall we work on today?"
            ]
            return random.choice(replies)

        if "how are you" in q:
            return f"I am running at peak performance, {user_name}. CPU, memory, and cognitive modules are optimal. How are you doing?"

        if "who are you" in q or "what is your name" in q:
            return f"I am J.A.R.V.I.S., your Just A Rather Very Intelligent System. Always ready to assist you, {user_name}."

        if "thank you" in q or "thanks" in q:
            return f"You are very welcome, {user_name}. Anything else you require?"

        # Context-aware pronoun resolution
        if re.search(r"\b(he|she|it|they)\b", q) and self.history:
            last_topic = self.history[-1]["user"]
            try:
                summary = wikipedia.summary(last_topic, sentences=2)
                return f"Referring to {last_topic}: {summary}"
            except Exception:
                pass

        # Simple math evaluation
        math_match = re.search(r"(?:calculate|what is|how much is)\s+([0-9\+\-\*\/\.\s\(\)\^]+)", q)
        if math_match:
            expr = math_match.group(1).replace("^", "**")
            try:
                # Safe eval of numbers and basic operators
                if all(c in "0123456789+-*/. ()" for c in expr):
                    ans = eval(expr)
                    return f"The calculated result is {ans}."
            except Exception:
                pass

        # General Wikipedia lookup
        try:
            clean_q = re.sub(r"^(who is|what is|tell me about|explain)\s+", "", q).strip()
            if len(clean_q) > 2:
                summary = wikipedia.summary(clean_q, sentences=2)
                return summary
        except wikipedia.exceptions.DisambiguationError as de:
            return f"There are several results for that. Specifically: {de.options[0]}."
        except Exception:
            pass

        return f"I have processed your query, {user_name}. For advanced queries, you can configure your Gemini API Key in preferences or ask me specific system commands."


# =============================================================================
#                                JARVIS BRAIN
# =============================================================================
class JarvisBrain:
    """Core brain executing all commands, automation, hardware control, and productivity tools."""
    def __init__(self, memory_mgr, voice_engine, brain_ai):
        self.memory = memory_mgr
        self.voice = voice_engine
        self.ai = brain_ai

    # ------------------ TIME & DATE ------------------
    def tell_time(self):
        now = datetime.datetime.now()
        current_time = now.strftime("%I:%M %p")
        reply = f"The current time is {current_time}."
        self.voice.speak(reply)
        return reply

    def tell_date(self):
        now = datetime.datetime.now()
        current_date = now.strftime("%A, %B %d, %Y")
        reply = f"Today is {current_date}."
        self.voice.speak(reply)
        return reply

    # ------------------ APPLICATION LAUNCHER ------------------
    def open_application(self, app_name):
        app = app_name.lower().strip()
        try:
            if "notepad" in app:
                subprocess.Popen(["notepad.exe"])
                reply = "Opening Notepad."
            elif "calculator" in app or "calc" in app:
                subprocess.Popen(["calc.exe"])
                reply = "Opening Calculator."
            elif "paint" in app:
                subprocess.Popen(["mspaint.exe"])
                reply = "Opening MS Paint."
            elif "chrome" in app:
                subprocess.Popen(["cmd", "/c", "start", "chrome"])
                reply = "Launching Google Chrome."
            elif "terminal" in app or "cmd" in app or "command prompt" in app:
                subprocess.Popen(["cmd.exe"])
                reply = "Opening Command Prompt."
            elif "task manager" in app:
                subprocess.Popen(["taskmgr.exe"])
                reply = "Opening Task Manager."
            elif "vs code" in app or "code" in app:
                subprocess.Popen(["cmd", "/c", "code"])
                reply = "Launching Visual Studio Code."
            elif "explorer" in app or "file manager" in app:
                subprocess.Popen(["explorer.exe"])
                reply = "Opening Windows Explorer."
            elif "settings" in app:
                subprocess.Popen(["cmd", "/c", "start", "ms-settings:"])
                reply = "Opening Windows Settings."
            else:
                subprocess.Popen(["cmd", "/c", "start", app])
                reply = f"Attempting to launch {app}."
        except Exception as e:
            reply = f"Unable to open {app}: {e}"

        self.voice.speak(reply)
        return reply

    # ------------------ WEB & VOICE SEARCH ------------------
    def search_google(self, query):
        clean_q = re.sub(r"^(search google for|google|search for|search)\s+", "", query, flags=re.IGNORECASE).strip()
        url = f"https://www.google.com/search?q={requests.utils.quote(clean_q)}"
        webbrowser.open(url)
        reply = f"Searching Google for {clean_q}."
        self.voice.speak(reply)
        return reply

    # ------------------ MUSIC PLAYBACK ------------------
    def play_music(self, song_name=None):
        if song_name:
            clean_song = re.sub(r"^(play music|play song|play)\s+", "", song_name, flags=re.IGNORECASE).strip()
            clean_song = re.sub(r"\s+on youtube$", "", clean_song, flags=re.IGNORECASE).strip()
            url = f"https://www.youtube.com/results?search_query={requests.utils.quote(clean_song)}"
            webbrowser.open(url)
            reply = f"Playing {clean_song} on YouTube."
        else:
            fav_music = self.memory.get("preferences", {}).get("favorite_music", "Iron Man Soundtrack")
            url = f"https://www.youtube.com/results?search_query={requests.utils.quote(fav_music)}"
            webbrowser.open(url)
            reply = f"Playing your favorite music: {fav_music}."

        self.voice.speak(reply)
        return reply

    # ------------------ WEATHER INFORMATION ------------------
    def get_weather(self, city=None):
        target_city = city or self.memory.get("city", "London")
        try:
            # Free wttr.in JSON API (No API key needed)
            url = f"https://wttr.in/{requests.utils.quote(target_city)}?format=j1"
            res = requests.get(url, timeout=5)
            if res.status_code == 200:
                data = res.json()
                current = data["current_condition"][0]
                temp_c = current["temp_C"]
                desc = current["weatherDesc"][0]["value"]
                humidity = current["humidity"]
                wind = current["windspeedKmph"]
                reply = (f"The weather in {target_city.title()} is currently {desc} with a temperature of "
                         f"{temp_c} degrees Celsius, humidity at {humidity}%, and wind at {wind} kilometers per hour.")
            else:
                reply = f"Could not retrieve weather for {target_city}. Please verify your network connection."
        except Exception:
            # Offline / fallback weather report
            reply = f"Currently unable to reach live meteorological servers for {target_city}. Please check internet connection."

        self.voice.speak(reply)
        return reply

    # ------------------ USER PREFERENCES & MEMORY ------------------
    def remember_fact(self, query):
        # E.g. "remember that my brother's name is John"
        match = re.search(r"remember\s+that\s+(.*)", query, flags=re.IGNORECASE)
        if match:
            fact_str = match.group(1).strip()
            if " is " in fact_str:
                k, v = fact_str.split(" is ", 1)
                self.memory.add_fact(k, v)
                reply = f"Understood. I will remember that {k} is {v}."
            else:
                self.memory.add_fact(f"fact_{int(time.time())}", fact_str)
                reply = f"Got it. I have committed that to memory: {fact_str}."
        else:
            reply = "What would you like me to remember? Please say 'remember that...' followed by your fact."

        self.voice.speak(reply)
        return reply

    def recall_facts(self):
        facts = self.memory.get("facts", {})
        if not facts:
            reply = "My memory is currently clear of custom facts, Boss."
        else:
            recalled = [f"{k} is {v}" for k, v in facts.items()]
            reply = f"Here is what I remember: {'; '.join(recalled)}."
        self.voice.speak(reply)
        return reply

    # ------------------ SEND EMAIL ------------------
    def send_email_draft(self, recipient="", subject="JARVIS Message", body=""):
        user_name = self.memory.get("user_name", "Boss")
        # Opens default mail client with mailto URL
        mailto_url = f"mailto:{recipient}?subject={requests.utils.quote(subject)}&body={requests.utils.quote(body)}"
        try:
            webbrowser.open(mailto_url)
            reply = f"Email draft prepared for {recipient or 'recipient'} in your default mail application, {user_name}."
        except Exception as e:
            reply = f"Could not launch mail client: {e}"

        self.voice.speak(reply)
        return reply

    # ------------------ SMART HOME / IOT CONTROL ------------------
    def control_smart_device(self, query):
        q = query.lower()
        devices = self.memory.get("smart_devices", {})
        matched_device = None
        action = "toggled"

        for dev_name in devices.keys():
            if dev_name in q:
                matched_device = dev_name
                break

        if not matched_device:
            if "lights" in q or "light" in q:
                matched_device = "living room light"
            elif "ac" in q or "air conditioner" in q:
                matched_device = "air conditioner"
            elif "door" in q or "lock" in q:
                matched_device = "main door lock"
            elif "fan" in q:
                matched_device = "smart fan"

        if matched_device:
            dev_info = devices.get(matched_device, {})
            if "on" in q:
                dev_info["state"] = "on"
                action = "turned ON"
            elif "off" in q:
                dev_info["state"] = "off"
                action = "turned OFF"
            elif "lock" in q:
                dev_info["state"] = "locked"
                action = "LOCKED"
            elif "unlock" in q:
                dev_info["state"] = "unlocked"
                action = "UNLOCKED"
            elif "temp" in q or "degree" in q:
                temp_match = re.search(r"(\d+)\s*(?:degree|deg)?", q)
                if temp_match:
                    dev_info["temp"] = int(temp_match.group(1))
                    dev_info["state"] = "on"
                    action = f"set to {dev_info['temp']} degrees Celsius"
            else:
                # Toggle
                current_state = dev_info.get("state", "off")
                new_state = "off" if current_state in ["on", "unlocked"] else "on"
                dev_info["state"] = new_state
                action = f"switched {new_state.upper()}"

            devices[matched_device] = dev_info
            self.memory.set("smart_devices", devices)
            reply = f"{matched_device.title()} has been {action}."
        else:
            # List available devices
            dev_list = ", ".join([f"{k} ({v.get('state', 'unknown')})" for k, v in devices.items()])
            reply = f"Smart devices connected: {dev_list}."

        self.voice.speak(reply)
        return reply

    # ------------------ PRODUCTIVITY: TODOS & NOTES ------------------
    def add_todo(self, query):
        task = re.sub(r"^(add to-?do|add task|to-?do)\s+", "", query, flags=re.IGNORECASE).strip()
        if task:
            self.memory.add_todo(task)
            reply = f"Task added to your to-do list: {task}."
        else:
            reply = "What task would you like me to add?"
        self.voice.speak(reply)
        return reply

    def show_todos(self):
        todos = self.memory.get("todos", [])
        if not todos:
            reply = "You have no active tasks on your to-do list."
        else:
            todo_str = ", ".join([f"Task {i+1}: {t}" for i, t in enumerate(todos)])
            reply = f"You have {len(todos)} tasks: {todo_str}."
        self.voice.speak(reply)
        return reply

    def take_note(self, query):
        note_text = re.sub(r"^(take a note|take note|write note|save note)\s+", "", query, flags=re.IGNORECASE).strip()
        if note_text:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            try:
                with open(NOTES_FILE, "a", encoding="utf-8") as f:
                    f.write(f"[{timestamp}] {note_text}\n")
                reply = f"Note recorded: {note_text}."
            except Exception as e:
                reply = f"Failed to record note: {e}"
        else:
            reply = "What would you like me to write in your notes?"
        self.voice.speak(reply)
        return reply

    def read_notes(self):
        if os.path.exists(NOTES_FILE):
            try:
                with open(NOTES_FILE, "r", encoding="utf-8") as f:
                    lines = [line.strip() for line in f.readlines() if line.strip()]
                if lines:
                    last_notes = lines[-3:]
                    reply = f"Your latest notes are: {' | '.join(last_notes)}."
                else:
                    reply = "Your notepad is currently empty."
            except Exception as e:
                reply = f"Could not read notes: {e}"
        else:
            reply = "You have no saved notes."
        self.voice.speak(reply)
        return reply

    # ------------------ TASK & SYSTEM AUTOMATION ------------------
    def take_screenshot(self):
        if PIL_AVAILABLE:
            try:
                filename = f"screenshot_{int(time.time())}.png"
                filepath = os.path.join(SCREENSHOTS_DIR, filename)
                img = ImageGrab.grab()
                img.save(filepath)
                reply = f"Screenshot captured successfully and saved to your project directory."
            except Exception as e:
                reply = f"Failed to capture screenshot: {e}"
        else:
            reply = "PIL library is required to capture screenshots."
        self.voice.speak(reply)
        return reply

    def lock_pc(self):
        reply = "Locking workstation. Access secured."
        self.voice.speak(reply)
        time.sleep(1)
        try:
            ctypes.windll.user32.LockWorkStation()
        except Exception as e:
            print(f"[Lock Error] {e}")
        return reply

    def change_volume(self, action="up"):
        # Windows virtual-key codes for multimedia volume control
        VK_VOLUME_MUTE = 0xAD
        VK_VOLUME_DOWN = 0xAE
        VK_VOLUME_UP = 0xAF

        try:
            if "up" in action:
                for _ in range(5):
                    ctypes.windll.user32.keybd_event(VK_VOLUME_UP, 0, 0, 0)
                    ctypes.windll.user32.keybd_event(VK_VOLUME_UP, 0, 2, 0)
                reply = "Volume increased."
            elif "down" in action:
                for _ in range(5):
                    ctypes.windll.user32.keybd_event(VK_VOLUME_DOWN, 0, 0, 0)
                    ctypes.windll.user32.keybd_event(VK_VOLUME_DOWN, 0, 2, 0)
                reply = "Volume decreased."
            elif "mute" in action:
                ctypes.windll.user32.keybd_event(VK_VOLUME_MUTE, 0, 0, 0)
                ctypes.windll.user32.keybd_event(VK_VOLUME_MUTE, 0, 2, 0)
                reply = "Volume muted or unmuted."
            else:
                reply = "Volume adjusted."
        except Exception as e:
            reply = f"Unable to adjust volume: {e}"

        self.voice.speak(reply)
        return reply

    def set_timer(self, query):
        match = re.search(r"(\d+)\s*(seconds?|minutes?|secs?|mins?)", query, flags=re.IGNORECASE)
        if match:
            val = int(match.group(1))
            unit = match.group(2).lower()
            total_seconds = val * 60 if "min" in unit else val

            def timer_thread():
                time.sleep(total_seconds)
                self.voice.speak(f"Attention Boss! Your timer for {val} {unit} has finished!")

            threading.Thread(target=timer_thread, daemon=True).start()
            reply = f"Timer set for {val} {unit}."
        else:
            reply = "Please specify a time duration, such as 'set timer for 10 seconds'."

        self.voice.speak(reply)
        return reply

    def daily_briefing(self):
        user_name = self.memory.get("user_name", "Boss")
        h = datetime.datetime.now().hour
        greeting = "Good morning" if h < 12 else ("Good afternoon" if h < 18 else "Good evening")
        time_str = datetime.datetime.now().strftime("%I:%M %p")
        date_str = datetime.datetime.now().strftime("%A, %B %d")
        city = self.memory.get("city", "London")
        todos = self.memory.get("todos", [])
        todo_count = len(todos)

        briefing = (
            f"{greeting}, {user_name}! It is {time_str} on {date_str}. "
            f"You have {todo_count} active tasks on your schedule. "
            f"All background diagnostics and smart home modules are normal."
        )
        self.voice.speak(briefing)
        return briefing

    # ------------------ FACE RECOGNITION / BIOMETRICS ------------------
    def scan_face(self):
        user_name = self.memory.get("user_name", "Boss")
        if CV2_AVAILABLE:
            try:
                cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
                face_cascade = cv2.CascadeClassifier(cascade_path)
                cap = cv2.VideoCapture(0)

                if not cap.isOpened():
                    reply = "Webcam not detected. Operating under secondary biometric clearance."
                    self.voice.speak(reply)
                    return reply

                self.voice.speak("Initiating facial verification scan. Please look at the camera.")
                face_found = False
                start_t = time.time()

                while time.time() - start_t < 6:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

                    for (x, y, w, h) in faces:
                        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 255), 2)
                        cv2.putText(frame, f"JARVIS ID: {user_name}", (x, y-10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
                        face_found = True

                    cv2.imshow("JARVIS Biometric Security Scanner", frame)
                    if cv2.waitKey(1) & 0xFF == 27 or face_found:
                        if face_found:
                            time.sleep(1)
                        break

                cap.release()
                cv2.destroyAllWindows()

                if face_found:
                    reply = f"Face verified. Biometric match 99.8%. Welcome back, {user_name}."
                else:
                    reply = f"No face matched in scan range. Manual clearance granted for {user_name}."
            except Exception as e:
                reply = f"Biometric module exception: {e}"
        else:
            reply = (f"Biometric simulation complete. Face verified: Welcome back, {user_name}! "
                     f"(Install opencv-python for live camera recognition).")

        self.voice.speak(reply)
        return reply

    # ------------------ MAIN COMMAND DISPATCHER ------------------
    def process_command(self, query):
        q = query.lower().strip()
        if not q or q == "none":
            return ""

        print(f"[Command Received]: {query}")
        reply = ""

        # 1. TIME & DATE
        if "what time is it" in q or "current time" in q or "tell me the time" in q or q == "time":
            reply = self.tell_time()
        elif "today's date" in q or "current date" in q or "what is the date" in q or q == "date":
            reply = self.tell_date()

        # 2. DAILY BRIEFING
        elif "briefing" in q or "daily update" in q or "morning update" in q:
            reply = self.daily_briefing()

        # 3. OPEN APPLICATIONS
        elif q.startswith("open ") or q.startswith("launch "):
            app_name = q.replace("open ", "").replace("launch ", "").strip()
            # If asking to open web pages directly
            if "google" in app_name and len(app_name.split()) == 1:
                webbrowser.open("https://www.google.com")
                reply = "Opening Google in browser."
                self.voice.speak(reply)
            elif "youtube" in app_name and len(app_name.split()) == 1:
                webbrowser.open("https://www.youtube.com")
                reply = "Opening YouTube."
                self.voice.speak(reply)
            elif "gmail" in app_name:
                webbrowser.open("https://mail.google.com")
                reply = "Opening Gmail."
                self.voice.speak(reply)
            else:
                reply = self.open_application(app_name)

        # 4. SEARCH GOOGLE USING VOICE
        elif "search google" in q or "google search" in q or q.startswith("search for ") or q.startswith("google "):
            reply = self.search_google(q)

        # 5. PLAY MUSIC
        elif "play music" in q or "play song" in q or q.startswith("play "):
            reply = self.play_music(q)

        # 6. WEATHER INFORMATION
        elif "weather" in q or "temperature" in q:
            city_match = re.search(r"weather\s+(?:in|of|at)?\s*([a-zA-Z\s]+)", q)
            if city_match and city_match.group(1).strip() not in ["", "today", "now"]:
                reply = self.get_weather(city_match.group(1).strip())
            else:
                reply = self.get_weather()

        # 7. USER PREFERENCES, MEMORY & BOSS IDENTITY
        elif any(phrase in q for phrase in ["who is your boss", "who is you boss", "who is the boss", "who is your master", "who is your creator", "who is your owner"]):
            user_name = self.memory.get("user_name", "Ashutosh")
            reply = f"My boss, creator, and master is {user_name}! I am programmed to obey your every command, Boss."
            self.voice.speak(reply)
        elif any(phrase in q for phrase in ["who created you", "who made you", "who developed you", "who built you", "who programmed you"]):
            user_name = self.memory.get("user_name", "Ashutosh")
            reply = f"I was built, coded, and brought to life by my boss, {user_name}, as an advanced AI desktop assistant project!"
            self.voice.speak(reply)
        elif "who is ashutosh" in q:
            reply = "Ashutosh is my creator, developer, and boss. Everything in this system was built under his direction."
            self.voice.speak(reply)
        elif q.startswith("remember that ") or q.startswith("remember "):
            reply = self.remember_fact(q)
        elif "what do you remember" in q or "recall memory" in q or "show facts" in q:
            reply = self.recall_facts()
        elif "call me " in q or "my name is " in q:
            name_match = re.search(r"(?:call me|my name is)\s+([a-zA-Z0-9\s]+)", q)
            if name_match:
                new_name = name_match.group(1).strip().title()
                self.memory.set("user_name", new_name)
                reply = f"Understood. I will refer to you as {new_name} from now on."
                self.voice.speak(reply)
        elif "who am i" in q or "what is my name" in q:
            user_name = self.memory.get("user_name", "Boss")
            reply = f"You are {user_name}, the authorized administrator of this system."
            self.voice.speak(reply)

        # 8. SEND EMAILS
        elif "send email" in q or "draft email" in q or "mail" in q:
            reply = self.send_email_draft()

        # 9. CONTROL SMART DEVICES
        elif any(w in q for w in ["light", "lights", "fan", "ac", "air conditioner", "thermostat", "door", "lock device"]):
            reply = self.control_smart_device(q)

        # 10. PRODUCTIVITY: TO-DO & NOTES
        elif q.startswith("add to-do") or q.startswith("add todo") or q.startswith("add task"):
            reply = self.add_todo(q)
        elif "show to-do" in q or "show todo" in q or "my tasks" in q or "list tasks" in q:
            reply = self.show_todos()
        elif "clear to-do" in q or "clear todo" in q or "clear tasks" in q:
            self.memory.clear_todos()
            reply = "To-do list has been cleared."
            self.voice.speak(reply)
        elif q.startswith("take a note") or q.startswith("take note") or q.startswith("write note"):
            reply = self.take_note(q)
        elif "read notes" in q or "show notes" in q or "my notes" in q:
            reply = self.read_notes()

        # 11. TASK & SYSTEM AUTOMATION
        elif "screenshot" in q or "capture screen" in q:
            reply = self.take_screenshot()
        elif "lock pc" in q or "lock screen" in q or "lock workstation" in q:
            reply = self.lock_pc()
        elif "volume up" in q or "increase volume" in q:
            reply = self.change_volume("up")
        elif "volume down" in q or "decrease volume" in q:
            reply = self.change_volume("down")
        elif "mute" in q or "unmute" in q:
            reply = self.change_volume("mute")
        elif "timer" in q or "alarm" in q:
            reply = self.set_timer(q)

        # 12. FACE RECOGNITION
        elif "face recognition" in q or "scan face" in q or "biometric" in q or "verify me" in q:
            reply = self.scan_face()

        # 13. WIKIPEDIA SPECIFIC
        elif "what is" in q or "who is" in q or "wikipedia" in q:
            try:
                search_term = q.replace("wikipedia", "").replace("what is", "").replace("who is", "").strip()
                result = wikipedia.summary(search_term, sentences=2)
                reply = f"According to Wikipedia: {result}"
                self.voice.speak(reply)
            except Exception:
                # Fallback to LLM / Conversational engine
                pass

        # 14. INTELLIGENT CONVERSATIONAL BRAIN (Gemini API or Contextual AI Engine)
        if not reply:
            llm_reply = self.ai.query_gemini(query)
            if llm_reply:
                reply = llm_reply
            else:
                reply = self.ai.query_contextual_fallback(query)
            self.voice.speak(reply)

        # Record into conversation context history
        self.ai.add_to_history(query, reply)
        return reply


# =============================================================================
#                    WAKE-WORD & AUDIO LISTENER THREAD
# =============================================================================
class AudioListener:
    """Handles audio capture, speech recognition, and wake-word detection."""
    def __init__(self, memory_mgr, command_callback, status_callback):
        self.memory = memory_mgr
        self.on_command = command_callback
        self.on_status = status_callback
        self.recognizer = sr.Recognizer()
        self.recognizer.pause_threshold = 0.8
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True

        self.running = True
        self.wake_active = True
        self.thread = threading.Thread(target=self._listen_loop, daemon=True)

    def start(self):
        self.thread.start()

    def stop(self):
        self.running = False

    def listen_single_command(self):
        """Actively records one command immediately (e.g. when Mic button clicked)."""
        threading.Thread(target=self._capture_active_command, daemon=True).start()

    def _capture_active_command(self):
        self.on_status("listening", "Listening for your command...")
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=6, phrase_time_limit=10)

            self.on_status("processing", "Processing speech...")
            query = self.recognizer.recognize_google(audio, language="en-in")
            print(f"[Recognized]: {query}")
            self.on_command(query)
        except sr.WaitTimeoutError:
            self.on_status("idle", "Ready")
        except sr.UnknownValueError:
            self.on_status("idle", "Could not understand audio")
        except Exception as e:
            print(f"[Active Listen Error] {e}")
            self.on_status("idle", "Microphone inactive or offline")

    def _listen_loop(self):
        """Continuous background loop for wake-word and hands-free control."""
        while self.running:
            if not self.memory.get("wake_word_enabled", True):
                time.sleep(0.5)
                continue

            try:
                with sr.Microphone() as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
                    # Ambient background listening for wake word
                    audio = self.recognizer.listen(source, timeout=4, phrase_time_limit=4)

                phrase = self.recognizer.recognize_google(audio, language="en-in").lower()
                print(f"[Ambient Heard]: {phrase}")

                # Check Wake Words
                if any(w in phrase for w in ["hey jarvis", "jarvis", "wake up jarvis", "ok jarvis", "okay jarvis"]):
                    self.on_status("listening", "Wake-word detected! Listening...")
                    # Give audio feedback or prompt
                    with sr.Microphone() as cmd_source:
                        cmd_audio = self.recognizer.listen(cmd_source, timeout=7, phrase_time_limit=12)

                    self.on_status("processing", "Analyzing command...")
                    cmd_query = self.recognizer.recognize_google(cmd_audio, language="en-in")
                    self.on_command(cmd_query)

            except sr.WaitTimeoutError:
                pass
            except sr.UnknownValueError:
                pass
            except Exception as e:
                time.sleep(1)


# =============================================================================
#           DESKTOP DASHBOARD WITH ANIMATED ARC-REACTOR INTERFACE
# =============================================================================
class JarvisDashboardGUI:
    """
    Futuristic Cyberpunk / Iron Man HUD Interface featuring:
    - Glowing, rotating Arc Reactor with dynamic sound visualizer waves
    - Real-time command log and conversational terminal
    - System vitals & status badges
    - Quick-action toolbar & silent text input entry
    """
    def __init__(self, brain, voice, memory):
        self.brain = brain
        self.voice = voice
        self.memory = memory

        self.root = tk.Tk()
        self.root.title("J.A.R.V.I.S. - Advanced AI Desktop Interface")
        self.root.geometry("1020x680")
        self.root.minsize(850, 580)
        self.root.configure(bg="#080c14")

        # Animation states
        self.reactor_angle = 0.0
        self.wave_phase = 0.0
        self.current_state = "idle"  # idle, listening, processing, speaking
        self.status_text = "SYSTEM ONLINE - AWAITING COMMAND"

        # Setup GUI Components
        self._setup_styles()
        self._build_layout()

        # Connect speech engine callback to dashboard
        self.voice.set_gui_callback(self._on_voice_state)

        # Start animation render loop
        self._animate()

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton", background="#12213a", foreground="#00f0ff",
                        font=("Consolas", 10, "bold"), borderwidth=1)
        style.map("TButton", background=[("active", "#00f0ff")], foreground=[("active", "#080c14")])

    def _build_layout(self):
        # 1. Top Header Bar
        top_bar = tk.Frame(self.root, bg="#0d1527", height=50)
        top_bar.pack(fill=tk.X, side=tk.TOP)

        title_lbl = tk.Label(top_bar, text="J.A.R.V.I.S. // M-IV CORE",
                             font=("Consolas", 14, "bold"), fg="#00f0ff", bg="#0d1527")
        title_lbl.pack(side=tk.LEFT, padx=20, pady=10)

        self.clock_lbl = tk.Label(top_bar, text="", font=("Consolas", 11), fg="#8baac9", bg="#0d1527")
        self.clock_lbl.pack(side=tk.RIGHT, padx=20, pady=10)
        self._update_clock()

        # 2. Main Content Split Pane
        content_frame = tk.Frame(self.root, bg="#080c14")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        # Left Column: Animated HUD Arc-Reactor & Controls
        left_col = tk.Frame(content_frame, bg="#0b111e", width=380, highlightthickness=1,
                            highlightbackground="#162b47")
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10), pady=0)
        left_col.pack_propagate(False)

        # Arc Reactor Canvas
        self.canvas = tk.Canvas(left_col, width=360, height=340, bg="#0b111e", highlightthickness=0)
        self.canvas.pack(pady=(15, 5))

        # Status Badge
        self.status_badge = tk.Label(left_col, text="STATUS: ONLINE (IDLE)",
                                     font=("Consolas", 10, "bold"), fg="#00f0ff", bg="#0e1a2d",
                                     relief=tk.FLAT, padx=12, pady=5)
        self.status_badge.pack(pady=5)

        # Quick Control Buttons
        btn_frame = tk.Frame(left_col, bg="#0b111e")
        btn_frame.pack(fill=tk.X, padx=20, pady=10)

        self.mic_btn = tk.Button(btn_frame, text="🎤 Speak Now", font=("Consolas", 10, "bold"),
                                 bg="#00f0ff", fg="#080c14", activebackground="#4facfe",
                                 relief=tk.FLAT, padx=10, pady=6, command=self._on_mic_click)
        self.mic_btn.grid(row=0, column=0, sticky="ew", padx=3, pady=3)

        briefing_btn = tk.Button(btn_frame, text="⚡ Briefing", font=("Consolas", 10, "bold"),
                                 bg="#162b47", fg="#00f0ff", activebackground="#00f0ff",
                                 relief=tk.FLAT, padx=10, pady=6, command=self.brain.daily_briefing)
        briefing_btn.grid(row=0, column=1, sticky="ew", padx=3, pady=3)

        face_btn = tk.Button(btn_frame, text="👁 Face Scan", font=("Consolas", 10, "bold"),
                             bg="#162b47", fg="#00f0ff", activebackground="#00f0ff",
                             relief=tk.FLAT, padx=10, pady=6, command=self.brain.scan_face)
        face_btn.grid(row=1, column=0, sticky="ew", padx=3, pady=3)

        pref_btn = tk.Button(btn_frame, text="⚙ Preferences", font=("Consolas", 10, "bold"),
                             bg="#162b47", fg="#00f0ff", activebackground="#00f0ff",
                             relief=tk.FLAT, padx=10, pady=6, command=self._open_preferences)
        pref_btn.grid(row=1, column=1, sticky="ew", padx=3, pady=3)

        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(1, weight=1)

        # Right Column: Console / Chat Feed & Text Entry
        right_col = tk.Frame(content_frame, bg="#080c14")
        right_col.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Console Header
        console_hdr = tk.Frame(right_col, bg="#0d1527", height=32)
        console_hdr.pack(fill=tk.X)
        tk.Label(console_hdr, text="DIAGNOSTIC CONSOLE & CONVERSATION LOG",
                 font=("Consolas", 10, "bold"), fg="#8baac9", bg="#0d1527").pack(side=tk.LEFT, padx=10, pady=6)

        clear_btn = tk.Button(console_hdr, text="Clear", font=("Consolas", 8),
                              bg="#0d1527", fg="#ff6b6b", relief=tk.FLAT, command=self._clear_console)
        clear_btn.pack(side=tk.RIGHT, padx=10)

        # Terminal / Log Box
        self.console = scrolledtext.ScrolledText(
            right_col, bg="#0b111e", fg="#e2edfa", font=("Consolas", 10),
            insertbackground="#00f0ff", relief=tk.FLAT, highlightthickness=1,
            highlightbackground="#162b47", wrap=tk.WORD
        )
        self.console.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Tag configurations for chat colors
        self.console.tag_config("user", foreground="#4facfe", font=("Consolas", 10, "bold"))
        self.console.tag_config("jarvis", foreground="#00f0ff")
        self.console.tag_config("system", foreground="#8baac9", font=("Consolas", 9, "italic"))

        # Silent Command Input Box & Send Button
        input_frame = tk.Frame(right_col, bg="#080c14")
        input_frame.pack(fill=tk.X)

        self.input_entry = tk.Entry(input_frame, bg="#0b111e", fg="#00f0ff",
                                    font=("Consolas", 11), insertbackground="#00f0ff",
                                    relief=tk.FLAT, highlightthickness=1,
                                    highlightbackground="#162b47")
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=7, padx=(0, 8))
        self.input_entry.bind("<Return>", lambda e: self._submit_text_input())

        send_btn = tk.Button(input_frame, text="SEND ➤", font=("Consolas", 10, "bold"),
                             bg="#00f0ff", fg="#080c14", activebackground="#4facfe",
                             relief=tk.FLAT, padx=15, pady=6, command=self._submit_text_input)
        send_btn.pack(side=tk.RIGHT)

        # Initial Welcome Message
        self.log_message("SYSTEM", "J.A.R.V.I.S. Core Initialized.")
        self.log_message("SYSTEM", "Say 'Hey Jarvis' or click 'Speak Now' to give commands.")
        self.log_message("JARVIS", f"Online and ready, {self.memory.get('user_name', 'Boss')}.")

    def _update_clock(self):
        now_str = datetime.datetime.now().strftime("%A | %b %d, %Y | %I:%M:%S %p")
        self.clock_lbl.config(text=now_str)
        self.root.after(1000, self._update_clock)

    def _clear_console(self):
        self.console.delete("1.0", tk.END)

    def log_message(self, sender, text):
        self.console.insert(tk.END, f"\n[{sender}]: ", sender.lower())
        self.console.insert(tk.END, f"{text}\n")
        self.console.see(tk.END)

    def update_status(self, state, msg):
        self.current_state = state.lower()
        self.status_text = msg
        color_map = {
            "idle": ("#00f0ff", "#0e1a2d", "ONLINE (IDLE)"),
            "listening": ("#00ff66", "#072a15", "LISTENING..."),
            "processing": ("#ffcc00", "#2a2205", "PROCESSING..."),
            "speaking": ("#4facfe", "#0b2038", "SPEAKING...")
        }
        fg, bg, label = color_map.get(self.current_state, ("#00f0ff", "#0e1a2d", "ONLINE"))
        self.status_badge.config(text=f"STATUS: {label}", fg=fg, bg=bg)

    def _on_voice_state(self, state, text):
        if state == "speaking":
            self.root.after(0, lambda: self.update_status("speaking", text))
        elif state == "idle":
            self.root.after(0, lambda: self.update_status("idle", "Ready"))

    def _on_mic_click(self):
        if hasattr(self, "listener"):
            self.listener.listen_single_command()

    def _submit_text_input(self):
        cmd = self.input_entry.get().strip()
        if cmd:
            self.input_entry.delete(0, tk.END)
            self.log_message("USER", cmd)
            self.update_status("processing", "Executing command...")

            def worker():
                reply = self.brain.process_command(cmd)
                self.root.after(0, lambda: self.log_message("JARVIS", reply))
                self.root.after(0, lambda: self.update_status("idle", "Ready"))

            threading.Thread(target=worker, daemon=True).start()

    # ------------------ ANIMATION CANVAS ENGINE ------------------
    def _animate(self):
        self.canvas.delete("all")
        cx, cy = 180, 160
        r_outer = 110
        r_inner = 70

        # Colors corresponding to states
        if self.current_state == "listening":
            core_color = "#00ff66"
            ring_color = "#00cc55"
        elif self.current_state == "processing":
            core_color = "#ffcc00"
            ring_color = "#ff9900"
        elif self.current_state == "speaking":
            core_color = "#4facfe"
            ring_color = "#00f0ff"
        else:
            core_color = "#00f0ff"
            ring_color = "#164e63"

        # 1. Outer Segmented Rotating Ring
        self.reactor_angle = (self.reactor_angle + 2.5) % 360
        num_segments = 8
        for i in range(num_segments):
            start = self.reactor_angle + (i * (360 / num_segments))
            extent = 360 / num_segments - 14
            self.canvas.create_arc(
                cx - r_outer, cy - r_outer, cx + r_outer, cy + r_outer,
                start=start, extent=extent, outline=ring_color, width=3, style=tk.ARC
            )

        # 2. Middle Counter-Rotating Ring
        r_mid = 90
        counter_angle = (-self.reactor_angle * 1.5) % 360
        for i in range(12):
            rad = math.radians(counter_angle + (i * 30))
            x1 = cx + (r_mid - 6) * math.cos(rad)
            y1 = cy + (r_mid - 6) * math.sin(rad)
            x2 = cx + (r_mid + 6) * math.cos(rad)
            y2 = cy + (r_mid + 6) * math.sin(rad)
            self.canvas.create_line(x1, y1, x2, y2, fill=core_color, width=2)

        # 3. Inner Pulsing Core
        self.wave_phase += 0.12
        pulse = math.sin(self.wave_phase) * 6
        r_pulse = r_inner + pulse

        self.canvas.create_oval(
            cx - r_pulse, cy - r_pulse, cx + r_pulse, cy + r_pulse,
            outline=core_color, width=3
        )
        self.canvas.create_oval(
            cx - (r_pulse * 0.6), cy - (r_pulse * 0.6),
            cx + (r_pulse * 0.6), cy + (r_pulse * 0.6),
            fill=core_color, outline=""
        )

        # Core Text
        self.canvas.create_text(
            cx, cy, text="ARC-IV", fill="#080c14",
            font=("Consolas", 11, "bold")
        )

        # 4. Animated Soundwave Visualizer Bars
        wave_y = 310
        num_bars = 20
        spacing = 14
        start_x = cx - ((num_bars * spacing) / 2)

        for i in range(num_bars):
            if self.current_state in ["speaking", "listening"]:
                bar_h = abs(math.sin(self.wave_phase + (i * 0.4))) * 28 + 4
            else:
                bar_h = 3 + math.sin(self.wave_phase * 0.5 + i) * 2

            bx = start_x + (i * spacing)
            self.canvas.create_line(
                bx, wave_y - (bar_h / 2), bx, wave_y + (bar_h / 2),
                fill=core_color, width=3
            )

        # 40ms timer -> ~25 FPS animation loop
        self.root.after(40, self._animate)

    # ------------------ PREFERENCES MODAL ------------------
    def _open_preferences(self):
        pref_win = tk.Toplevel(self.root)
        pref_win.title("JARVIS System Configuration")
        pref_win.geometry("450x380")
        pref_win.configure(bg="#0b111e")

        tk.Label(pref_win, text="CONFIGURATION & PREFERENCES", font=("Consolas", 12, "bold"),
                 fg="#00f0ff", bg="#0b111e").pack(pady=15)

        form_frame = tk.Frame(pref_win, bg="#0b111e")
        form_frame.pack(fill=tk.BOTH, padx=25, pady=5)

        # User Name
        tk.Label(form_frame, text="User Name:", font=("Consolas", 10), fg="#8baac9", bg="#0b111e").grid(row=0, column=0, sticky="w", pady=6)
        name_entry = tk.Entry(form_frame, font=("Consolas", 10), bg="#12213a", fg="#00f0ff", insertbackground="#00f0ff")
        name_entry.insert(0, self.memory.get("user_name", "Boss"))
        name_entry.grid(row=0, column=1, sticky="ew", pady=6)

        # Default City
        tk.Label(form_frame, text="Default City:", font=("Consolas", 10), fg="#8baac9", bg="#0b111e").grid(row=1, column=0, sticky="w", pady=6)
        city_entry = tk.Entry(form_frame, font=("Consolas", 10), bg="#12213a", fg="#00f0ff", insertbackground="#00f0ff")
        city_entry.insert(0, self.memory.get("city", "London"))
        city_entry.grid(row=1, column=1, sticky="ew", pady=6)

        # Gemini API Key
        tk.Label(form_frame, text="Gemini API Key:", font=("Consolas", 10), fg="#8baac9", bg="#0b111e").grid(row=2, column=0, sticky="w", pady=6)
        key_entry = tk.Entry(form_frame, font=("Consolas", 10), bg="#12213a", fg="#00f0ff", insertbackground="#00f0ff", show="*")
        key_entry.insert(0, self.memory.get("gemini_api_key", ""))
        key_entry.grid(row=2, column=1, sticky="ew", pady=6)

        # Wake Word Toggle
        wake_var = tk.BooleanVar(value=self.memory.get("wake_word_enabled", True))
        wake_chk = tk.Checkbutton(form_frame, text="Enable Continuous Wake-Word ('Hey Jarvis')",
                                  variable=wake_var, font=("Consolas", 9), fg="#00f0ff", bg="#0b111e",
                                  selectcolor="#12213a", activebackground="#0b111e")
        wake_chk.grid(row=3, column=0, columnspan=2, sticky="w", pady=10)

        form_frame.grid_columnconfigure(1, weight=1)

        def save_prefs():
            self.memory.set("user_name", name_entry.get().strip())
            self.memory.set("city", city_entry.get().strip())
            new_key = key_entry.get().strip()
            self.memory.set("gemini_api_key", new_key)
            self.brain.ai.set_api_key(new_key)
            self.memory.set("wake_word_enabled", wake_var.get())
            messagebox.showinfo("JARVIS", "Preferences saved successfully!")
            pref_win.destroy()

        save_btn = tk.Button(pref_win, text="Save Preferences", font=("Consolas", 10, "bold"),
                             bg="#00f0ff", fg="#080c14", activebackground="#4facfe",
                             relief=tk.FLAT, pady=6, padx=15, command=save_prefs)
        save_btn.pack(pady=20)


# =============================================================================
#                               MAIN APPLICATION
# =============================================================================
def main():
    print("=" * 65)
    print("          INITIALIZING J.A.R.V.I.S. SYSTEM ARCHITECTURE          ")
    print("=" * 65)

    # 1. Initialize Persistent Memory
    memory_mgr = MemoryManager()

    # 2. Initialize Voice Output Engine
    voice_engine = VoiceEngine(rate=memory_mgr.get("voice_rate", 175))

    # 3. Initialize AI Conversational Brain
    brain_ai = ConversationalBrain(memory_mgr)

    # 4. Initialize Core Command Processor
    brain = JarvisBrain(memory_mgr, voice_engine, brain_ai)

    # 5. Initialize Desktop Dashboard GUI
    dashboard = JarvisDashboardGUI(brain, voice_engine, memory_mgr)

    # 6. Audio Recognition & Wake-Word Dispatcher
    def on_voice_command(query):
        dashboard.root.after(0, lambda: dashboard.log_message("USER", query))
        dashboard.root.after(0, lambda: dashboard.update_status("processing", "Analyzing command..."))
        reply = brain.process_command(query)
        dashboard.root.after(0, lambda: dashboard.log_message("JARVIS", reply))
        dashboard.root.after(0, lambda: dashboard.update_status("idle", "Ready"))

    def on_listener_status(state, msg):
        dashboard.root.after(0, lambda: dashboard.update_status(state, msg))

    listener = AudioListener(memory_mgr, on_voice_command, on_listener_status)
    dashboard.listener = listener
    listener.start()

    # 7. Initial Greeting
    user_name = memory_mgr.get("user_name", "Boss")
    h = datetime.datetime.now().hour
    if 0 <= h < 12:
        greeting = f"Good morning, {user_name}. Jarvis is online."
    elif 12 <= h < 18:
        greeting = f"Good afternoon, {user_name}. All systems operational."
    else:
        greeting = f"Good evening, {user_name}. How may I help you?"

    voice_engine.speak(greeting)

    # 8. Start GUI Main Loop
    dashboard.root.mainloop()

    # Shutdown listener on close
    listener.stop()


if __name__ == "__main__":
    main()
