import os
import math
from PIL import Image, ImageDraw, ImageFont
from fpdf import FPDF

# Canvas dimensions (Full HD 16:9 Presentation Format)
WIDTH = 1920
HEIGHT = 1080

# =============================================================================
# COLOR PALETTE: THEME 2 - CRIMSON NOIR (#02060E & #C50337)
# =============================================================================
BG_NOIR = (4, 8, 16)            # #040810 Deep obsidian noir
BG_CARD = (15, 19, 29)          # #0F131D Sleek dark card container
BG_INNER_BOX = (22, 26, 38)     # #161A26 Card sub-box fill
CARD_BORDER = (55, 18, 30)      # #37121E Subtle dark crimson border
CARD_BORDER_LIGHT = (85, 25, 42) # #55192A Visible crimson border
CRIMSON = (197, 3, 55)          # #C50337 Signature vivid crimson red
CRIMSON_BRIGHT = (235, 30, 80)  # #EB1E50 Vibrant highlight crimson
CRIMSON_DEEP = (90, 8, 28)      # #5A081C Wine red ambient curve
TEXT_WHITE = (255, 255, 255)    # #FFFFFF Pure crisp white
TEXT_BODY = (215, 220, 230)     # #D7DCE6 Clean legible light grey
TEXT_MUTED = (145, 155, 170)    # #919BAA Slate grey
TEXT_ROSE = (255, 120, 145)     # #FF7891 Elegant soft rose/crimson accent
ACCENT_GREEN = (39, 174, 96)    # Green for approvals & status

# Load System Fonts
try:
    FONT_TITLE = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 44)
    FONT_SUBTITLE = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 22)
    FONT_HEADING = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 30)
    FONT_CARD_TITLE = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 22)
    FONT_BODY = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 18)
    FONT_BOLD = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 18)
    FONT_SMALL = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 15)
    FONT_MONO = ImageFont.truetype("C:/Windows/Fonts/consolab.ttf", 17)
    FONT_BADGE = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 13)
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


def draw_checkmark(draw, x, y, size=18, color=CRIMSON_BRIGHT):
    """Draws a clean, anti-aliased vector checkmark."""
    p1 = (x, y + int(size * 0.55))
    p2 = (x + int(size * 0.38), y + size)
    p3 = (x + size, y)
    draw.line([p1, p2], fill=color, width=3)
    draw.line([p2, p3], fill=color, width=3)


def create_base_slide(slide_num, total_slides=8, category="PROJECT OVERVIEW"):
    """Draws Crimson Noir background, ambient curves, status bar, and footer."""
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_NOIR)
    draw = ImageDraw.Draw(img)

    # Ambient Crimson curves in corners
    # Top right crimson arc/glow
    for r in range(450, 0, -10):
        c = (int(BG_NOIR[0] + (CRIMSON_DEEP[0] - BG_NOIR[0]) * (1 - r / 450)),
             int(BG_NOIR[1] + (CRIMSON_DEEP[1] - BG_NOIR[1]) * (1 - r / 450)),
             int(BG_NOIR[2] + (CRIMSON_DEEP[2] - BG_NOIR[2]) * (1 - r / 450)))
        draw.ellipse([(WIDTH - 100 - r, -100 - r), (WIDTH - 100 + r, -100 + r)], fill=c)

    # Bottom left subtle crimson arc
    for r in range(350, 0, -10):
        c = (int(BG_NOIR[0] + (CRIMSON[0] - BG_NOIR[0]) * 0.25 * (1 - r / 350)),
             int(BG_NOIR[1] + (CRIMSON[1] - BG_NOIR[1]) * 0.08 * (1 - r / 350)),
             int(BG_NOIR[2] + (CRIMSON[2] - BG_NOIR[2]) * 0.15 * (1 - r / 350)))
        draw.ellipse([(-100 - r, HEIGHT - 50 - r), (-100 + r, HEIGHT - 50 + r)], fill=c)

    # Top Header Rule
    draw.line([(0, 68), (WIDTH, 68)], fill=(40, 15, 25), width=1)
    draw.line([(60, 68), (220, 68)], fill=CRIMSON, width=3) # Crimson accent notch

    # Top Brand / Header details
    draw.text((60, 24), "KCC INSTITUTE OF TECHNOLOGY & MANAGEMENT", font=FONT_BADGE, fill=CRIMSON_BRIGHT)
    
    # Category badge in center
    badge_text = category.upper()
    draw.text((WIDTH // 2 - int(draw.textlength(badge_text, font=FONT_BADGE)) // 2, 24), badge_text, font=FONT_BADGE, fill=TEXT_MUTED)

    # Slide Counter right
    counter_text = f"SLIDE {slide_num:02d} / {total_slides:02d}"
    draw.text((WIDTH - 180, 24), counter_text, font=FONT_BADGE, fill=TEXT_MUTED)

    # Bottom Footer Bar
    draw.line([(0, HEIGHT - 45), (WIDTH, HEIGHT - 45)], fill=CARD_BORDER, width=1)
    draw.text((60, HEIGHT - 32), "Voice-Based Personal Virtual Assistant (JARVIS) | Academic Mini Project 2026-2027", font=FONT_SMALL, fill=TEXT_MUTED)
    draw.text((WIDTH - 380, HEIGHT - 32), "Department of Computer Science & Engineering", font=FONT_SMALL, fill=CRIMSON_BRIGHT)

    return img, draw


def draw_noir_card(draw, x, y, w, h, title="", subtitle="", border_color=CARD_BORDER, fill_color=BG_CARD):
    """Draws an executive Crimson Noir styled card box with top accent bar."""
    draw.rounded_rectangle([(x, y), (x + w, y + h)], radius=12, fill=fill_color, outline=border_color, width=2)
    # Top Crimson accent bar
    draw.rounded_rectangle([(x, y), (x + w, y + 5)], radius=3, fill=CRIMSON)

    if title:
        draw.text((x + 28, y + 22), title, font=FONT_CARD_TITLE, fill=TEXT_WHITE)
    if subtitle:
        draw.text((x + 28, y + 54), subtitle, font=FONT_SMALL, fill=TEXT_ROSE)


# =============================================================================
# SLIDE 1: TITLE SLIDE (TEAM & GUIDE INCLUDED - CRIMSON NOIR)
# =============================================================================
def make_slide_1():
    img, draw = create_base_slide(1, category="PROJECT OVERVIEW & TEAM")

    # Dot matrix decoration (like in reference image)
    for row in range(3):
        for col in range(5):
            draw.ellipse([(60 + col * 12, 108 + row * 12), (60 + col * 12 + 3, 108 + row * 12 + 3)], fill=CRIMSON)

    # Pill category
    draw.rounded_rectangle([(140, 108), (380, 140)], radius=16, fill=(40, 12, 22), outline=CRIMSON, width=1)
    draw.text((158, 115), "AI & SPEECH RECOGNITION", font=FONT_BADGE, fill=TEXT_WHITE)

    # Main Project Title
    draw.text((60, 158), "Voice-Based Personal Virtual Assistant", font=FONT_TITLE, fill=TEXT_WHITE)
    draw.text((60, 220), "Project JARVIS (Just A Rather Very Intelligent System)", font=FONT_HEADING, fill=CRIMSON_BRIGHT)
    draw.text((60, 270), "A Context-Aware, Hands-Free Intelligent Assistant & Operating System Automation Agent", font=FONT_SUBTITLE, fill=TEXT_MUTED)

    # Right Header: Official KCC Logo
    if os.path.exists("kcc_official_logo.png"):
        kcc = Image.open("kcc_official_logo.png")
        if kcc.mode == "RGBA":
            bg = Image.new("RGB", kcc.size, BG_CARD)
            bg.paste(kcc, mask=kcc.split()[3])
            kcc = bg
        kcc_w = 110
        kcc_h = int(kcc_w * (kcc.height / kcc.width))
        kcc_res = kcc.resize((kcc_w, kcc_h), Image.Resampling.LANCZOS)
        img.paste(kcc_res, (WIDTH - 190, 135))
        draw.rectangle([(WIDTH - 192, 133), (WIDTH - 192 + kcc_w + 4, 133 + kcc_h + 4)], outline=CRIMSON, width=1)

    # Card 1: Project Guide Card (Left Box)
    draw_noir_card(draw, 60, 345, 560, 595, title="PROJECT GUIDE & MENTOR", subtitle="Department Faculty Supervision")
    
    # Guide Details Inside Card
    draw.rounded_rectangle([(90, 440), (590, 560)], radius=8, fill=BG_INNER_BOX, outline=(50, 20, 32), width=1)
    draw.text((115, 460), "Mr. Mundigonda Sanjay", font=FONT_HEADING, fill=TEXT_WHITE)
    draw.text((115, 510), "Assistant Professor | Project Guide", font=FONT_BOLD, fill=CRIMSON_BRIGHT)

    draw.text((90, 595), "Department of Computer Science & Engineering", font=FONT_BOLD, fill=TEXT_WHITE)
    draw.text((90, 630), "Academic Session: 2026 – 2027", font=FONT_BODY, fill=TEXT_MUTED)
    draw.text((90, 665), "College Code: 492 | KCC ITM, Greater Noida", font=FONT_BODY, fill=TEXT_MUTED)
    draw.text((90, 700), "Project Domain: Artificial Intelligence & NLP", font=FONT_BODY, fill=TEXT_MUTED)

    # Guide highlights & verification
    draw.line([(90, 750), (590, 750)], fill=CARD_BORDER, width=1)
    draw.text((90, 770), "Assessment Status: APPROVED", font=FONT_BOLD, fill=ACCENT_GREEN)
    
    # Clickable link rows
    draw.rounded_rectangle([(90, 810), (590, 852)], radius=6, fill=BG_INNER_BOX, outline=CRIMSON, width=1)
    draw.text((105, 822), "// GITHUB REPO : github.com/ashutosh18-web", font=FONT_SMALL, fill=TEXT_WHITE)

    draw.rounded_rectangle([(90, 868), (590, 910)], radius=6, fill=BG_INNER_BOX, outline=CARD_BORDER, width=1)
    draw.text((105, 880), "// LIVE DEMO   : ashutosh18-web.github.io", font=FONT_SMALL, fill=TEXT_ROSE)

    # Card 2: Team Members Card (Right Box)
    draw_noir_card(draw, 660, 345, 1200, 595, title="PROJECT TEAM MEMBERS", subtitle="Group Contributors & Roll Numbers")

    # Team List Details
    members = [
        ("1", "Ashutosh Chaudhari", "2504921530087", "Lead Developer – Core Architecture & NLP"),
        ("2", "Pranav", "2504921530255", "Speech Synthesis & Audio Processing Pipeline"),
        ("3", "Mohd Yasir", "2504921520132", "Web Interface & UI Visualizer Design"),
        ("4", "Dhruv Sharma", "2504920100223", "System Automation & Integration Testing")
    ]

    card_y = 445
    for idx, name, roll, role in members:
        draw.rounded_rectangle([(695, card_y), (1825, card_y + 102)], radius=8, fill=BG_INNER_BOX, outline=(50, 20, 32), width=1)
        
        # Crimson Badge
        draw.rounded_rectangle([(715, card_y + 16), (775, card_y + 86)], radius=6, fill=CRIMSON)
        draw.text((735, card_y + 24), idx, font=FONT_HEADING, fill=TEXT_WHITE)

        # Name and Roll
        draw.text((800, card_y + 20), name, font=FONT_CARD_TITLE, fill=TEXT_WHITE)
        draw.text((800, card_y + 58), f"Roll Number: {roll}", font=FONT_BODY, fill=CRIMSON_BRIGHT)

        # Role badge right side
        draw.rounded_rectangle([(1270, card_y + 28), (1805, card_y + 74)], radius=6, fill=(18, 22, 32), outline=CRIMSON, width=1)
        draw.text((1295, card_y + 40), role, font=FONT_BADGE, fill=TEXT_ROSE)

        card_y += 120

    return img


# =============================================================================
# SLIDE 2: PURPOSE OF THE PROJECT (CRIMSON NOIR)
# =============================================================================
def make_slide_2():
    img, draw = create_base_slide(2, category="PROJECT MOTIVATION & OBJECTIVES")

    draw.text((60, 105), "01 // PURPOSE OF THE PROJECT", font=FONT_TITLE, fill=TEXT_WHITE)
    draw.text((60, 160), "Addressing the limitations of conventional mouse-and-keyboard computing through touchless speech intelligence.", font=FONT_SUBTITLE, fill=TEXT_MUTED)

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
        (60, 225, 870, 330),
        (980, 225, 880, 330),
        (60, 580, 870, 330),
        (980, 580, 880, 330)
    ]

    for (title, desc, badge), (x, y, w, h) in zip(goals, card_coords):
        draw_noir_card(draw, x, y, w, h, title=title)
        
        # Badge on right
        badge_w = int(draw.textlength(badge, font=FONT_BADGE)) + 26
        draw.rounded_rectangle([(x + w - badge_w - 25, y + 16), (x + w - 25, y + 48)], radius=14, fill=(40, 12, 22), outline=CRIMSON, width=1)
        draw.text((x + w - badge_w - 12, y + 24), badge, font=FONT_BADGE, fill=TEXT_ROSE)

        # Word-wrapped description
        lines = wrap_text(desc, FONT_BODY, w - 50, draw)
        line_y = y + 78
        for line in lines:
            draw.text((x + 28, line_y), line, font=FONT_BODY, fill=TEXT_BODY)
            line_y += 32

    return img


# =============================================================================
# SLIDE 3: TECHNOLOGIES USED (CRIMSON NOIR)
# =============================================================================
def make_slide_3():
    img, draw = create_base_slide(3, category="TECHNOLOGY STACK & TOOLS")

    draw.text((60, 105), "02 // TECHNOLOGIES & TOOLS USED", font=FONT_TITLE, fill=TEXT_WHITE)
    draw.text((60, 160), "Modern hybrid architecture combining Python 3.13 backend with HTML5 Web Speech engines.", font=FONT_SUBTITLE, fill=TEXT_MUTED)

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
    h = 685
    y = 225

    for (title, desc, tools), x in zip(techs, xs):
        draw_noir_card(draw, x, y, w, h, title=title)
        
        # Description
        lines = wrap_text(desc, FONT_BODY, w - 50, draw)
        line_y = y + 68
        for line in lines:
            draw.text((x + 25, line_y), line, font=FONT_BODY, fill=TEXT_MUTED)
            line_y += 28

        # Tool Pill Badges
        draw.line([(x + 20, y + 255), (x + w - 20, y + 255)], fill=CARD_BORDER, width=1)
        draw.text((x + 25, y + 270), "CORE LIBRARIES / ENGINES:", font=FONT_BADGE, fill=CRIMSON_BRIGHT)

        pill_y = y + 305
        for tool in tools:
            draw.rounded_rectangle([(x + 25, pill_y), (x + w - 25, pill_y + 55)], radius=6, fill=BG_INNER_BOX, outline=CARD_BORDER, width=1)
            # Crimson indicator tick
            draw.rounded_rectangle([(x + 35, pill_y + 14), (x + 45, pill_y + 41)], radius=2, fill=CRIMSON)
            draw.text((x + 60, pill_y + 16), tool, font=FONT_BOLD, fill=TEXT_WHITE)
            pill_y += 68

    return img


# =============================================================================
# SLIDE 4: CONCEPT USED IN THIS PROJECT (CRIMSON NOIR)
# =============================================================================
def make_slide_4():
    img, draw = create_base_slide(4, category="CORE CONCEPTS & METHODOLOGY")

    draw.text((60, 105), "03 // CONCEPTS USED IN THIS PROJECT", font=FONT_TITLE, fill=TEXT_WHITE)
    draw.text((60, 160), "Key software engineering paradigms, acoustic feedback management, and multi-turn NLP logic.", font=FONT_SUBTITLE, fill=TEXT_MUTED)

    concepts = [
        ("1. Acoustic Echo Suppression (Feedback Loop Barrier)",
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

    card_y = 225
    for title, desc, tag in concepts:
        draw_noir_card(draw, 60, card_y, 1800, 160, title=title)
        
        # Dynamically sized tag badge
        tag_w = int(draw.textlength(tag, font=FONT_BADGE)) + 26
        badge_x2 = 1860 - 25
        badge_x1 = badge_x2 - tag_w
        draw.rounded_rectangle([(badge_x1, card_y + 16), (badge_x2, card_y + 48)], radius=14, fill=(40, 12, 22), outline=CRIMSON, width=1)
        draw.text((badge_x1 + 13, card_y + 24), tag, font=FONT_BADGE, fill=TEXT_ROSE)

        # Description wrapped
        lines = wrap_text(desc, FONT_BODY, 1720, draw)
        line_y = card_y + 62
        for line in lines:
            draw.text((88, line_y), line, font=FONT_BODY, fill=TEXT_BODY)
            line_y += 28

        card_y += 175

    return img


# =============================================================================
# SLIDE 5: MODULES NEEDED (CRIMSON NOIR)
# =============================================================================
def make_slide_5():
    img, draw = create_base_slide(5, category="SYSTEM ARCHITECTURE & MODULES")

    draw.text((60, 105), "04 // MODULES NEEDED IN JARVIS", font=FONT_TITLE, fill=TEXT_WHITE)
    draw.text((60, 160), "Modular decomposition ensuring separation of concerns, scalability, and robust error tolerance.", font=FONT_SUBTITLE, fill=TEXT_MUTED)

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
        (60, 225, 870, 330),
        (980, 225, 880, 330),
        (60, 580, 870, 330),
        (980, 580, 880, 330)
    ]

    for (title, desc, bullets), (x, y, w, h) in zip(modules, card_coords):
        draw_noir_card(draw, x, y, w, h, title=title)
        
        # Clean description
        lines = wrap_text(desc, FONT_BODY, w - 50, draw)
        desc_y = y + 54
        for l in lines:
            draw.text((x + 28, desc_y), l, font=FONT_BODY, fill=TEXT_MUTED)
            desc_y += 26

        draw.line([(x + 25, y + 115), (x + w - 25, y + 115)], fill=CARD_BORDER, width=1)
        
        # Bullets
        bullet_y = y + 130
        for b in bullets:
            draw.text((x + 35, bullet_y), "►", font=FONT_BODY, fill=CRIMSON_BRIGHT)
            draw.text((x + 65, bullet_y), b, font=FONT_BOLD, fill=TEXT_WHITE)
            bullet_y += 40

    return img


# =============================================================================
# SLIDE 6: WORKING & DATA FLOW ARCHITECTURE (CRIMSON NOIR)
# =============================================================================
def make_slide_6():
    img, draw = create_base_slide(6, category="SYSTEM EXECUTION WORKFLOW")

    draw.text((60, 105), "05 // WORKING & DATA FLOW ARCHITECTURE", font=FONT_TITLE, fill=TEXT_WHITE)
    draw.text((60, 160), "End-to-end lifecycle of a voice command from microphone capture to physical system execution.", font=FONT_SUBTITLE, fill=TEXT_MUTED)

    steps = [
        ("STEP 01", "Acoustic Audio Capture", "Microphone continuously samples user voice using dynamic energy thresholding & noise reduction.", CRIMSON),
        ("STEP 02", "Speech-to-Text Conversion", "Audio stream converted into clean textual transcript via Google Speech / Web Speech engines.", CRIMSON_BRIGHT),
        ("STEP 03", "Intent Dispatching", "NLP engine normalizes string, matches intents (Media, Apps, Weather, System), and routes execution.", CRIMSON),
        ("STEP 04", "Command Execution", "Executes action: launches desktop app, opens YouTube song, queries Wikipedia API, or toggles IoT device.", ACCENT_GREEN),
        ("STEP 05", "Voice Output & HUD Feedback", "Synthesizes voice reply via TTS while Arc-Reactor soundwave visualizer animates in real-time.", CRIMSON_BRIGHT)
    ]

    card_y = 225
    for step_num, title, desc, color in steps:
        # Step block
        draw.rounded_rectangle([(60, card_y), (1860, card_y + 118)], radius=10, fill=BG_CARD, outline=CARD_BORDER, width=2)
        # Left accent stripe
        draw.rounded_rectangle([(60, card_y), (66, card_y + 118)], radius=2, fill=color)

        # Step badge
        draw.rounded_rectangle([(85, card_y + 20), (225, card_y + 98)], radius=6, fill=BG_INNER_BOX, outline=color, width=2)
        draw.text((110, card_y + 42), step_num, font=FONT_CARD_TITLE, fill=color)

        # Title and details
        draw.text((255, card_y + 25), title, font=FONT_CARD_TITLE, fill=TEXT_WHITE)
        draw.text((255, card_y + 68), desc, font=FONT_BODY, fill=TEXT_BODY)

        # Arrow indicator between steps
        if card_y < 700:
            arrow_y = card_y + 118
            draw.text((950, arrow_y - 6), "▼", font=FONT_BODY, fill=CRIMSON_BRIGHT)

        card_y += 140

    return img


# =============================================================================
# SLIDE 7: CONCLUSION & FUTURE SCOPE (CRIMSON NOIR)
# =============================================================================
def make_slide_7():
    img, draw = create_base_slide(7, category="PROJECT SUMMARY & ROADMAP")

    draw.text((60, 105), "06 // CONCLUSION & FUTURE SCOPE", font=FONT_TITLE, fill=TEXT_WHITE)
    draw.text((60, 160), "Reflecting on system milestones achieved and outlining future engineering enhancements.", font=FONT_SUBTITLE, fill=TEXT_MUTED)

    # Left: Project Achievements
    draw_noir_card(draw, 60, 225, 870, 685, title="PROJECT ACHIEVEMENTS & RESULTS", subtitle="Key Project Milestones Reached")

    achievements = [
        "Successfully developed a dual-environment virtual assistant operable both as a Windows desktop software and a globally accessible Web app.",
        "Engineered robust audio echo suppression, preventing infinite feedback loops during live microphone voice interactions.",
        "Integrated multi-word streaming with silence debouncing to accurately capture regional phrases like 'Play Bhojpuri song'.",
        "Deployed 100% zero-install client live on GitHub Pages with real-time responsive 60 FPS animated Arc-Reactor HUD.",
        "Achieved seamless integration with live APIs (Wikipedia knowledge base, wttr.in weather forecasts, YouTube media search)."
    ]

    ach_y = 315
    for a in achievements:
        draw_checkmark(draw, 90, ach_y + 4, size=20, color=CRIMSON_BRIGHT)
        
        lines = wrap_text(a, FONT_BODY, 710, draw)
        line_y = ach_y
        for line in lines:
            draw.text((130, line_y), line, font=FONT_BODY, fill=TEXT_WHITE)
            line_y += 28

        ach_y += 114

    # Right: Future Scope
    draw_noir_card(draw, 980, 225, 880, 685, title="FUTURE SCOPE & ROADMAP", subtitle="Upcoming Architectural Innovations")

    future_items = [
        ("Offline Local LLMs (Llama 3 / Gemma)", "Embedding quantized small language models directly on the client machine for 100% offline intelligence without cloud reliance."),
        ("Physical IoT Hardware Integration", "Bridging simulated smart devices to physical microcontrollers (ESP32/Raspberry Pi) and home automation systems via MQTT protocols."),
        ("Voice Biometric Authentication", "Upgrading from webcam face detection to deep learning voiceprint identification for biometric security clearance."),
        ("Multi-Lingual NLP Synthesis", "Expanding full spoken conversational fluency into Indian regional languages (Hindi, Bhojpuri, Tamil) natively.")
    ]

    fut_y = 310
    for title, desc in future_items:
        draw.rounded_rectangle([(1010, fut_y), (1830, fut_y + 115)], radius=8, fill=BG_INNER_BOX, outline=CARD_BORDER, width=1)
        # Left crimson tick
        draw.rounded_rectangle([(1010, fut_y), (1016, fut_y + 115)], radius=2, fill=CRIMSON)
        draw.text((1035, fut_y + 18), "► " + title, font=FONT_BOLD, fill=TEXT_WHITE)
        
        lines = wrap_text(desc, FONT_SMALL, 770, draw)
        line_y = fut_y + 50
        for line in lines:
            draw.text((1045, line_y), line, font=FONT_SMALL, fill=TEXT_MUTED)
            line_y += 24

        fut_y += 140

    return img


# =============================================================================
# SLIDE 8: REFERENCES & REPOSITORY (CRIMSON NOIR & INTERACTIVE HYPERLINKS)
# =============================================================================
def make_slide_8():
    img, draw = create_base_slide(8, category="REFERENCES & REPOSITORIES")

    draw.text((60, 105), "07 // REFERENCES & DOCUMENTATION", font=FONT_TITLE, fill=TEXT_WHITE)
    draw.text((60, 160), "Academic references, open-source documentation, and interactive project deployment links.", font=FONT_SUBTITLE, fill=TEXT_MUTED)

    # Card 1: Academic References
    draw_noir_card(draw, 60, 225, 560, 685, title="ACADEMIC REFERENCES", subtitle="Standards & Research Specifications")
    refs = [
        ("1. Python Software Foundation Docs", "Official Language & Standard Library Reference Manual (Python 3.13)."),
        ("2. W3C Web Speech API Specification", "Browser-native SpeechRecognition & SpeechSynthesis Interfaces."),
        ("3. Google Cloud Speech Documentation", "Best practices for acoustic speech processing & streaming models."),
        ("4. OpenCV Machine Vision Library", "Haar Feature-based Cascade Classifier Object Detection Guide."),
        ("5. Wikipedia REST API Reference", "Wikimedia Foundation Knowledge Graph & Structured Query Services.")
    ]
    ref_y = 310
    for r_title, r_desc in refs:
        draw.text((85, ref_y), r_title, font=FONT_BOLD, fill=TEXT_WHITE)
        lines = wrap_text(r_desc, FONT_SMALL, 500, draw)
        desc_y = ref_y + 24
        for l in lines:
            draw.text((85, desc_y), l, font=FONT_SMALL, fill=TEXT_MUTED)
            desc_y += 22
        ref_y = desc_y + 14

    # Card 2: Libraries & Frameworks
    draw_noir_card(draw, 660, 225, 560, 685, title="LIBRARIES & FRAMEWORKS", subtitle="Open Source Ecosystem & Dependencies")
    libs = [
        ("• Pyttsx3 (v2.99)", "Offline text-to-speech engine using Windows SAPI5 drivers."),
        ("• SpeechRecognition (v3.17)", "Microphone audio processing with Google Speech backend."),
        ("• PyAudio (v0.2.14)", "PortAudio cross-platform low-latency microphone I/O."),
        ("• Pillow (PIL v12.3)", "Digital imaging pipeline for HUD generation and screenshots."),
        ("• Tkinter GUI & Web Canvas", "Dual UI interface with 60 FPS animated Arc-Reactor HUD.")
    ]
    lib_y = 310
    for l_title, l_desc in libs:
        draw.text((685, lib_y), l_title, font=FONT_BOLD, fill=TEXT_WHITE)
        lines = wrap_text(l_desc, FONT_SMALL, 500, draw)
        desc_y = lib_y + 24
        for l in lines:
            draw.text((685, desc_y), l, font=FONT_SMALL, fill=TEXT_MUTED)
            desc_y += 22
        lib_y = desc_y + 14

    # Card 3: Project Deployment Card (Right) - Interactive Clickable Links
    draw_noir_card(draw, 1260, 225, 600, 685, title="PROJECT REPOSITORY & DEMO", subtitle="Click Any Box to Open in Browser")
    
    # 1. GitHub Repository Box
    draw.rounded_rectangle([(1290, 305), (1830, 435)], radius=8, fill=BG_INNER_BOX, outline=CRIMSON, width=2)
    draw.text((1315, 322), "GITHUB REPOSITORY", font=FONT_CARD_TITLE, fill=TEXT_WHITE)
    draw.text((1315, 360), "github.com/ashutosh18-web/", font=FONT_BOLD, fill=CRIMSON_BRIGHT)
    draw.text((1315, 390), "Voice-Based-personal-Virtual-Assistant-Jarvis-", font=FONT_SMALL, fill=TEXT_ROSE)
    # Action Button Pill
    draw.rounded_rectangle([(1610, 320), (1815, 355)], radius=14, fill=(40, 12, 22), outline=CRIMSON, width=1)
    draw.text((1625, 328), "[VISIT REPO >>]", font=FONT_BADGE, fill=TEXT_WHITE)

    # 2. 1-Click Live Web Client Box
    draw.rounded_rectangle([(1290, 465), (1830, 595)], radius=8, fill=BG_INNER_BOX, outline=CRIMSON_BRIGHT, width=2)
    draw.text((1315, 482), "1-CLICK LIVE WEB CLIENT", font=FONT_CARD_TITLE, fill=TEXT_WHITE)
    draw.text((1315, 520), "ashutosh18-web.github.io/", font=FONT_BOLD, fill=CRIMSON_BRIGHT)
    draw.text((1315, 550), "Voice-Based-personal-Virtual-Assistant-Jarvis-", font=FONT_SMALL, fill=TEXT_ROSE)
    # Action Button Pill
    draw.rounded_rectangle([(1605, 480), (1815, 515)], radius=14, fill=(40, 12, 22), outline=CRIMSON, width=1)
    draw.text((1618, 488), "[LAUNCH DEMO >>]", font=FONT_BADGE, fill=TEXT_WHITE)

    # 3. Thank you box at the bottom
    draw.rounded_rectangle([(1290, 625), (1830, 885)], radius=8, fill=BG_CARD, outline=CARD_BORDER, width=1)
    draw.text((1440, 665), "THANK YOU!", font=FONT_TITLE, fill=CRIMSON_BRIGHT)
    draw.text((1350, 735), "Voice-Based Personal Virtual Assistant", font=FONT_BOLD, fill=TEXT_WHITE)
    draw.text((1430, 775), "Questions & Discussion", font=FONT_BODY, fill=TEXT_MUTED)
    draw.text((1330, 825), "Developed by Ashutosh, Pranav, Yasir & Dhruv", font=FONT_BADGE, fill=TEXT_ROSE)

    return img


# =============================================================================
# COMPILE ALL SLIDES TO MULTI-PAGE PDF WITH INTERACTIVE HYPERLINKS
# =============================================================================
def generate_all_crimson_slides():
    print("Generating Crimson Noir Slide 1: Title & Team Details...")
    s1 = make_slide_1()
    s1_path = "slide_1_crimson.png"
    s1.save(s1_path)

    print("Generating Crimson Noir Slide 2: Purpose & Objectives...")
    s2 = make_slide_2()
    s2_path = "slide_2_crimson.png"
    s2.save(s2_path)

    print("Generating Crimson Noir Slide 3: Technologies Used...")
    s3 = make_slide_3()
    s3_path = "slide_3_crimson.png"
    s3.save(s3_path)

    print("Generating Crimson Noir Slide 4: Concepts Used...")
    s4 = make_slide_4()
    s4_path = "slide_4_crimson.png"
    s4.save(s4_path)

    print("Generating Crimson Noir Slide 5: Modules Needed...")
    s5 = make_slide_5()
    s5_path = "slide_5_crimson.png"
    s5.save(s5_path)

    print("Generating Crimson Noir Slide 6: Working & Workflow...")
    s6 = make_slide_6()
    s6_path = "slide_6_crimson.png"
    s6.save(s6_path)

    print("Generating Crimson Noir Slide 7: Conclusion & Scope...")
    s7 = make_slide_7()
    s7_path = "slide_7_crimson.png"
    s7.save(s7_path)

    print("Generating Crimson Noir Slide 8: References & Interactive Links...")
    s8 = make_slide_8()
    s8_path = "slide_8_crimson.png"
    s8.save(s8_path)

    output_pdf_path = os.path.abspath("Voice_Based_Personal_Virtual_Assistant_Jarvis_Presentation_Crimson_Noir.pdf")
    print(f"Compiling into Crimson Noir presentation PDF: {output_pdf_path}...")

    pdf = FPDF(orientation="landscape", unit="pt", format=(1080, 1920))
    pdf.set_margin(0)

    slides_info = [
        (s1_path, [
            (90, 810, 500, 42, "https://github.com/ashutosh18-web/Voice-Based-personal-Virtual-Assistant-Jarvis-"),
            (90, 868, 500, 42, "https://ashutosh18-web.github.io/Voice-Based-personal-Virtual-Assistant-Jarvis-/")
        ]),
        (s2_path, []),
        (s3_path, []),
        (s4_path, []),
        (s5_path, []),
        (s6_path, []),
        (s7_path, []),
        (s8_path, [
            (1290, 305, 540, 130, "https://github.com/ashutosh18-web/Voice-Based-personal-Virtual-Assistant-Jarvis-"),
            (1290, 465, 540, 130, "https://ashutosh18-web.github.io/Voice-Based-personal-Virtual-Assistant-Jarvis-/")
        ])
    ]

    for img_path, links in slides_info:
        pdf.add_page()
        pdf.image(img_path, x=0, y=0, w=1920, h=1080)
        for lx, ly, lw, lh, url in links:
            pdf.link(lx, ly, lw, lh, url)

    pdf.output(output_pdf_path)
    print(f"Crimson Noir PDF generated: {output_pdf_path} ({os.path.getsize(output_pdf_path) / 1024:.2f} KB)")


if __name__ == "__main__":
    generate_all_crimson_slides()
