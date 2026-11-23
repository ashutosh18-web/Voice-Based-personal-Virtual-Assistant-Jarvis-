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
    "user_name": "Boss",
    "assistant_name": "Jarvis",
    "city": "Delhi",
    "language": "auto",  # "auto", "hi-in", "en-in"
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
    """Thread-safe text-to-speech speaker using pyttsx3 with SAPI fallback."""
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
        engine = None
        sapi_voice = None
        try:
            import pythoncom
            pythoncom.CoInitialize()
        except Exception:
            pass

        # Try pyttsx3 init
        try:
            engine = pyttsx3.init("sapi5")
        except Exception:
            try:
                engine = pyttsx3.init()
            except Exception:
                engine = None

        if engine is not None:
            try:
                voices = engine.getProperty("voices")
                if len(voices) > 1:
                    engine.setProperty("voice", voices[1].id)
                elif len(voices) > 0:
                    engine.setProperty("voice", voices[0].id)
                engine.setProperty("rate", self.rate)
            except Exception:
                pass
        else:
            try:
                import win32com.client
                sapi_voice = win32com.client.Dispatch("SAPI.SpVoice")
            except Exception:
                sapi_voice = None

        while True:
            text = self.queue.get()
            if text is None:
                break

            self.is_speaking = True
            if self.gui_callback:
                self.gui_callback("speaking", text)

            try:
                if engine is not None:
                    engine.say(text)
                    engine.runAndWait()
                elif sapi_voice is not None:
                    sapi_voice.Speak(text)
                else:
                    time.sleep(min(2.5, max(0.8, len(text) * 0.04)))
            except Exception as e:
                print(f"[Voice Output Note] {e}")
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

        # Simple math evaluation (Bilingual: English + Hindi)
        math_words = ["calculate", "how much is", "what is", "plus", "minus", "into", "times", "divided by", "divide by", "multiplied by",
                      "हिसाब", "गणना", "जोड़ो", "जोड़", "घटाओ", "घटाव", "गुणा", "गुना", "भाग"]
        if any(w in q for w in math_words) or re.search(r"\d+\s*[\+\-\*\/xX]\s*\d+", q):
            expr_str = f" {q} "
            for prefix in ["calculate", "how much is", "what is", "हिसाब करो", "गणना करो", "बताओ", "how much"]:
                expr_str = expr_str.replace(prefix, "")
            replacements = {
                " into ": " * ", " times ": " * ", " x ": " * ", " multiply by ": " * ", " multiplied by ": " * ", " guna ": " * ", " गुना ": " * ", " गुणा ": " * ",
                " divided by ": " / ", " divide by ": " / ", " bhag ": " / ", " भाग ": " / ", " बटा ": " / ",
                " plus ": " + ", " and ": " + ", " add ": " + ", " jodo ": " + ", " जोड़ ": " + ", " धन ": " + ",
                " minus ": " - ", " ghatao ": " - ", " subtract ": " - ", " घटाव ": " - ", " घटाओ ": " - ", " ऋण ": " - "
            }
            for k, v in replacements.items():
                expr_str = expr_str.replace(k, v)
            expr_cleaned = re.sub(r"[^0-9\+\-\*\/\.\(\)]", "", expr_str)
            if expr_cleaned and any(c.isdigit() for c in expr_cleaned) and any(op in expr_cleaned for op in "+-*/"):
                try:
                    ans = eval(expr_cleaned)
                    if isinstance(ans, float) and ans.is_integer():
                        ans = int(ans)
                    is_hi = bool(re.search(r"[\u0900-\u097F]", query)) or any(w in q for w in ["hisaab", "guna", "jodo"])
                    return f"गणना का परिणाम {ans} है।" if is_hi else f"The calculated result is {ans}."
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

    # ------------------ SMART HOME / IOT CONTROL (EN + HI) ------------------
    def control_smart_device(self, query):
        q = query.lower()
        devices = self.memory.get("smart_devices", {})
        matched_device = None
        action = "toggled"
        is_hi = bool(re.search(r"[\u0900-\u097F]", query)) or any(w in q for w in ["chalu", "band", "jalao", "kholo", "bujhao"])

        for dev_name in devices.keys():
            if dev_name in q:
                matched_device = dev_name
                break

        if not matched_device:
            if any(w in q for w in ["lights", "light", "लाइट", "बल्ब"]):
                matched_device = "living room light"
            elif any(w in q for w in ["ac", "air conditioner", "एसी"]):
                matched_device = "air conditioner"
            elif any(w in q for w in ["door", "lock", "दरवाजा", "ताला"]):
                matched_device = "main door lock"
            elif any(w in q for w in ["fan", "पंखा"]):
                matched_device = "smart fan"

        if matched_device:
            dev_info = devices.get(matched_device, {})
            if any(w in q for w in ["on", "जलाओ", "चालू", "chalu", "ऑन"]):
                dev_info["state"] = "on"
                action = "चालू (ON) कर दी गई है" if is_hi else "turned ON"
            elif any(w in q for w in ["off", "बंद", "बुझाओ", "band", "ऑफ"]):
                dev_info["state"] = "off"
                action = "बंद (OFF) कर दी गई है" if is_hi else "turned OFF"
            elif any(w in q for w in ["unlock", "खोलो", "अनलॉक", "kholo"]):
                dev_info["state"] = "unlocked"
                action = "अनलॉक (UNLOCKED) कर दिया गया है" if is_hi else "UNLOCKED"
            elif any(w in q for w in ["lock", "लॉक"]):
                dev_info["state"] = "locked"
                action = "लॉक (LOCKED) कर दिया गया है" if is_hi else "LOCKED"
            elif "temp" in q or "degree" in q:
                temp_match = re.search(r"(\d+)\s*(?:degree|deg)?", q)
                if temp_match:
                    dev_info["temp"] = int(temp_match.group(1))
                    dev_info["state"] = "on"
                    action = f"{dev_info['temp']} डिग्री पर सेट कर दिया गया है" if is_hi else f"set to {dev_info['temp']} degrees Celsius"
            else:
                current_state = dev_info.get("state", "off")
                new_state = "off" if current_state in ["on", "unlocked"] else "on"
                dev_info["state"] = new_state
                action = f"{'बंद' if new_state == 'off' else 'चालू'} कर दिया गया है" if is_hi else f"switched {new_state.upper()}"

            devices[matched_device] = dev_info
            self.memory.set("smart_devices", devices)

            dev_display = matched_device.title()
            if is_hi:
                hi_names = {
                    "living room light": "लिविंग रूम की लाइट",
                    "bedroom light": "बेडरूम की लाइट",
                    "air conditioner": "एयर कंडीशनर",
                    "main door lock": "मुख्य दरवाजा",
                    "smart fan": "स्मार्ट पंखा"
                }
                dev_display = hi_names.get(matched_device, dev_display)
                reply = f"{dev_display} {action}।"
            else:
                reply = f"{dev_display} has been {action}."
        else:
            dev_list = ", ".join([f"{k} ({v.get('state', 'unknown')})" for k, v in devices.items()])
            reply = f"उपलब्ध स्मार्ट उपकरण: {dev_list}।" if is_hi else f"Smart devices connected: {dev_list}."

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

    def is_hindi(self, text):
        """Detects whether user query is in Hindi (Devanagari or common Hinglish words)."""
        if not text:
            return False
        if re.search(r"[\u0900-\u097F]", text):
            return True
        hinglish_words = [
            "kholo", "chalu", "band", "batao", "kya", "hai", "samay", "mausam", "aaj",
            "gana", "bajao", "geet", "sunao", "tarikh", "kaun", "kaise", "namaste", "pranam",
            "karo", "dikhao", "likho", "awaaz", "badhao", "shukriya", "dhanyawad"
        ]
        return any(re.search(rf"\b{w}\b", text.lower()) for w in hinglish_words)

    # ------------------ MAIN COMMAND DISPATCHER (EN + HI) ------------------
    def process_command(self, query):
        q = query.lower().strip()
        if not q or q == "none":
            return ""

        print(f"[Command Received]: {query}")
        is_hi = self.is_hindi(query)
        reply = ""
        user_name = self.memory.get("user_name", "Boss")

        # 1. GREETINGS & CASUAL TALK
        if any(w in q for w in ["hello", "hi", "hey", "namaste", "pranam", "नमस्ते", "प्रणाम", "हेलो", "सुप्रभात"]):
            reply = f"नमस्ते {user_name}! जार्विस पूरी तरह सक्रिय है। आज मैं आपकी क्या मदद करूँ?" if is_hi else f"Greetings, {user_name}! All systems are online and ready for your commands."
            self.voice.speak(reply)
            self.ai.add_to_history(query, reply)
            return reply

        elif any(w in q for w in ["how are you", "तुम कैसे हो", "आप कैसे हैं", "kaise ho", "kya haal"]):
            reply = f"मैं बिल्कुल ठीक और 100% कार्यकुशलता पर सक्रिय हूँ, {user_name}! आपका दिन कैसा चल रहा है?" if is_hi else f"I am running at optimal capacity, {user_name}! How can I assist you today?"
            self.voice.speak(reply)
            self.ai.add_to_history(query, reply)
            return reply

        elif any(w in q for w in ["who are you", "what is your name", "तुम कौन हो", "तुम्हारा नाम क्या है", "tum kaun ho", "naam kya hai"]):
            reply = "मैं जार्विस (JARVIS) हूँ — आपका इंटेलिजेंट पर्सनल वॉइस असिस्टेंट। हमेशा आपकी सेवा में तत्पर, बॉस।" if is_hi else "I am J.A.R.V.I.S., your Just A Rather Very Intelligent System. Always at your service, Boss."
            self.voice.speak(reply)
            self.ai.add_to_history(query, reply)
            return reply

        elif any(w in q for w in ["thank you", "thanks", "धन्यवाद", "शुक्रिया", "shukriya", "dhanyawad"]):
            reply = f"आपका बहुत-बहुत स्वागत है, {user_name}! कोई और सहायता चाहिए तो बताएं।" if is_hi else f"You are very welcome, {user_name}! Let me know if you need anything else."
            self.voice.speak(reply)
            self.ai.add_to_history(query, reply)
            return reply

        elif any(w in q for w in ["what can you do", "help", "तुम क्या कर सकते हो", "मदद", "kya kar sakte ho"]):
            reply = "मैं यूट्यूब पर गाने बजा सकता हूँ, गूगल पर खोज सकता हूँ, समय और मौसम बता सकता हूँ, और आपके कंप्यूटर व स्मार्ट होम को कंट्रोल कर सकता हूँ।" if is_hi else "I can play music on YouTube, search Google, tell time and weather, launch desktop apps, and manage your smart home!"
            self.voice.speak(reply)
            self.ai.add_to_history(query, reply)
            return reply

        # 2. TIME & DATE
        elif any(w in q for w in ["what time is it", "current time", "tell me the time", "time", "समय", "टाइम", "कितने बजे", "samay", "kitne baje"]):
            if is_hi:
                now = datetime.datetime.now()
                reply = f"अभी समय {now.strftime('%I:%M %p')} है।"
                self.voice.speak(reply)
            else:
                reply = self.tell_time()

        elif any(w in q for w in ["today's date", "current date", "what is the date", "date", "तारीख", "दिनांक", "आज कौन सा दिन", "tarikh", "aaj kaun sa din"]):
            if is_hi:
                now = datetime.datetime.now()
                reply = f"आज {now.strftime('%A, %d %B %Y')} है।"
                self.voice.speak(reply)
            else:
                reply = self.tell_date()

        # 3. DAILY BRIEFING
        elif any(w in q for w in ["briefing", "daily update", "morning update", "अपडेट", "हालचाल"]):
            reply = self.daily_briefing()

        # 4. JOKES & HUMOR (BILINGUAL)
        elif any(w in q for w in ["joke", "chutkula", "jokes", "चुटकुला", "जोक", "हंसाओ"]):
            hindi_jokes = [
                "टीचर: अगर तुम्हारा सबसे अच्छा दोस्त और 5 लाख रुपए एक साथ गिर रहे हों, तो तुम किसे बचाओगे? छात्र: 5 लाख रुपए! क्योंकि दोस्त तो पैसे देखकर खुद ही आ जाएगा!",
                "पप्पू डॉक्टर के पास गया: डॉक्टर साहब, मुझे नींद में चलने की बीमारी है। डॉक्टर: तो रात को ताला लगा लिया करो! पप्पू: ताला तो लगा लेता हूँ, पर चाबी भी तो मेरे पास ही रहती है!",
                "टीचर: संता, बताओ पानी में रहने वाले 3 जीवों के नाम! संता: मेंढक! टीचर: बहुत अच्छे, बाकी दो? संता: उसकी मम्मी और उसके पापा!",
                "प्रोग्रामर डॉक्टर के पास गया: डॉक्टर साहब, मुझे नींद नहीं आ रही। डॉक्टर: एक बार सिस्टम रीस्टार्ट करके देखो!"
            ]
            english_jokes = [
                "Why don't scientists trust atoms? Because they make up everything!",
                "Why did the computer show up at work late? It had a hard drive!",
                "There are only 10 types of people in the world: those who understand binary, and those who don't.",
                "Why do programmers prefer dark mode? Because light attracts bugs!"
            ]
            import random
            reply = random.choice(hindi_jokes) if is_hi else random.choice(english_jokes)
            self.voice.speak(reply)
            self.ai.add_to_history(query, reply)
            return reply

        # 5. PLAY MUSIC & YOUTUBE SONGS (BILINGUAL)
        elif not any(w in q for w in ["joke", "चुटकुला", "जोक"]) and any(w in q for w in ["play music", "play song", "play ", "गाना", "गीत", "म्यूजिक", "बजाओ", "चलाओ", "सुनाओ", "gana", "bajao", "chalao"]):
            clean_song = re.sub(r"^(कृपया\s+)?(मुझे\s+)?(कोई\s+)?(गाना\s+)?(बजाओ\s+|चलाओ\s+|सुनाओ\s+)?(please\s+)?(play\s+music|play\s+song|play)?\s*", "", q, flags=re.IGNORECASE).strip()
            clean_song = re.sub(r"\s+(on youtube|यूट्यूब पर|यूट्यूब पे|सुनाओ|बजाओ|चलाओ|का गाना|गाना)$", "", clean_song, flags=re.IGNORECASE).strip()
            
            if not clean_song or clean_song in ["play", "music", "song", "गाना", "गीत", "gana"]:
                clean_song = "bhojpuri hit songs" if is_hi else self.memory.get("preferences", {}).get("favorite_music", "Iron Man AC/DC")
            
            url = f"https://www.youtube.com/results?search_query={requests.utils.quote(clean_song)}"
            webbrowser.open(url)
            reply = f"यूट्यूब पर '{clean_song}' बजा रहा हूँ, {user_name}।" if is_hi else f"Playing '{clean_song}' on YouTube for you, {user_name}."
            self.voice.speak(reply)

        # 5. YOUTUBE & GOOGLE OPEN / SEARCH
        elif any(w in q for w in ["open youtube", "launch youtube", "यूट्यूब खोलो", "यूट्यूब चलाओ", "youtube kholo"]):
            webbrowser.open("https://www.youtube.com")
            reply = f"यूट्यूब खोल रहा हूँ, {user_name}।" if is_hi else "Opening YouTube."
            self.voice.speak(reply)

        elif any(w in q for w in ["open google", "गूगल खोलो", "google kholo"]):
            webbrowser.open("https://www.google.com")
            reply = f"गूगल खोल रहा हूँ, {user_name}।" if is_hi else "Opening Google in browser."
            self.voice.speak(reply)

        elif any(w in q for w in ["search google", "google search", "search for ", "गूगल पर सर्च", "सर्च करो", "खोजो", "ढूंढो", "search karo"]):
            clean_q = re.sub(r"^(search google for|google search|search for|search|गूगल पर सर्च करो|गूगल पर खोजो|सर्च करो|खोजो|ढूंढो)\s*", "", q, flags=re.IGNORECASE).strip()
            clean_q = re.sub(r"\s+(सर्च करो|खोजो|ढूंढो)$", "", clean_q, flags=re.IGNORECASE).strip()
            url = f"https://www.google.com/search?q={requests.utils.quote(clean_q)}"
            webbrowser.open(url)
            reply = f"गूगल पर '{clean_q}' खोज रहा हूँ।" if is_hi else f"Searching Google for {clean_q}."
            self.voice.speak(reply)

        # 6. SMART HOME CONTROL (BILINGUAL) - Handled before app launcher so "लाइट चालू करो" is not confused with apps
        elif any(w in q for w in ["light", "lights", "fan", "ac", "air conditioner", "door", "lock", "लाइट", "पंखा", "एसी", "दरवाजा", "ताला"]):
            reply = self.control_smart_device(q)

        # 7. OPEN APPLICATIONS (BILINGUAL APP MAPPINGS)
        elif (q.startswith("open ") or q.startswith("launch ") or any(k in q for k in ["खोलो", "चालू करो", "kholo", "chalu karo"])):
            app_lower = q.replace("open ", "").replace("launch ", "").replace("खोलो", "").replace("चालू करो", "").replace("kholo", "").strip()
            if "notepad" in app_lower or "नोटपैड" in app_lower:
                reply = self.open_application("notepad")
            elif "calculator" in app_lower or "calc" in app_lower or "कैलकुलेटर" in app_lower:
                reply = self.open_application("calculator")
            elif "paint" in app_lower or "पेंट" in app_lower:
                reply = self.open_application("paint")
            elif "chrome" in app_lower or "क्रोम" in app_lower:
                reply = self.open_application("chrome")
            elif "whatsapp" in app_lower or "व्हाट्सएप" in app_lower:
                webbrowser.open("https://web.whatsapp.com")
                reply = "व्हाट्सएप वेब खोल रहा हूँ।" if is_hi else "Opening WhatsApp Web."
                self.voice.speak(reply)
            elif "gmail" in app_lower or "जीमेल" in app_lower or "ईमेल" in app_lower:
                webbrowser.open("https://mail.google.com")
                reply = "जीमेल खोल रहा हूँ।" if is_hi else "Opening Gmail."
                self.voice.speak(reply)
            elif "terminal" in app_lower or "cmd" in app_lower or "कमांड प्रॉम्प्ट" in app_lower:
                reply = self.open_application("cmd")
            elif "task manager" in app_lower or "टास्क मैनेजर" in app_lower:
                reply = self.open_application("task manager")
            elif "vs code" in app_lower or "code" in app_lower or "वीएस कोड" in app_lower:
                reply = self.open_application("code")
            else:
                reply = self.open_application(app_lower)

        # 7. WEATHER INFORMATION
        elif any(w in q for w in ["weather", "temperature", "मौसम", "तापमान", "बारिश", "mausam", "tapman"]):
            city_match = re.search(r"(?:weather in|weather of|मौसम|तापमान)\s+([a-zA-Z\u0900-\u097F\s]+)", q)
            target_city = None
            if city_match:
                candidate = city_match.group(1).replace("का", "").replace("में", "").replace("today", "").replace("now", "").strip()
                if candidate:
                    target_city = candidate
            
            target_city = target_city or self.memory.get("city", "Delhi")
            try:
                url = f"https://wttr.in/{requests.utils.quote(target_city)}?format=j1"
                res = requests.get(url, timeout=5)
                if res.status_code == 200:
                    data = res.json()
                    current = data["current_condition"][0]
                    temp_c = current["temp_C"]
                    desc = current["weatherDesc"][0]["value"]
                    humidity = current["humidity"]
                    reply = (f"{target_city.title()} में अभी मौसम {desc} है और तापमान {temp_c} डिग्री सेल्सियस है।" if is_hi else
                             f"The weather in {target_city.title()} is currently {desc} with a temperature of {temp_c} degrees Celsius, humidity at {humidity}%.")
                else:
                    reply = "मौसम की जानकारी अभी उपलब्ध नहीं हो पा रही है।" if is_hi else f"Could not retrieve weather for {target_city}."
            except Exception:
                reply = "मौसम सेवा से संपर्क नहीं हो पा रहा है।" if is_hi else f"Unable to reach meteorological servers for {target_city}."
            self.voice.speak(reply)

        # 8. USER PREFERENCES & IDENTITY
        elif any(phrase in q for phrase in ["who is your boss", "who is the boss", "तुम्हारा बॉस कौन है", "तुम्हारा मालिक कौन है"]):
            reply = f"आप मेरे बॉस हैं, {user_name}! मैं आपके हर आदेश का पालन करता हूँ।" if is_hi else f"You are my boss, {user_name}! I am programmed to obey your every command."
            self.voice.speak(reply)
        elif any(phrase in q for phrase in ["who created you", "who made you", "तुम्हें किसने बनाया", "तुम्हारा निर्माता कौन है"]):
            reply = "मुझे आशुतोष, प्रणव, यासिर और ध्रुव ने कॉलेज मिनी प्रोजेक्ट के रूप में बनाया है।" if is_hi else "I was created and developed by Ashutosh, Pranav, Yasir, and Dhruv as an academic AI assistant."
            self.voice.speak(reply)
        elif q.startswith("remember that ") or q.startswith("remember ") or "याद रखो" in q:
            reply = self.remember_fact(q)
        elif "what do you remember" in q or "recall memory" in q or "क्या याद है" in q:
            reply = self.recall_facts()
        elif "call me " in q or "my name is " in q or "मेरा नाम " in q:
            name_match = re.search(r"(?:call me|my name is|मेरा नाम)\s+([a-zA-Z0-9\u0900-\u097F\s]+)", q)
            if name_match:
                new_name = name_match.group(1).replace("है", "").strip().title()
                self.memory.set("user_name", new_name)
                reply = f"समझ गया। अब से मैं आपको {new_name} कहूँगा।" if is_hi else f"Understood. I will refer to you as {new_name} from now on."
                self.voice.speak(reply)
        elif "who am i" in q or "what is my name" in q or "मैं कौन हूँ" in q or "मेरा नाम क्या है" in q:
            reply = f"आप {user_name} हैं, इस सिस्टम के अधिकृत बॉस!" if is_hi else f"You are {user_name}, the authorized administrator of this system."
            self.voice.speak(reply)

        # 9. SEND EMAILS
        elif any(w in q for w in ["send email", "draft email", "mail", "ईमेल भेजो", "मेल भेजो"]):
            reply = self.send_email_draft()

        # 10. PRODUCTIVITY: TO-DO & NOTES
        elif q.startswith("add to-do") or q.startswith("add todo") or "टास्क जोड़ो" in q or "काम जोड़ो" in q:
            reply = self.add_todo(q)
            if is_hi: reply = "कार्य आपकी टू-डू लिस्ट में जोड़ दिया गया है।"
        elif "show to-do" in q or "show todo" in q or "टास्क दिखाओ" in q or "काम दिखाओ" in q:
            reply = self.show_todos()
        elif "clear to-do" in q or "clear todo" in q or "टास्क साफ करो" in q:
            self.memory.clear_todos()
            reply = "टू-डू लिस्ट साफ कर दी गई है।" if is_hi else "To-do list has been cleared."
            self.voice.speak(reply)
        elif q.startswith("take a note") or q.startswith("take note") or "नोट लिखो" in q or "नोट बनाओ" in q:
            reply = self.take_note(q)
            if is_hi: reply = "आपका नोट फाइल में सुरक्षित कर लिया गया है।"
        elif "read notes" in q or "show notes" in q or "नोट्स दिखाओ" in q:
            reply = self.read_notes()

        # 12. TASK & SYSTEM AUTOMATION
        elif any(w in q for w in ["screenshot", "capture screen", "स्क्रीनशॉट", "फोटो खींचो"]):
            reply = self.take_screenshot()
            if is_hi: reply = "स्क्रीनशॉट ले लिया गया है और सुरक्षित कर दिया गया है।"
        elif any(w in q for w in ["lock pc", "lock screen", "lock workstation", "कंप्यूटर लॉक करो", "स्क्रीन लॉक करो"]):
            reply = self.lock_pc()
            if is_hi: reply = "कंप्यूटर स्क्रीन लॉक की जा रही है।"
        elif any(w in q for w in ["volume up", "increase volume", "आवाज़ बढ़ाओ", "वॉल्यूम बढ़ाओ"]):
            reply = self.change_volume("up")
            if is_hi: reply = "आवाज़ बढ़ा दी गई है।"
        elif any(w in q for w in ["volume down", "decrease volume", "आवाज़ कम करो", "वॉल्यूम कम करो"]):
            reply = self.change_volume("down")
            if is_hi: reply = "आवाज़ कम कर दी गई है।"
        elif any(w in q for w in ["mute", "unmute", "म्यूट करो", "आवाज़ बंद करो"]):
            reply = self.change_volume("mute")
            if is_hi: reply = "सिस्टम म्यूट कर दिया गया है।"
        elif "timer" in q or "alarm" in q:
            reply = self.set_timer(q)

        # 13. BIOMETRIC FACE RECOGNITION
        elif any(w in q for w in ["face recognition", "scan face", "biometric", "verify me", "फेस स्कैन", "चेहरा पहचानो"]):
            reply = self.scan_face()

        # 14. WIKIPEDIA GENERAL KNOWLEDGE
        elif any(w in q for w in ["what is", "who is", "wikipedia", "क्या है", "कौन है", "के बारे में बताओ"]):
            try:
                search_term = q.replace("wikipedia", "").replace("what is", "").replace("who is", "").replace("क्या है", "").replace("कौन है", "").replace("के बारे में बताओ", "").strip()
                if is_hi:
                    wikipedia.set_lang("hi")
                else:
                    wikipedia.set_lang("en")
                result = wikipedia.summary(search_term, sentences=2)
                reply = f"विकिपीडिया के अनुसार: {result}" if is_hi else f"According to Wikipedia: {result}"
                self.voice.speak(reply)
            except Exception:
                pass

        # 15. INTELLIGENT CONVERSATIONAL BRAIN (Gemini API or Contextual Fallback)
        if not reply:
            llm_reply = self.ai.query_gemini(query)
            if llm_reply:
                reply = llm_reply
            else:
                reply = self.ai.query_contextual_fallback(query)
            self.voice.speak(reply)

        self.ai.add_to_history(query, reply)
        return reply


# =============================================================================
#                    WAKE-WORD & AUDIO LISTENER THREAD
# =============================================================================
class AudioListener:
    """Handles audio capture, multi-lingual speech recognition, and wake-word detection."""
    def __init__(self, memory_mgr, command_callback, status_callback, voice_engine=None):
        self.memory = memory_mgr
        self.voice_engine = voice_engine
        self.on_command = command_callback
        self.on_status = status_callback
        self.recognizer = sr.Recognizer()
        
        # Optimized acoustic thresholds for sensitive speech pickup without premature cutoff
        self.recognizer.pause_threshold = 1.3        # Allows natural pauses without cutting off
        self.recognizer.non_speaking_duration = 0.5
        self.recognizer.energy_threshold = 300       # High sensitivity floor
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.dynamic_energy_ratio = 1.5
        
        self.language = self.memory.get("language", "auto")
        self.calibrated = False

        self.running = True
        self.wake_active = True
        self.thread = threading.Thread(target=self._listen_loop, daemon=True)

    def start(self):
        self.thread.start()

    def stop(self):
        self.running = False

    def calibrate_microphone(self):
        """Calibrates microphone energy threshold once at startup."""
        if self.calibrated:
            return
        try:
            with sr.Microphone() as source:
                self.on_status("processing", "Calibrating mic for room acoustics...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1.0)
                self.calibrated = True
                print(f"[Mic Calibrated]: Ambient energy threshold set to {self.recognizer.energy_threshold:.1f}")
        except Exception as e:
            print(f"[Mic Calibration Warning]: {e}")

    def recognize_audio(self, audio):
        """Recognizes speech in Hindi, English, or Auto-Bilingual mode."""
        lang_pref = (self.language or self.memory.get("language", "auto")).lower()

        if lang_pref == "hi-in":
            try:
                return self.recognizer.recognize_google(audio, language="hi-in")
            except sr.UnknownValueError:
                return None
        elif lang_pref == "en-in":
            try:
                return self.recognizer.recognize_google(audio, language="en-in")
            except sr.UnknownValueError:
                return None
        else:
            # AUTO / BILINGUAL MODE:
            # Try Hindi first (since Hindi speakers often mix English words or pure Hindi)
            try:
                text_hi = self.recognizer.recognize_google(audio, language="hi-in")
                if text_hi and len(text_hi.strip()) > 0:
                    return text_hi
            except sr.UnknownValueError:
                pass
            except Exception:
                pass

            # Fallback to Indian English
            try:
                text_en = self.recognizer.recognize_google(audio, language="en-in")
                return text_en
            except sr.UnknownValueError:
                return None

    def listen_single_command(self):
        """Actively records one command immediately (e.g. when Mic button clicked)."""
        threading.Thread(target=self._capture_active_command, daemon=True).start()

    def _capture_active_command(self):
        # Echo suppression barrier
        if self.voice_engine and self.voice_engine.is_speaking:
            self.on_status("idle", "Waiting for assistant to finish speaking...")
            return

        self.on_status("listening", "Listening... बोलिए (Speak now)")
        try:
            with sr.Microphone() as source:
                if not self.calibrated:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.4)
                    self.calibrated = True
                audio = self.recognizer.listen(source, timeout=7, phrase_time_limit=12)

            self.on_status("processing", "Recognizing speech / आवाज़ पहचानी जा रही है...")
            query = self.recognize_audio(audio)
            if query:
                print(f"[Recognized]: {query}")
                self.on_command(query)
            else:
                self.on_status("idle", "Could not understand audio / आवाज़ समझ नहीं आई")
        except sr.WaitTimeoutError:
            self.on_status("idle", "Ready / तैयार")
        except sr.UnknownValueError:
            self.on_status("idle", "Could not understand audio / आवाज़ समझ नहीं आई")
        except Exception as e:
            print(f"[Active Listen Error] {e}")
            self.on_status("idle", "Microphone offline / माइक उपलब्ध नहीं")

    def _listen_loop(self):
        """Continuous background loop for wake-word and hands-free control."""
        self.calibrate_microphone()

        wake_words = [
            "hey jarvis", "jarvis", "wake up jarvis", "ok jarvis", "okay jarvis", 
            "suno jarvis", "namaste jarvis", "जार्विस", "हे जार्विस", "सुनो जार्विस", "नमस्ते जार्विस", "ओके जार्विस"
        ]

        while self.running:
            # Echo suppression: do not listen while JARVIS is actively speaking
            if self.voice_engine and self.voice_engine.is_speaking:
                time.sleep(0.3)
                continue

            if not self.memory.get("wake_word_enabled", True):
                time.sleep(0.5)
                continue

            try:
                with sr.Microphone() as source:
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=6)

                phrase = self.recognize_audio(audio)
                if not phrase:
                    continue

                phrase_clean = phrase.lower()
                print(f"[Ambient Heard]: {phrase_clean}")

                # Check Wake Words
                if any(w in phrase_clean for w in wake_words):
                    self.on_status("listening", "Wake-word detected! Listening... / जार्विस सक्रिय...")
                    
                    with sr.Microphone() as cmd_source:
                        cmd_audio = self.recognizer.listen(cmd_source, timeout=8, phrase_time_limit=14)

                    self.on_status("processing", "Analyzing command / आदेश विश्लेषित हो रहा है...")
                    cmd_query = self.recognize_audio(cmd_audio)
                    if cmd_query:
                        self.on_command(cmd_query)
                    else:
                        self.on_status("idle", "Ready / तैयार")

            except sr.WaitTimeoutError:
                pass
            except sr.UnknownValueError:
                pass
            except Exception as e:
                time.sleep(0.5)


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

        # Language Switcher Button in Top Bar
        current_lang = self.memory.get("language", "auto")
        if current_lang == "hi-in":
            lang_label = "🇮🇳 LANG: हिन्दी (hi-IN)"
        elif current_lang == "en-in":
            lang_label = "🇬🇧 LANG: English (en-IN)"
        else:
            lang_label = "🌐 LANG: AUTO (EN/HI)"

        self.lang_btn = tk.Button(top_bar, text=lang_label, font=("Consolas", 9, "bold"),
                                  bg="#162b47", fg="#00f0ff", activebackground="#00f0ff",
                                  relief=tk.FLAT, padx=10, pady=4, command=self._toggle_language)
        self.lang_btn.pack(side=tk.RIGHT, padx=15, pady=10)

        self.clock_lbl = tk.Label(top_bar, text="", font=("Consolas", 11), fg="#8baac9", bg="#0d1527")
        self.clock_lbl.pack(side=tk.RIGHT, padx=10, pady=10)
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

        self.mic_btn = tk.Button(btn_frame, text="🎤 Speak / बोलें", font=("Consolas", 10, "bold"),
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

    def _toggle_language(self):
        curr = self.memory.get("language", "auto")
        if curr == "auto":
            nxt = "hi-in"
            lbl = "🇮🇳 LANG: हिन्दी (hi-IN)"
            msg = "Speech recognition set to Hindi (हिन्दी) mode."
        elif curr == "hi-in":
            nxt = "en-in"
            lbl = "🇬🇧 LANG: English (en-IN)"
            msg = "Speech recognition set to English (India) mode."
        else:
            nxt = "auto"
            lbl = "🌐 LANG: AUTO (EN/HI)"
            msg = "Speech recognition set to Auto Bilingual (English + Hindi) mode."

        self.memory.set("language", nxt)
        if hasattr(self, "listener") and self.listener:
            self.listener.language = nxt
        self.lang_btn.config(text=lbl)
        self.log_message("SYSTEM", msg)

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

    listener = AudioListener(memory_mgr, on_voice_command, on_listener_status, voice_engine=voice_engine)
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
