import os
from PIL import Image, ImageDraw, ImageFont

# Set up clean academic color palette (Light mode for A4 printing)
BG_WHITE = (255, 255, 255)
BOX_BG = (245, 248, 252)
BOX_BORDER = (40, 80, 130)
PRIMARY_BLUE = (20, 60, 120)
ACCENT_BLUE = (41, 128, 185)
ACCENT_GREEN = (39, 174, 96)
ACCENT_RED = (192, 57, 43)
TEXT_DARK = (25, 25, 25)
TEXT_MUTED = (85, 85, 85)
ARROW_COLOR = (40, 80, 130)

# Fonts
try:
    FONT_TITLE = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 26)
    FONT_HEADER = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 20)
    FONT_BOLD = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 16)
    FONT_BODY = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 14)
    FONT_SMALL = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 12)
    FONT_MONO = ImageFont.truetype("C:/Windows/Fonts/consolab.ttf", 14)
except Exception:
    FONT_TITLE = ImageFont.load_default()
    FONT_HEADER = ImageFont.load_default()
    FONT_BOLD = ImageFont.load_default()
    FONT_BODY = ImageFont.load_default()
    FONT_SMALL = ImageFont.load_default()
    FONT_MONO = ImageFont.load_default()


def draw_arrow(draw, x1, y1, x2, y2, color=ARROW_COLOR, width=2, arrow_size=8):
    """Draws a directed arrow from (x1, y1) to (x2, y2)."""
    draw.line([(x1, y1), (x2, y2)], fill=color, width=width)
    import math
    angle = math.atan2(y2 - y1, x2 - x1)
    # Arrow head points
    p1 = (x2 - arrow_size * math.cos(angle - math.pi / 6),
          y2 - arrow_size * math.sin(angle - math.pi / 6))
    p2 = (x2 - arrow_size * math.cos(angle + math.pi / 6),
          y2 - arrow_size * math.sin(angle + math.pi / 6))
    draw.polygon([(x2, y2), p1, p2], fill=color)


def draw_rounded_rect(draw, x, y, w, h, fill=BOX_BG, outline=BOX_BORDER, radius=8, width=2):
    """Draws a crisp rectangle with rounded corners."""
    draw.rounded_rectangle([(x, y), (x + w, y + h)], radius=radius, fill=fill, outline=outline, width=width)


# =============================================================================
# 1. SYSTEM ARCHITECTURE DIAGRAM (Fig. 3.1)
# =============================================================================
def generate_architecture_diagram():
    w, h = 1600, 950
    img = Image.new("RGB", (w, h), BG_WHITE)
    draw = ImageDraw.Draw(img)

    # Title Banner
    draw.text((w // 2 - 320, 30), "SYSTEM ARCHITECTURE: VOICE-BASED VIRTUAL ASSISTANT (JARVIS)", font=FONT_TITLE, fill=PRIMARY_BLUE)
    draw.line([(w // 2 - 330, 70), (w // 2 + 330, 70)], fill=ACCENT_BLUE, width=2)

    # Column 1: Audio Input & Acoustic Preprocessing
    draw_rounded_rect(draw, 50, 110, 320, 780, fill=(245, 248, 255), outline=PRIMARY_BLUE)
    draw.text((75, 130), "1. AUDIO ACQUISITION & FILTER", font=FONT_HEADER, fill=PRIMARY_BLUE)
    draw.line([(75, 160), (345, 160)], fill=ACCENT_BLUE, width=1)

    draw_rounded_rect(draw, 75, 180, 270, 90, fill=BG_WHITE, outline=BOX_BORDER)
    draw.text((95, 195), "Microphone Input", font=FONT_BOLD, fill=TEXT_DARK)
    draw.text((95, 225), "• PyAudio (Desktop)\n• Web Audio API (Web)", font=FONT_SMALL, fill=TEXT_MUTED)

    draw_arrow(draw, 210, 270, 210, 320)

    draw_rounded_rect(draw, 75, 320, 270, 130, fill=BG_WHITE, outline=BOX_BORDER)
    draw.text((95, 335), "Noise & Energy Filter", font=FONT_BOLD, fill=TEXT_DARK)
    draw.text((95, 365), "• Ambient Calibration\n• Energy Thresholding\n• Silence Detection (1.3s)", font=FONT_SMALL, fill=TEXT_MUTED)

    draw_arrow(draw, 210, 450, 210, 500)

    # Echo Lock Box (Highlighted in Neon/Amber)
    draw_rounded_rect(draw, 75, 500, 270, 150, fill=(254, 249, 231), outline=(214, 137, 16))
    draw.text((90, 515), "Echo Suppression Lock", font=FONT_BOLD, fill=(183, 119, 14))
    draw.text((90, 545), "• State: isSpeaking Flag\n• Mutes Mic During TTS\n• Prevents Feedback Loops\n• Auto-Resumes on Idle", font=FONT_SMALL, fill=TEXT_DARK)

    draw_arrow(draw, 210, 650, 210, 700)

    draw_rounded_rect(draw, 75, 700, 270, 120, fill=BG_WHITE, outline=BOX_BORDER)
    draw.text((95, 715), "Clean Audio Buffer", font=FONT_BOLD, fill=TEXT_DARK)
    draw.text((95, 745), "• Multi-word Continuous Stream\n• PCM 16kHz WAV format", font=FONT_SMALL, fill=TEXT_MUTED)

    # Arrow to Column 2
    draw_arrow(draw, 370, 760, 420, 760)

    # Column 2: Speech Recognition & NLP Intent Engine
    draw_rounded_rect(draw, 420, 110, 350, 780, fill=(245, 252, 248), outline=ACCENT_GREEN)
    draw.text((445, 130), "2. SPEECH-TO-TEXT & NLP", font=FONT_HEADER, fill=ACCENT_GREEN)
    draw.line([(445, 160), (745, 160)], fill=ACCENT_GREEN, width=1)

    draw_rounded_rect(draw, 445, 180, 300, 130, fill=BG_WHITE, outline=BOX_BORDER)
    draw.text((465, 195), "Speech Recognition Engine", font=FONT_BOLD, fill=TEXT_DARK)
    draw.text((465, 225), "• Google Cloud Speech API\n• W3C Web Speech API\n• en-IN & hi-IN Accents", font=FONT_SMALL, fill=TEXT_MUTED)

    draw_arrow(draw, 595, 310, 595, 360)

    draw_rounded_rect(draw, 445, 360, 300, 140, fill=BG_WHITE, outline=BOX_BORDER)
    draw.text((465, 375), "Text Normalization Matrix", font=FONT_BOLD, fill=TEXT_DARK)
    draw.text((465, 405), "• Lowercasing & Punctuation Strip\n• Stop-word Filtering\n• Regional Query Sanitizer\n  (e.g., 'Play Bhojpuri song')", font=FONT_SMALL, fill=TEXT_MUTED)

    draw_arrow(draw, 595, 500, 595, 550)

    draw_rounded_rect(draw, 445, 550, 300, 150, fill=BG_WHITE, outline=BOX_BORDER)
    draw.text((465, 565), "Intent Classifier & Router", font=FONT_BOLD, fill=TEXT_DARK)
    draw.text((465, 595), "• Keyword Pattern Heuristics\n• Action Domain Matcher:\n  - System OS / Launcher\n  - Media & YouTube\n  - Cloud API / Weather / Wiki\n  - Smart Home Hub", font=FONT_SMALL, fill=TEXT_MUTED)

    draw_arrow(draw, 595, 700, 595, 740)

    draw_rounded_rect(draw, 445, 740, 300, 100, fill=BG_WHITE, outline=BOX_BORDER)
    draw.text((465, 755), "Persistent Memory Matrix", font=FONT_BOLD, fill=TEXT_DARK)
    draw.text((465, 785), "• JSON Storage (Desktop)\n• LocalStorage (Web Client)", font=FONT_SMALL, fill=TEXT_MUTED)

    # Arrow to Column 3
    draw_arrow(draw, 770, 430, 820, 430)

    # Column 3: Execution Subsystems & APIs
    draw_rounded_rect(draw, 820, 110, 380, 780, fill=(255, 250, 245), outline=(230, 126, 34))
    draw.text((845, 130), "3. DISPATCHER & SUBSYSTEMS", font=FONT_HEADER, fill=(211, 84, 0))
    draw.line([(845, 160), (1175, 160)], fill=(230, 126, 34), width=1)

    subsystems = [
        ("Desktop System Automation", "• Launch Apps (Notepad, Calc, CMD)\n• Volume Control & Screen Lock\n• Screenshot & Note Taker", 180),
        ("Media & YouTube Streaming", "• Regex 'Play <song>' Extraction\n• YouTube Search Dispatcher\n• Music Player Integration", 320),
        ("Cloud Knowledge & Weather", "• Wikipedia Summary API\n• Real-Time wttr.in Weather API\n• Google Search Auto-Lookup", 460),
        ("Smart Home & IoT Simulator", "• Living Room / Bedroom Lights\n• AC Thermostat Control\n• Main Door Security Lock", 600),
        ("Computer Vision & Security", "• OpenCV Webcam Face Scanner\n• Haar Cascade Classifier\n• Biometric Verification HUD", 740)
    ]

    for title, desc, y_pos in subsystems:
        draw_rounded_rect(draw, 845, y_pos, 330, 115, fill=BG_WHITE, outline=BOX_BORDER)
        draw.text((860, y_pos + 12), title, font=FONT_BOLD, fill=PRIMARY_BLUE)
        draw.text((860, y_pos + 38), desc, font=FONT_SMALL, fill=TEXT_MUTED)

    # Arrow to Column 4
    draw_arrow(draw, 1200, 480, 1250, 480)

    # Column 4: Multimodal Output (TTS & Arc-Reactor Visualizer)
    draw_rounded_rect(draw, 1250, 110, 300, 780, fill=(245, 248, 255), outline=ACCENT_BLUE)
    draw.text((1270, 130), "4. OUTPUT & FEEDBACK", font=FONT_HEADER, fill=ACCENT_BLUE)
    draw.line([(1270, 160), (1530, 160)], fill=ACCENT_BLUE, width=1)

    draw_rounded_rect(draw, 1270, 180, 260, 160, fill=BG_WHITE, outline=BOX_BORDER)
    draw.text((1285, 195), "Speech Synthesis Engine", font=FONT_BOLD, fill=TEXT_DARK)
    draw.text((1285, 225), "• pyttsx3 (SAPI5 Driver)\n• Web SpeechSynthesis API\n• Natural Tone & Speed Rate\n• Dispatches 'Start Speaking'", font=FONT_SMALL, fill=TEXT_MUTED)

    draw_arrow(draw, 1400, 340, 1400, 390)

    draw_rounded_rect(draw, 1270, 390, 260, 160, fill=BG_WHITE, outline=BOX_BORDER)
    draw.text((1285, 405), "HUD Visual Feedback", font=FONT_BOLD, fill=TEXT_DARK)
    draw.text((1285, 435), "• 60 FPS Canvas Arc-Reactor\n• Dynamic Soundwave Visualizer\n• Live Diagnostic Terminal\n• State Badge Indicators", font=FONT_SMALL, fill=TEXT_MUTED)

    draw_arrow(draw, 1400, 550, 1400, 600)

    draw_rounded_rect(draw, 1270, 600, 260, 120, fill=BG_WHITE, outline=BOX_BORDER)
    draw.text((1285, 615), "Physical Audio Output", font=FONT_BOLD, fill=TEXT_DARK)
    draw.text((1285, 645), "• Loudspeaker / Headset\n• Clear Vocal Feedback Aloud", font=FONT_SMALL, fill=TEXT_MUTED)

    # Echo Lock Return Path (Dotted feedback arrow)
    draw.line([(1400, 720), (1400, 840)], fill=ACCENT_RED, width=2)
    draw.line([(1400, 840), (210, 840)], fill=ACCENT_RED, width=2)
    draw_arrow(draw, 210, 840, 210, 660, color=ACCENT_RED, width=2)
    draw.rectangle([(650, 825), (1000, 855)], fill=(253, 237, 236), outline=ACCENT_RED, width=1)
    draw.text((665, 832), "Active Feedback Lock: isSpeaking = True blocks mic input", font=FONT_SMALL, fill=ACCENT_RED)

    out_path = os.path.abspath("fig_3_1_architecture.png")
    img.save(out_path, quality=95)
    print("Saved Architecture Diagram:", out_path)


# =============================================================================
# 2. FLOWCHART DIAGRAM (Fig. 3.2)
# =============================================================================
def generate_flowchart_diagram():
    w, h = 1100, 1450
    img = Image.new("RGB", (w, h), BG_WHITE)
    draw = ImageDraw.Draw(img)

    draw.text((w // 2 - 300, 25), "FLOWCHART: SPEECH PROCESSING & ECHO CANCELLATION", font=FONT_TITLE, fill=PRIMARY_BLUE)
    draw.line([(w // 2 - 310, 60), (w // 2 + 310, 60)], fill=ACCENT_BLUE, width=2)

    cx = w // 2

    # Step 1: Start
    draw_rounded_rect(draw, cx - 140, 80, 280, 55, fill=(234, 250, 234), outline=ACCENT_GREEN, radius=25)
    draw.text((cx - 100, 96), "START / INITIALIZE", font=FONT_BOLD, fill=ACCENT_GREEN)
    draw_arrow(draw, cx, 135, cx, 175)

    # Step 2: Calibrate & Listen
    draw_rounded_rect(draw, cx - 180, 175, 360, 60, fill=BOX_BG, outline=BOX_BORDER)
    draw.text((cx - 160, 192), "Calibrate Ambient Noise & Open Audio Stream", font=FONT_BODY, fill=TEXT_DARK)
    draw_arrow(draw, cx, 235, cx, 275)

    # Step 3: Decision: Is Assistant Speaking?
    # Draw Diamond for Decision
    dy = 320
    d_half_w = 180
    d_half_h = 45
    pts = [(cx, dy - d_half_h), (cx + d_half_w, dy), (cx, dy + d_half_h), (cx - d_half_w, dy)]
    draw.polygon(pts, fill=(254, 249, 231), outline=(214, 137, 16), width=2)
    draw.text((cx - 120, dy - 12), "Is Assistant Speaking?", font=FONT_BOLD, fill=(183, 119, 14))
    draw.text((cx - 75, dy + 8), "(isSpeaking == True)", font=FONT_SMALL, fill=(183, 119, 14))

    # Branch: YES (Loop back / mute)
    draw.text((cx + d_half_w + 10, dy - 20), "YES", font=FONT_BOLD, fill=ACCENT_RED)
    draw.line([(cx + d_half_w, dy), (cx + 340, dy)], fill=ACCENT_RED, width=2)
    draw.line([(cx + 340, dy), (cx + 340, 205)], fill=ACCENT_RED, width=2)
    draw_arrow(draw, cx + 340, 205, cx + 180, 205, color=ACCENT_RED, width=2)
    draw.rectangle([(cx + 200, 230), (cx + 420, 260)], fill=(253, 237, 236), outline=ACCENT_RED, width=1)
    draw.text((cx + 210, 238), "Mute Buffer (Loop Blocked)", font=FONT_SMALL, fill=ACCENT_RED)

    # Branch: NO (Proceed)
    draw.text((cx + 10, dy + d_half_h + 10), "NO", font=FONT_BOLD, fill=ACCENT_GREEN)
    draw_arrow(draw, cx, dy + d_half_h, cx, dy + d_half_h + 50)

    # Step 4: Microphone Samples Speech
    y4 = dy + d_half_h + 50
    draw_rounded_rect(draw, cx - 180, y4, 360, 60, fill=BOX_BG, outline=BOX_BORDER)
    draw.text((cx - 150, y4 + 18), "Continuous Audio Sampling & Streaming", font=FONT_BODY, fill=TEXT_DARK)
    draw_arrow(draw, cx, y4 + 60, cx, y4 + 100)

    # Step 5: Decision: Silence Debounce Elapsed?
    y5 = y4 + 145
    pts5 = [(cx, y5 - d_half_h), (cx + d_half_w, y5), (cx, y5 + d_half_h), (cx - d_half_w, y5)]
    draw.polygon(pts5, fill=(254, 249, 231), outline=(214, 137, 16), width=2)
    draw.text((cx - 120, y5 - 12), "1.3s Silence Debounce?", font=FONT_BOLD, fill=(183, 119, 14))
    draw.text((cx - 100, y5 + 8), "(Capture multi-word phrase)", font=FONT_SMALL, fill=(183, 119, 14))

    # NO -> Continue Buffering
    draw.text((cx - d_half_w - 40, y5 - 20), "NO", font=FONT_BOLD, fill=(214, 137, 16))
    draw.line([(cx - d_half_w, y5), (cx - 300, y5)], fill=ARROW_COLOR, width=2)
    draw.line([(cx - 300, y5), (cx - 300, y4 + 30)], fill=ARROW_COLOR, width=2)
    draw_arrow(draw, cx - 300, y4 + 30, cx - 180, y4 + 30)

    # YES -> Dispatch to STT
    draw.text((cx + 10, y5 + d_half_h + 10), "YES", font=FONT_BOLD, fill=ACCENT_GREEN)
    draw_arrow(draw, cx, y5 + d_half_h, cx, y5 + d_half_h + 50)

    # Step 6: Convert Speech to Text
    y6 = y5 + d_half_h + 50
    draw_rounded_rect(draw, cx - 180, y6, 360, 60, fill=BOX_BG, outline=BOX_BORDER)
    draw.text((cx - 140, y6 + 18), "Convert Speech to Text (Google / Web Speech)", font=FONT_BODY, fill=TEXT_DARK)
    draw_arrow(draw, cx, y6 + 60, cx, y6 + 100)

    # Step 7: String Normalization & Cleaning
    y7 = y6 + 100
    draw_rounded_rect(draw, cx - 180, y7, 360, 60, fill=BOX_BG, outline=BOX_BORDER)
    draw.text((cx - 150, y7 + 18), "Regex Normalization & Action Intent Mapping", font=FONT_BODY, fill=TEXT_DARK)
    draw_arrow(draw, cx, y7 + 60, cx, y7 + 100)

    # Step 8: Set isSpeaking = True
    y8 = y7 + 100
    draw_rounded_rect(draw, cx - 180, y8, 360, 55, fill=(254, 249, 231), outline=(214, 137, 16))
    draw.text((cx - 150, y8 + 16), "Set isSpeaking = True (Activate Echo Lock)", font=FONT_BOLD, fill=(183, 119, 14))
    draw_arrow(draw, cx, y8 + 55, cx, y8 + 95)

    # Step 9: Execute Action
    y9 = y8 + 95
    draw_rounded_rect(draw, cx - 180, y9, 360, 60, fill=BOX_BG, outline=BOX_BORDER)
    draw.text((cx - 160, y9 + 18), "Execute Action (App / Music / Weather / IoT)", font=FONT_BODY, fill=TEXT_DARK)
    draw_arrow(draw, cx, y9 + 60, cx, y9 + 100)

    # Step 10: TTS Voice Output & HUD Animation
    y10 = y9 + 100
    draw_rounded_rect(draw, cx - 180, y10, 360, 60, fill=BOX_BG, outline=BOX_BORDER)
    draw.text((cx - 165, y10 + 18), "Synthesize Audio Reply Aloud & Animate HUD", font=FONT_BODY, fill=TEXT_DARK)
    draw_arrow(draw, cx, y10 + 60, cx, y10 + 100)

    # Step 11: Release Lock
    y11 = y10 + 100
    draw_rounded_rect(draw, cx - 180, y11, 360, 55, fill=(234, 250, 234), outline=ACCENT_GREEN)
    draw.text((cx - 155, y11 + 16), "Set isSpeaking = False (Release Echo Lock)", font=FONT_BOLD, fill=ACCENT_GREEN)
    draw_arrow(draw, cx, y11 + 55, cx, y11 + 95)

    # Loop back to listen
    draw.line([(cx, y11 + 95), (cx, y11 + 115)], fill=ARROW_COLOR, width=2)
    draw.line([(cx, y11 + 115), (cx + 390, y11 + 115)], fill=ARROW_COLOR, width=2)
    draw.line([(cx + 390, y11 + 115), (cx + 390, 145)], fill=ARROW_COLOR, width=2)
    draw.line([(cx + 390, 145), (cx, 145)], fill=ARROW_COLOR, width=2)
    draw_arrow(draw, cx + 50, 145, cx, 145)

    out_path = os.path.abspath("fig_3_2_flowchart.png")
    img.save(out_path, quality=95)
    print("Saved Flowchart Diagram:", out_path)


# =============================================================================
# 3. COLLEGE CREST / HEADER LOGO
# =============================================================================
def generate_college_crest():
    w, h = 800, 200
    img = Image.new("RGB", (w, h), BG_WHITE)
    draw = ImageDraw.Draw(img)

    # Dark Box logo on left
    draw.rectangle([(20, 20), (160, 170)], fill=(35, 45, 60), outline=(20, 30, 45), width=2)
    draw.text((35, 35), "KCC", font=ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 36), fill=(255, 255, 255))
    draw.text((32, 90), "INSTITUTE", font=ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 15), fill=(210, 220, 235))
    draw.text((32, 110), "OF TECHNOLOGY", font=ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 11), fill=(180, 195, 215))
    draw.text((32, 126), "& MANAGEMENT", font=ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 11), fill=(180, 195, 215))
    draw.rectangle([(20, 150), (160, 170)], fill=(20, 25, 35))
    draw.text((35, 153), "GREATER NOIDA", font=ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 10), fill=(255, 255, 255))

    # Right side text
    draw.text((190, 35), "KCC INSTITUTE OF TECHNOLOGY & MANAGEMENT", font=ImageFont.truetype("C:/Windows/Fonts/timesbd.ttf", 20), fill=(20, 35, 60))
    draw.text((190, 68), "Approved by AICTE, Ministry of HRD, Govt. of India", font=ImageFont.truetype("C:/Windows/Fonts/timesi.ttf", 13), fill=(70, 70, 70))
    draw.text((190, 90), "Affiliated to Dr. A.P.J. Abdul Kalam Technical University (AKTU), Lucknow", font=ImageFont.truetype("C:/Windows/Fonts/times.ttf", 13), fill=(70, 70, 70))
    draw.text((190, 115), "College Code: 492 | Knowledge Park III, Greater Noida (U.P.) - 201306", font=ImageFont.truetype("C:/Windows/Fonts/timesbd.ttf", 13), fill=(30, 80, 140))
    draw.line([(190, 145), (780, 145)], fill=(30, 80, 140), width=2)

    out_path = os.path.abspath("fig_college_logo.png")
    img.save(out_path, quality=95)
    print("Saved College Crest:", out_path)


if __name__ == "__main__":
    generate_architecture_diagram()
    generate_flowchart_diagram()
    generate_college_crest()
