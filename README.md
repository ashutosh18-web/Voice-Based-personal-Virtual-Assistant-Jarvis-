# J.A.R.V.I.S. - Advanced AI Desktop Voice Assistant

A complete, futuristic voice-activated AI desktop assistant built in Python.

## 🌟 Key Features

1. **Animated Futuristic GUI**:
   - Arc-Reactor animated canvas with rotating segmented rings and pulsing core.
   - Dynamic soundwave audio visualizer that reacts when speaking or listening.
   - Diagnostic console displaying real-time speech transcription and assistant feedback.
   - Live clock, date, and system status indicators.

2. **Wake-Word Detection**:
   - Continuous background listening for **"Hey Jarvis"**, **"Jarvis"**, or **"Wake up Jarvis"**.
   - Push-to-talk mic button and keyboard text-entry fallback.

3. **Time, Date & Daily Briefing**:
   - Current time, formatted date, and one-command complete daily briefing.

4. **Application Launcher**:
   - Opens Notepad, Calculator, MS Paint, Google Chrome, Command Prompt, Task Manager, VS Code, Settings, and more.

5. **Voice Search & Music Playback**:
   - Voice-controlled Google searching and YouTube video/music playback.

6. **Live Weather Forecast**:
   - Fetches live temperature, weather conditions, humidity, and wind speed (via free Open-Meteo / wttr API without requiring API keys).

7. **Intelligent Conversational Brain (LLM & Context Memory)**:
   - Built-in multi-turn contextual conversational AI with memory.
   - Direct integration with **Google Gemini API** (`GEMINI_API_KEY`) for deep reasoning and general knowledge.

8. **Persistent Memory & Preferences**:
   - Automatically saves user name, preferences, facts, and tasks to `jarvis_memory.json`.
   - Remembers facts: *"remember that my car is red"*, *"what do you remember"*.

9. **Smart Device / IoT Hub**:
   - Controls simulated or connected smart devices: living room light, bedroom light, air conditioner temperature, fan, and door locks.

10. **Productivity Suite**:
    - **To-Do List**: Add, view, and clear tasks.
    - **Quick Notes**: Record thoughts with timestamps to `jarvis_notes.txt`.
    - **Timers**: Set countdown timers by voice (*"set a timer for 10 seconds"*).

11. **Task & System Automation**:
    - Take desktop screenshots (*saved automatically in the `screenshots/` folder*).
    - Adjust system volume (volume up, volume down, mute).
    - Lock Windows workstation securely.

12. **Face Recognition & Biometrics**:
    - Biometric verification scan using OpenCV Haar cascades (with simulated fallback if webcam is unavailable).

---

## 🚀 How to Run

1. Open your terminal in this directory:
   ```bash
   python jarvis.py
   ```

2. Optional (for live camera face recognition):
   ```bash
   pip install opencv-python
   ```

---

## 🎙️ Example Voice Commands

| Category | Example Phrases |
|---|---|
| **Wake Word** | *"Hey Jarvis"*, *"Jarvis"* |
| **Time & Date** | *"What time is it?"*, *"Tell me today's date"* |
| **Briefing** | *"Give me my daily briefing"* |
| **Apps** | *"Open Notepad"*, *"Launch Calculator"*, *"Open Chrome"*, *"Open Paint"* |
| **Search** | *"Search Google for Python tutorials"*, *"Google James Webb telescope"* |
| **Music** | *"Play music"*, *"Play Believer on YouTube"* |
| **Weather** | *"What is the weather?"*, *"Weather in New York"* |
| **Memory** | *"Remember that my birthday is in July"*, *"What do you remember?"* |
| **Smart Home** | *"Turn on the living room light"*, *"Set AC to 21 degrees"*, *"Lock the door"* |
| **To-Dos & Notes** | *"Add to-do submit mini project"*, *"Show to-do list"*, *"Take a note buy groceries"* |
| **System** | *"Take screenshot"*, *"Volume up"*, *"Mute"*, *"Lock screen"*, *"Set timer for 5 minutes"* |
| **Biometrics** | *"Scan face"*, *"Face recognition"* |
| **AI Questions** | *"Who is Albert Einstein?"*, *"Calculate 45 times 12"*, *"Tell me a science fact"* |
