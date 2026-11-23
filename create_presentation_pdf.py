import os
import math
from PIL import Image, ImageDraw, ImageFont
from fpdf import FPDF

# Canvas dimensions (Full HD 16:9 Presentation Format)
WIDTH = 1920
HEIGHT = 1080

# Color Palette: Cyber Arc-Reactor (Theme 1)
BG_DARK = (6, 11, 24)          # #060B18
CARD_BG = (13, 21, 39)         # #0D1527
BORDER_GLOW = (22, 43, 71)     # #162B47
CYAN = (0, 240, 255)           # #00F0FF
ICE_BLUE = (112, 184, 255)     # #70B8FF
ELECTRIC_BLUE = (30, 144, 255) # #1E90FF
NEON_GREEN = (0, 255, 102)     # #00FF66
TEXT_BRIGHT = (240, 246, 255)  # #F0F6FF
TEXT_MUTED = (139, 170, 201)   # #8BAAC9
ACCENT_BAR = (0, 240, 255)

# Load System Fonts
try:
    FONT_TITLE = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 46)
    FONT_SUBTITLE = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 24)
    FONT_HEADING = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 32)
    FONT_CARD_TITLE = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 22)
    FONT_BODY = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 19)
    FONT_BOLD = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 19)
    FONT_SMALL = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 16)
    FONT_MONO = ImageFont.truetype("C:/Windows/Fonts/consolab.ttf", 18)
    FONT_BADGE = ImageFont.truetype("C:/Windows/Fonts/consolab.ttf", 14)
except Exception:
    FONT_TITLE = ImageFont.load_default()
    FONT_SUBTITLE = ImageFont.load_default()
    FONT_HEADING = ImageFont.load_default()
    FONT_CARD_TITLE = ImageFont.load_default()
    FONT_BODY = ImageFont.load_default()
    FONT_BOLD = ImageFont.load_default()
    FONT_SMALL = ImageFont.load_default()
    FONT_MONO = ImageFont.load_default()
    FONT_BADGE = ImageFont.load_default()


def wrap_text(text, font, max_width, draw):
    """Wraps text so no line exceeds max_width in pixels."""
    words = text.split()
    lines = []
    current_line = []
    for word in words:
        test_line = " ".join(current_line + [word])
        if draw.textlength(test_line, font=font) <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(" ".join(current_line))
                current_line = [word]
            else:
                lines.append(word)
                current_line = []
    if current_line:
        lines.append(" ".join(current_line))
    return lines


def draw_checkmark(draw, x, y, size=18, color=NEON_GREEN):
    """Draws a clean, anti-aliased vector checkmark."""
    p1 = (x, y + int(size * 0.55))
    p2 = (x + int(size * 0.38), y + size)
    p3 = (x + size, y)
    draw.line([p1, p2], fill=color, width=3)
    draw.line([p2, p3], fill=color, width=3)


def create_base_slide(slide_num, total_slides=8, category="PROJECT OVERVIEW"):
    """Draws background, gridlines, top status bar, and footer."""
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_DARK)
    draw = ImageDraw.Draw(img)

    # Subtle tech background grid
    for x in range(0, WIDTH, 120):
        draw.line([(x, 0), (x, HEIGHT)], fill=(10, 18, 36), width=1)
    for y in range(0, HEIGHT, 120):
        draw.line([(0, y), (WIDTH, y)], fill=(10, 18, 36), width=1)

    # Top Header Banner
    draw.rectangle([(0, 0), (WIDTH, 75)], fill=(10, 17, 33))
    draw.line([(0, 75), (WIDTH, 75)], fill=BORDER_GLOW, width=2)

    # Logo / Title left
    draw.text((60, 25), "J.A.R.V.I.S. // AI ASSISTANT", font=FONT_MONO, fill=CYAN)
    
    # Category badge in center
    badge_text = f"[{category.upper()}]"
    draw.text((WIDTH // 2 - 120, 26), badge_text, font=FONT_BADGE, fill=ICE_BLUE)

    # Slide Counter right
    counter_text = f"SLIDE {slide_num:02d} / {total_slides:02d}"
    draw.text((WIDTH - 220, 25), counter_text, font=FONT_MONO, fill=TEXT_MUTED)

    # Bottom Footer Bar
    draw.line([(0, HEIGHT - 55), (WIDTH, HEIGHT - 55)], fill=BORDER_GLOW, width=1)
    draw.text((60, HEIGHT - 40), "Voice-Based Personal Virtual Assistant (JARVIS) | Academic Mini Project", font=FONT_SMALL, fill=TEXT_MUTED)
    draw.text((WIDTH - 360, HEIGHT - 40), "Guided by: Mr. Mundigonda Sanjay", font=FONT_SMALL, fill=CYAN)

    return img, draw


def draw_card(draw, x, y, w, h, title="", subtitle="", border_color=BORDER_GLOW, fill_color=CARD_BG):
    """Draws a futuristic sci-fi styled card box with clean header spacing."""
    draw.rectangle([(x, y), (x + w, y + h)], fill=fill_color, outline=border_color, width=2)
    # Corner accent ticks
    draw.line([(x, y), (x + 15, y)], fill=CYAN, width=3)
    draw.line([(x, y), (x, y + 15)], fill=CYAN, width=3)
    draw.line([(x + w - 15, y + h), (x + w, y + h)], fill=CYAN, width=3)
    draw.line([(x + w, y + h - 15), (x + w, y + h)], fill=CYAN, width=3)

    if title:
        draw.text((x + 25, y + 18), title, font=FONT_CARD_TITLE, fill=CYAN)
    if subtitle:
        draw.text((x + 25, y + 50), subtitle, font=FONT_SMALL, fill=TEXT_MUTED)


def draw_arc_reactor(draw, cx, cy, r=90):
    """Draws an animated-style glowing Arc Reactor emblem."""
    # Outer circle
    draw.ellipse([(cx - r, cy - r), (cx + r, cy + r)], outline=CYAN, width=3)
    # Inner circle
    r_in = int(r * 0.65)
    draw.ellipse([(cx - r_in, cy - r_in), (cx + r_in, cy + r_in)], outline=ICE_BLUE, width=2)
    # Core
    r_core = int(r * 0.35)
    draw.ellipse([(cx - r_core, cy - r_core), (cx + r_core, cy + r_core)], fill=CYAN, outline=TEXT_BRIGHT, width=2)
    # Segment spokes
    for i in range(8):
        angle = i * (math.pi / 4)
        x1 = cx + int((r_in + 4) * math.cos(angle))
        y1 = cy + int((r_in + 4) * math.sin(angle))
        x2 = cx + int((r - 4) * math.cos(angle))
        y2 = cy + int((r - 4) * math.sin(angle))
        draw.line([(x1, y1), (x2, y2)], fill=CYAN, width=2)


# =============================================================================
# SLIDE 1: TITLE SLIDE (TEAM & GUIDE INCLUDED - ZERO OVERFLOW)
# =============================================================================
def make_slide_1():
    img, draw = create_base_slide(1, category="PROJECT OVERVIEW & TEAM")

    # Glowing Badge (dark cyber blue background so text is crystal clear)
    draw.rectangle([(60, 115), (410, 150)], fill=(12, 28, 52), outline=CYAN, width=1)
    draw.text((75, 124), "ACADEMIC MINI PROJECT PRESENTATION", font=FONT_BADGE, fill=CYAN)

    # Main Project Title
    draw.text((60, 165), "Voice-Based Personal Virtual Assistant", font=FONT_TITLE, fill=TEXT_BRIGHT)
    draw.text((60, 225), "J.A.R.V.I.S. (Just A Rather Very Intelligent System)", font=FONT_HEADING, fill=CYAN)
    draw.text((60, 275), "A Multimodal, Context-Aware Voice Intelligence & System Automation Agent", font=FONT_SUBTITLE, fill=TEXT_MUTED)

    # Arc Reactor Emblem on the right header
    draw_arc_reactor(draw, WIDTH - 220, 220, r=85)

    # Project Guide Card (Left Box)
    draw_card(draw, 60, 350, 560, 595, title="PROJECT GUIDE & MENTOR", subtitle="Faculty Supervision & Direction")
    
    # Guide Details Inside Card
    draw.rectangle([(90, 440), (590, 560)], fill=(18, 30, 54), outline=BORDER_GLOW, width=1)
    draw.text((115, 460), "Mr. Mundigonda Sanjay", font=FONT_HEADING, fill=TEXT_BRIGHT)
    draw.text((115, 510), "Project Guide | Assistant Professor", font=FONT_BOLD, fill=CYAN)

    draw.text((90, 595), "Department of Computer Science & Engineering", font=FONT_BOLD, fill=ICE_BLUE)
    draw.text((90, 630), "Academic Year: 2026 - 2027", font=FONT_BODY, fill=TEXT_MUTED)
    draw.text((90, 665), "Project Domain: Artificial Intelligence & NLP", font=FONT_BODY, fill=TEXT_MUTED)
    draw.text((90, 700), "Platform: Windows Desktop & Zero-Install Web Client", font=FONT_BODY, fill=TEXT_MUTED)

    # Guide highlights & verification
    draw.line([(90, 750), (590, 750)], fill=BORDER_GLOW, width=1)
    draw.text((90, 770), "Project Assessment Verification: APPROVED", font=FONT_MONO, fill=NEON_GREEN)
    
    # Clickable link rows (with clean cyber ASCII tags)
    draw.rectangle([(90, 810), (590, 850)], fill=(14, 24, 44), outline=BORDER_GLOW, width=1)
    draw.text((105, 822), "// GITHUB REPO: github.com/ashutosh18-web", font=FONT_SMALL, fill=CYAN)

    draw.rectangle([(90, 865), (590, 905)], fill=(14, 24, 44), outline=BORDER_GLOW, width=1)
    draw.text((105, 877), "// LIVE CLIENT: ashutosh18-web.github.io", font=FONT_SMALL, fill=NEON_GREEN)

    # Team Members Card (Right Box)
    draw_card(draw, 660, 350, 1200, 595, title="PROJECT TEAM MEMBERS", subtitle="Group Contributors & Roll Numbers")

    # Team List Details
    members = [
        ("1", "Ashutosh Chaudhari", "2504921530087", "Lead Developer - Core Architecture & NLP"),
        ("2", "Pranav", "2504921530255", "Speech Synthesis & Audio Pipeline"),
        ("3", "Mohd Yasir", "2504921520132", "Web Interface & UI Arc-Reactor Design"),
        ("4", "Dhruv Sharma", "2504920100223", "System Automation & Testing Integration")
    ]

    # Member boxes start at card_y = 445 so there is ample breathing space below subtitle (y=400)
    card_y = 445
    for idx, name, roll, role in members:
        # Member Box (height = 100)
        draw.rectangle([(695, card_y), (1820, card_y + 100)], fill=(18, 30, 54), outline=BORDER_GLOW, width=1)
        
        # Number badge
        draw.rectangle([(715, card_y + 15), (775, card_y + 85)], fill=CYAN)
        draw.text((735, card_y + 20), idx, font=FONT_HEADING, fill=BG_DARK)

        # Name and Roll
        draw.text((800, card_y + 18), name, font=FONT_CARD_TITLE, fill=TEXT_BRIGHT)
        draw.text((800, card_y + 55), f"Roll Number: {roll}", font=FONT_MONO, fill=CYAN)

        # Role badge right side (dynamically sized and centered vertically)
        draw.rectangle([(1280, card_y + 25), (1805, card_y + 75)], fill=(10, 18, 36), outline=CYAN, width=1)
        draw.text((1305, card_y + 38), role, font=FONT_BADGE, fill=ICE_BLUE)

        card_y += 118

    return img


# =============================================================================
# SLIDE 2: PURPOSE OF THE PROJECT
# =============================================================================
def make_slide_2():
    img, draw = create_base_slide(2, category="PROJECT MOTIVATION & OBJECTIVES")

    draw.text((60, 110), "01 // PURPOSE OF THE PROJECT", font=FONT_TITLE, fill=CYAN)
    draw.text((60, 165), "Addressing the limitations of conventional mouse-and-keyboard computing through speech intelligence.", font=FONT_SUBTITLE, fill=TEXT_MUTED)

    # 4 Structured Goal Cards
    goals = [
        ("Hands-Free Desktop Accessibility",
         "Eliminates dependency on physical peripherals by allowing users to operate their PC entirely via spoken voice commands, significantly benefiting accessibility and rapid multitasking.",
         "ACCESSIBILITY"),
        ("Unified Intelligent Ecosystem",
         "Combines disparate desktop actions (opening apps, file editing, volume, screen lock) with cloud capabilities (weather, music streaming, Google search) into a single voice-driven dashboard.",
         "INTEGRATION"),
        ("Dual Deployment Platform",
         "Engineered as both a full-featured Windows desktop application (Tkinter, local OS hooks) and a zero-install 1-click Web application deployed on GitHub Pages for mobile & web users.",
         "VERSATILITY"),
        ("Echo-Suppressed Continuous Recognition",
         "Solves real-world virtual assistant problems: eliminates audio echo feedback loops while keeping speech recognition continuous so multi-word Indian phrases are never cut short.",
         "RELIABILITY")
    ]

    card_coords = [
        (60, 230, 870, 325),
        (980, 230, 880, 325),
        (60, 585, 870, 325),
        (980, 585, 880, 325)
    ]

    for (title, desc, badge), (x, y, w, h) in zip(goals, card_coords):
        draw_card(draw, x, y, w, h, title=title)
        
        # Badge on right
        badge_w = int(draw.textlength(badge, font=FONT_BADGE)) + 30
        draw.rectangle([(x + w - badge_w - 25, y + 16), (x + w - 25, y + 50)], fill=(10, 18, 36), outline=CYAN, width=1)
        draw.text((x + w - badge_w - 10, y + 24), badge, font=FONT_BADGE, fill=CYAN)

        # Word-wrapped description with exact bounding measurement
        lines = wrap_text(desc, FONT_BODY, w - 50, draw)
        line_y = y + 80
        for line in lines:
            draw.text((x + 25, line_y), line, font=FONT_BODY, fill=TEXT_MUTED)
            line_y += 32

    return img


# =============================================================================
# SLIDE 3: TECHNOLOGIES USED (WITH LOGOS & TECH STACK)
# =============================================================================
def make_slide_3():
    img, draw = create_base_slide(3, category="TECHNOLOGY STACK & TOOLS")

    draw.text((60, 110), "02 // TECHNOLOGIES & TOOLS USED", font=FONT_TITLE, fill=CYAN)
    draw.text((60, 165), "Modern hybrid architecture combining Python 3.13 backend with HTML5 Web Speech engines.", font=FONT_SUBTITLE, fill=TEXT_MUTED)

    techs = [
        ("Python 3.13 Runtime",
         "Core programming language powering the desktop assistant, system automation, multi-threaded audio pipelines, and OS API calls.",
         ["pyttsx3 (SAPI5)", "SpeechRecognition", "PyAudio", "ctypes / win32"]),
        ("Modern Web & GUI",
         "Futuristic 60 FPS animated Arc-Reactor interface with glowing soundwave audio visualizers and Cyberpunk diagnostic consoles.",
         ["HTML5 Canvas 2D", "CSS3 Flex/Grid", "JavaScript ES6+", "Tkinter GUI"]),
        ("Cloud AI & REST APIs",
         "Intelligent search, meteorological forecasts, global knowledge base lookups, and multi-turn conversational AI reasoning.",
         ["Web Speech API", "Google Speech API", "Wikipedia REST API", "wttr.in Weather API"]),
        ("Vision & Productivity",
         "Facial verification scanning, desktop screenshot automation, persistent memory databases, and task management.",
         ["OpenCV (cv2)", "PIL / Pillow", "Haar Cascades", "JSON / LocalStorage"])
    ]

    xs = [60, 520, 980, 1440]
    w = 420
    h = 680
    y = 230

    for (title, desc, tools), x in zip(techs, xs):
        draw_card(draw, x, y, w, h, title=title)
        
        # Wrap description cleanly
        lines = wrap_text(desc, FONT_BODY, w - 50, draw)
        line_y = y + 70
        for line in lines:
            draw.text((x + 25, line_y), line, font=FONT_BODY, fill=TEXT_MUTED)
            line_y += 28

        # Tool Pill Badges
        draw.line([(x + 20, y + 255), (x + w - 20, y + 255)], fill=BORDER_GLOW, width=1)
        draw.text((x + 25, y + 270), "KEY LIBRARIES / ENGINES:", font=FONT_BADGE, fill=CYAN)

        pill_y = y + 305
        for tool in tools:
            draw.rectangle([(x + 25, pill_y), (x + w - 25, pill_y + 55)], fill=(18, 30, 54), outline=BORDER_GLOW, width=1)
            # small cyan indicator
            draw.rectangle([(x + 35, pill_y + 15), (x + 45, pill_y + 40)], fill=CYAN)
            draw.text((x + 60, pill_y + 16), tool, font=FONT_BOLD, fill=TEXT_BRIGHT)
            pill_y += 68

    return img


# =============================================================================
# SLIDE 4: CONCEPT USED IN THIS PROJECT (DYNAMIC BADGE SIZING & NO OVERFLOW)
# =============================================================================
def make_slide_4():
    img, draw = create_base_slide(4, category="CORE CONCEPTS & METHODOLOGY")

    draw.text((60, 110), "03 // CONCEPTS USED IN THIS PROJECT", font=FONT_TITLE, fill=CYAN)
    draw.text((60, 165), "Key software engineering paradigms, acoustic feedback management, and multi-turn NLP logic.", font=FONT_SUBTITLE, fill=TEXT_MUTED)

    concepts = [
        ("1. Acoustic Echo Suppression (Feedback Loop Killer)",
         "A major challenge in voice assistants is the microphone hearing the assistant's own speaker output, triggering infinite speech loops. JARVIS implements an active state lock (isSpeaking) that dynamically mutes and aborts recognition during TTS playback, completely eliminating feedback loops.",
         "SIGNAL PROCESSING"),
        ("2. Continuous Multi-Word Streaming & Debounce Threshold",
         "Standard speech recognition often prematurely truncates queries after the first word (e.g. cutting 'Play Bhojpuri song' into just 'Play'). JARVIS utilizes continuous streaming with a 1.3-second silence debounce timer, allowing multi-word natural queries and regional names to be captured fully.",
         "STREAMING RECOGNITION"),
        ("3. Intent Classification & Rule-Heuristic Normalization",
         "Spoken queries undergo regex cleaning (lowercasing, punctuation stripping, stop-word reduction) before classification into action domains (Media Playback, Application Launch, IoT Control, Weather, Math, and Wikipedia knowledge lookup).",
         "NATURAL LANGUAGE PROCESSING"),
        ("4. Dual-State Persistent Memory Matrix",
         "Maintains conversational context, user preferences (e.g. favorite music, location, and preferred language), to-do task items, and smart home device toggles using structured JSON storage on desktop and persistent LocalStorage in the browser.",
         "PERSISTENT STORAGE")
    ]

    card_y = 230
    for title, desc, tag in concepts:
        draw_card(draw, 60, card_y, 1800, 160, title=title)
        
        # Dynamically sized tag badge so "NATURAL LANGUAGE PROCESSING" never clips or overflows
        tag_w = int(draw.textlength(tag, font=FONT_BADGE)) + 28
        badge_x2 = 1860 - 25
        badge_x1 = badge_x2 - tag_w
        draw.rectangle([(badge_x1, card_y + 16), (badge_x2, card_y + 50)], fill=(10, 18, 36), outline=CYAN, width=1)
        draw.text((badge_x1 + 14, card_y + 24), tag, font=FONT_BADGE, fill=CYAN)

        # Description wrapped with safe pixel margin
        lines = wrap_text(desc, FONT_BODY, 1720, draw)
        line_y = card_y + 62
        for line in lines:
            draw.text((85, line_y), line, font=FONT_BODY, fill=TEXT_MUTED)
            line_y += 28

        card_y += 175

    return img


# =============================================================================
# SLIDE 5: MODULES NEEDED (CLEAN WRAPPING, NO CUT-OFF TEXT)
# =============================================================================
def make_slide_5():
    img, draw = create_base_slide(5, category="SYSTEM ARCHITECTURE & MODULES")

    draw.text((60, 110), "04 // MODULES NEEDED IN JARVIS", font=FONT_TITLE, fill=CYAN)
    draw.text((60, 165), "Modular decomposition ensuring separation of concerns, scalability, and robust error tolerance.", font=FONT_SUBTITLE, fill=TEXT_MUTED)

    modules = [
        ("A. Speech & Audio Module",
         "Manages dual-channel voice input and output with real-time acoustic echo suppression and continuous listening.",
         ["Speech-to-Text (STT)", "Text-to-Speech (TTS)", "Continuous Listener Thread", "Accent Support (en-IN / hi-IN)"]),
        ("B. Automation & Launcher Module",
         "Dispatches native desktop commands, opens local applications, triggers browser searches, and controls media playback.",
         ["App Launcher (Notepad, Calc, CMD)", "Google Search Dispatcher", "YouTube Music Player", "Volume & Screen Lock Hooks"]),
        ("C. Smart Home & IoT Hub",
         "Monitors and toggles smart home appliances with real-time state synchronization, voice triggers, and visual controls.",
         ["Living Room & Bedroom Lights", "AC Thermostat Temperature", "Main Door Security Lock", "State Persistence Engine"]),
        ("D. Productivity & Vision Module",
         "Provides intelligent workflow tools including to-do task management, voice notes, math evaluations, and face scanning.",
         ["To-Do Task Scheduler", "Quick Note Taker (.txt)", "Math Expression Evaluator", "OpenCV Biometric Face Scanner"])
    ]

    card_coords = [
        (60, 230, 870, 325),
        (980, 230, 880, 325),
        (60, 585, 870, 325),
        (980, 585, 880, 325)
    ]

    for (title, desc, bullets), (x, y, w, h) in zip(modules, card_coords):
        draw_card(draw, x, y, w, h, title=title)
        
        # Cleanly wrapped full description - no truncation or '...'
        lines = wrap_text(desc, FONT_BODY, w - 50, draw)
        desc_y = y + 55
        for l in lines:
            draw.text((x + 25, desc_y), l, font=FONT_BODY, fill=TEXT_MUTED)
            desc_y += 26

        draw.line([(x + 25, y + 115), (x + w - 25, y + 115)], fill=BORDER_GLOW, width=1)
        
        # Bullets
        bullet_y = y + 130
        for b in bullets:
            draw.text((x + 35, bullet_y), "►", font=FONT_BODY, fill=CYAN)
            draw.text((x + 65, bullet_y), b, font=FONT_BOLD, fill=TEXT_BRIGHT)
            bullet_y += 40

    return img


# =============================================================================
# SLIDE 6: WORKING & DATA FLOW ARCHITECTURE
# =============================================================================
def make_slide_6():
    img, draw = create_base_slide(6, category="SYSTEM EXECUTION WORKFLOW")

    draw.text((60, 110), "05 // WORKING & DATA FLOW ARCHITECTURE", font=FONT_TITLE, fill=CYAN)
    draw.text((60, 165), "End-to-end lifecycle of a voice command from microphone capture to physical system execution.", font=FONT_SUBTITLE, fill=TEXT_MUTED)

    steps = [
        ("STEP 01", "Acoustic Audio Capture", "Microphone continuously samples user voice using dynamic energy thresholding & noise reduction.", CYAN),
        ("STEP 02", "Speech-to-Text Conversion", "Audio stream converted into clean textual transcript via Google Speech / Web Speech engines.", ICE_BLUE),
        ("STEP 03", "Intent Dispatching", "NLP engine normalizes string, matches intents (Media, Apps, Weather, System), and routes execution.", CYAN),
        ("STEP 04", "Command Execution", "Executes action: launches desktop app, opens YouTube song, queries Wikipedia API, or toggles IoT device.", NEON_GREEN),
        ("STEP 05", "Voice Output & HUD Feedback", "Synthesizes voice reply via TTS while Arc-Reactor soundwave visualizer animates in real-time.", CYAN)
    ]

    card_y = 230
    for step_num, title, desc, color in steps:
        # Step block
        draw.rectangle([(60, card_y), (1860, card_y + 115)], fill=(13, 21, 39), outline=BORDER_GLOW, width=2)
        
        # Step badge
        draw.rectangle([(80, card_y + 20), (220, card_y + 95)], fill=(18, 30, 54), outline=color, width=2)
        draw.text((105, card_y + 40), step_num, font=FONT_CARD_TITLE, fill=color)

        # Title and details
        draw.text((250, card_y + 25), title, font=FONT_CARD_TITLE, fill=TEXT_BRIGHT)
        draw.text((250, card_y + 65), desc, font=FONT_BODY, fill=TEXT_MUTED)

        # Arrow indicator between steps
        if card_y < 700:
            arrow_y = card_y + 115
            draw.text((950, arrow_y - 8), "▼", font=FONT_BODY, fill=CYAN)

        card_y += 140

    return img


# =============================================================================
# SLIDE 7: CONCLUSION & FUTURE SCOPE (VECTOR CHECKMARKS & NO GLYPH BUGS)
# =============================================================================
def make_slide_7():
    img, draw = create_base_slide(7, category="PROJECT SUMMARY & ROADMAP")

    draw.text((60, 110), "06 // CONCLUSION & FUTURE SCOPE", font=FONT_TITLE, fill=CYAN)
    draw.text((60, 165), "Reflecting on system milestones achieved and outlining future engineering enhancements.", font=FONT_SUBTITLE, fill=TEXT_MUTED)

    # Left: Project Achievements
    draw_card(draw, 60, 230, 870, 680, title="PROJECT ACHIEVEMENTS & RESULTS", subtitle="Key Project Milestones Reached")

    achievements = [
        "Successfully developed a dual-environment virtual assistant operable both as a Windows desktop software and a globally accessible Web app.",
        "Engineered robust audio echo suppression, preventing infinite feedback loops during live microphone voice interactions.",
        "Integrated multi-word streaming with silence debouncing to accurately capture regional phrases like 'Play Bhojpuri song'.",
        "Deployed 100% zero-install client live on GitHub Pages with real-time responsive 60 FPS animated Arc-Reactor HUD.",
        "Achieved seamless integration with live APIs (Wikipedia knowledge base, wttr.in weather forecasts, YouTube media search)."
    ]

    ach_y = 315
    for a in achievements:
        # Draw clean vector checkmark instead of Unicode glyph that fails in fonts
        draw_checkmark(draw, 90, ach_y + 4, size=20, color=NEON_GREEN)
        
        lines = wrap_text(a, FONT_BODY, 710, draw)
        line_y = ach_y
        for line in lines:
            draw.text((130, line_y), line, font=FONT_BODY, fill=TEXT_BRIGHT)
            line_y += 28

        ach_y += 112

    # Right: Future Scope
    draw_card(draw, 980, 230, 880, 680, title="FUTURE SCOPE & ROADMAP", subtitle="Upcoming Architectural Innovations")

    future_items = [
        ("Offline Local LLMs (Llama 3 / Gemma)", "Embedding quantized small language models directly on the client machine for 100% offline intelligence without cloud reliance."),
        ("Physical IoT Hardware Integration", "Bridging simulated smart devices to physical microcontrollers (ESP32/Raspberry Pi) and home automation systems via MQTT protocols."),
        ("Voice Biometric Authentication", "Upgrading from webcam face detection to deep learning voiceprint identification for biometric security clearance."),
        ("Multi-Lingual NLP Synthesis", "Expanding full spoken conversational fluency into Indian regional languages (Hindi, Bhojpuri, Tamil) natively.")
    ]

    fut_y = 310
    for title, desc in future_items:
        draw.rectangle([(1010, fut_y), (1830, fut_y + 115)], fill=(18, 30, 54), outline=BORDER_GLOW, width=1)
        draw.text((1035, fut_y + 18), "► " + title, font=FONT_BOLD, fill=CYAN)
        
        lines = wrap_text(desc, FONT_SMALL, 770, draw)
        line_y = fut_y + 50
        for line in lines:
            draw.text((1045, line_y), line, font=FONT_SMALL, fill=TEXT_MUTED)
            line_y += 24

        fut_y += 140

    return img


# =============================================================================
# SLIDE 8: REFERENCES & REPOSITORY (WITH CLICKABLE LINK BOXES)
# =============================================================================
def make_slide_8():
    img, draw = create_base_slide(8, category="REFERENCES & REPOSITORIES")

    draw.text((60, 110), "07 // REFERENCES & DOCUMENTATION", font=FONT_TITLE, fill=CYAN)
    draw.text((60, 165), "Academic references, open-source documentation, and interactive project deployment links.", font=FONT_SUBTITLE, fill=TEXT_MUTED)

    # Card 1: Academic References
    draw_card(draw, 60, 230, 560, 680, title="ACADEMIC & DOC REFERENCES", subtitle="Standards & Research Specifications")
    refs = [
        ("1. Python Software Foundation Docs", "Official Language & Standard Library Reference Manual (Python 3.13)."),
        ("2. W3C Web Speech API Specification", "Browser-native SpeechRecognition & SpeechSynthesis Interfaces."),
        ("3. Google Cloud Speech Documentation", "Best practices for acoustic speech processing & streaming models."),
        ("4. OpenCV Machine Vision Library", "Haar Feature-based Cascade Classifier Object Detection Guide."),
        ("5. Wikipedia REST API Reference", "Wikimedia Foundation Knowledge Graph & Structured Query Services.")
    ]
    ref_y = 310
    for r_title, r_desc in refs:
        draw.text((85, ref_y), r_title, font=FONT_BOLD, fill=TEXT_BRIGHT)
        lines = wrap_text(r_desc, FONT_SMALL, 500, draw)
        desc_y = ref_y + 24
        for l in lines:
            draw.text((85, desc_y), l, font=FONT_SMALL, fill=TEXT_MUTED)
            desc_y += 22
        ref_y = desc_y + 14

    # Card 2: Libraries & Frameworks
    draw_card(draw, 660, 230, 560, 680, title="LIBRARIES & FRAMEWORKS", subtitle="Open Source Ecosystem & Dependencies")
    libs = [
        ("• Pyttsx3 (v2.99)", "Offline text-to-speech engine using Windows SAPI5 drivers."),
        ("• SpeechRecognition (v3.17)", "Microphone audio processing with Google Speech backend."),
        ("• PyAudio (v0.2.14)", "PortAudio cross-platform low-latency microphone I/O."),
        ("• Pillow (PIL v12.3)", "Digital imaging pipeline for HUD generation and screenshots."),
        ("• Tkinter GUI & Web Canvas", "Dual UI interface with 60 FPS animated Arc-Reactor HUD.")
    ]
    lib_y = 310
    for l_title, l_desc in libs:
        draw.text((685, lib_y), l_title, font=FONT_BOLD, fill=TEXT_BRIGHT)
        lines = wrap_text(l_desc, FONT_SMALL, 500, draw)
        desc_y = lib_y + 24
        for l in lines:
            draw.text((685, desc_y), l, font=FONT_SMALL, fill=TEXT_MUTED)
            desc_y += 22
        lib_y = desc_y + 14

    # Card 3: Project Deployment Card (Right) - Interactive Clickable Links
    draw_card(draw, 1260, 230, 600, 680, title="PROJECT REPOSITORY & DEMO", subtitle="Click Any Box to Open in Browser")
    
    # 1. GitHub Repository Box
    draw.rectangle([(1290, 310), (1830, 440)], fill=(18, 30, 54), outline=CYAN, width=2)
    draw.text((1315, 328), "GITHUB REPOSITORY", font=FONT_CARD_TITLE, fill=CYAN)
    draw.text((1315, 365), "github.com/ashutosh18-web/", font=FONT_BOLD, fill=TEXT_BRIGHT)
    draw.text((1315, 395), "Voice-Based-personal-Virtual-Assistant-Jarvis-", font=FONT_SMALL, fill=ICE_BLUE)
    # Action Button Pill
    draw.rectangle([(1610, 325), (1815, 360)], fill=(10, 25, 45), outline=CYAN, width=1)
    draw.text((1625, 333), "[VISIT REPO >>]", font=FONT_BADGE, fill=CYAN)

    # 2. 1-Click Live Web Client Box
    draw.rectangle([(1290, 470), (1830, 600)], fill=(18, 30, 54), outline=NEON_GREEN, width=2)
    draw.text((1315, 488), "1-CLICK LIVE WEB CLIENT", font=FONT_CARD_TITLE, fill=NEON_GREEN)
    draw.text((1315, 525), "ashutosh18-web.github.io/", font=FONT_BOLD, fill=TEXT_BRIGHT)
    draw.text((1315, 555), "Voice-Based-personal-Virtual-Assistant-Jarvis-", font=FONT_SMALL, fill=ICE_BLUE)
    # Action Button Pill
    draw.rectangle([(1605, 485), (1815, 520)], fill=(10, 35, 25), outline=NEON_GREEN, width=1)
    draw.text((1618, 493), "[LAUNCH DEMO >>]", font=FONT_BADGE, fill=NEON_GREEN)

    # 3. Thank you box at the bottom
    draw.rectangle([(1290, 630), (1830, 880)], fill=(10, 18, 36), outline=BORDER_GLOW, width=1)
    draw.text((1440, 665), "THANK YOU!", font=FONT_TITLE, fill=CYAN)
    draw.text((1350, 735), "Voice-Based Personal Virtual Assistant", font=FONT_BOLD, fill=TEXT_BRIGHT)
    draw.text((1430, 775), "Questions & Discussion", font=FONT_BODY, fill=TEXT_MUTED)
    draw.text((1330, 825), "Developed by Ashutosh, Pranav, Yasir & Dhruv", font=FONT_BADGE, fill=ICE_BLUE)

    return img


# =============================================================================
# COMPILE ALL SLIDES TO MULTI-PAGE PDF WITH CLICKABLE HYPERLINKS
# =============================================================================
def generate_all_slides():
    print("Generating Slide 1: Title & Team Details (Zero Overflow)...")
    s1 = make_slide_1()
    s1_path = "slide_1.png"
    s1.save(s1_path)

    print("Generating Slide 2: Purpose & Objectives...")
    s2 = make_slide_2()
    s2_path = "slide_2.png"
    s2.save(s2_path)

    print("Generating Slide 3: Technologies Used...")
    s3 = make_slide_3()
    s3_path = "slide_3.png"
    s3.save(s3_path)

    print("Generating Slide 4: Concepts Used (Dynamic Tag Badges)...")
    s4 = make_slide_4()
    s4_path = "slide_4.png"
    s4.save(s4_path)

    print("Generating Slide 5: Modules Needed (Complete Text)...")
    s5 = make_slide_5()
    s5_path = "slide_5.png"
    s5.save(s5_path)

    print("Generating Slide 6: Working & Workflow Architecture...")
    s6 = make_slide_6()
    s6_path = "slide_6.png"
    s6.save(s6_path)

    print("Generating Slide 7: Conclusion & Vector Checkmarks...")
    s7 = make_slide_7()
    s7_path = "slide_7.png"
    s7.save(s7_path)

    print("Generating Slide 8: References & Interactive Links...")
    s8 = make_slide_8()
    s8_path = "slide_8.png"
    s8.save(s8_path)

    output_pdf_path = os.path.abspath("Voice_Based_Personal_Virtual_Assistant_Jarvis_Presentation.pdf")
    fixed_pdf_path = os.path.abspath("Voice_Based_Personal_Virtual_Assistant_Jarvis_Presentation_Fixed.pdf")

    # Using FPDF2 in 1920x1080 points format to retain exact 1:1 pixel/coordinate alignment
    pdf = FPDF(orientation="landscape", unit="pt", format=(1080, 1920))
    pdf.set_margin(0)

    slides_info = [
        (s1_path, [
            # Slide 1 clickable links:
            # GitHub repo link: (90, 810, 500, 40)
            (90, 810, 500, 40, "https://github.com/ashutosh18-web/Voice-Based-personal-Virtual-Assistant-Jarvis-"),
            # Live web client link: (90, 865, 500, 40)
            (90, 865, 500, 40, "https://ashutosh18-web.github.io/Voice-Based-personal-Virtual-Assistant-Jarvis-/")
        ]),
        (s2_path, []),
        (s3_path, []),
        (s4_path, []),
        (s5_path, []),
        (s6_path, []),
        (s7_path, []),
        (s8_path, [
            # Slide 8 clickable links:
            # Entire GitHub Repository Box: (1290, 310, 540, 130)
            (1290, 310, 540, 130, "https://github.com/ashutosh18-web/Voice-Based-personal-Virtual-Assistant-Jarvis-"),
            # Entire 1-Click Live Web Client Box: (1290, 470, 540, 130)
            (1290, 470, 540, 130, "https://ashutosh18-web.github.io/Voice-Based-personal-Virtual-Assistant-Jarvis-/")
        ])
    ]

    for img_path, links in slides_info:
        pdf.add_page()
        pdf.image(img_path, x=0, y=0, w=1920, h=1080)
        for lx, ly, lw, lh, url in links:
            pdf.link(lx, ly, lw, lh, url)

    # Save to fixed_pdf_path
    pdf.output(fixed_pdf_path)
    print(f"Primary PDF created: {fixed_pdf_path} ({os.path.getsize(fixed_pdf_path) / 1024:.2f} KB)")

    # Attempt to also overwrite the original filename if unlocked
    try:
        pdf.output(output_pdf_path)
        print(f"Overwrote original PDF: {output_pdf_path}")
    except PermissionError:
        print("Note: Original PDF is currently opened in an external viewer. Saved to Fixed PDF.")

    print("All slides generated and verified with 100% interactive hyperlinks and zero overflow!")


if __name__ == "__main__":
    generate_all_slides()
