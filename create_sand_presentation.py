import os
import math
from PIL import Image, ImageDraw, ImageFont
from fpdf import FPDF

# =============================================================================
# CANVAS DIMENSIONS (Full HD 16:9 Presentation Format)
# =============================================================================
WIDTH = 1920
HEIGHT = 1080

# =============================================================================
# COLOR PALETTE: THEME 4 - MINIMAL SAND & CHARCOAL
# Authentic, Architectural, Editorial (High Contrast, Zero Sci-Fi Gimmicks)
# =============================================================================
SAND_BG = (235, 230, 221)          # #EBE6DD Warm linen / natural sand background
SAND_CARD = (245, 241, 235)        # #F5F1EB Off-white subtle card container
SAND_CARD_HOVER = (252, 250, 246)  # #FCFAF6 Crisp highlight sand
SAND_BORDER = (195, 188, 175)      # #C3BCAF Crisp architectural warm grey border
SAND_BORDER_DARK = (160, 152, 138) # #A0988A Deeper structural dividing line

CHARCOAL = (28, 30, 33)            # #1C1E21 Deep matte carbon / architectural charcoal
CHARCOAL_CARD = (36, 40, 44)       # #24282C Rich dark container fill
CHARCOAL_SUBBOX = (48, 52, 58)     # #30343A Sub-box fill inside dark cards
CHARCOAL_BORDER = (60, 65, 72)     # #3C4148 Border for charcoal elements

TEXT_DARK = (24, 26, 29)           # #181A1D Charcoal high-contrast text
TEXT_MUTED = (110, 105, 98)        # #6E6962 Warm slate muted text
TEXT_LIGHT = (242, 238, 230)       # #F2EEE6 Sand white text on dark cards
TEXT_LIGHT_MUTED = (185, 180, 170) # #B9B4AA Muted text on dark cards
ACCENT_GREEN = (46, 125, 50)       # Muted forest green for status checks

# =============================================================================
# LOAD SYSTEM FONTS
# =============================================================================
try:
    FONT_TITLE = ImageFont.truetype("C:/Windows/Fonts/impact.ttf", 50)
    FONT_SUBTITLE = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 20)
    FONT_HEADING = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 28)
    FONT_CARD_TITLE = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 21)
    FONT_BODY = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 17)
    FONT_BOLD = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 17)
    FONT_SMALL = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 14)
    FONT_SMALL_BOLD = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 14)
    FONT_MONO = ImageFont.truetype("C:/Windows/Fonts/consolab.ttf", 16)
    FONT_BADGE = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 12)
    FONT_BIG_NUM = ImageFont.truetype("C:/Windows/Fonts/impact.ttf", 36)
except Exception:
    FONT_TITLE = ImageFont.load_default()
    FONT_SUBTITLE = ImageFont.load_default()
    FONT_HEADING = ImageFont.load_default()
    FONT_CARD_TITLE = ImageFont.load_default()
    FONT_BODY = ImageFont.load_default()
    FONT_BOLD = ImageFont.load_default()
    FONT_SMALL = ImageFont.load_default()
    FONT_SMALL_BOLD = ImageFont.load_default()
    FONT_MONO = ImageFont.load_default()
    FONT_BADGE = ImageFont.load_default()
    FONT_BIG_NUM = ImageFont.load_default()


def wrap_text(text, font, max_width, draw):
    """Wraps text cleanly so no line exceeds max_width in pixels."""
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


def draw_checkmark(draw, x, y, size=16, color=CHARCOAL):
    """Draws a clean, sharp architectural checkmark."""
    p1 = (x, y + int(size * 0.55))
    p2 = (x + int(size * 0.38), y + size)
    p3 = (x + size, y)
    draw.line([p1, p2], fill=color, width=3)
    draw.line([p2, p3], fill=color, width=3)


def create_sand_base_slide(slide_num, total_slides=8, category="PROJECT OVERVIEW"):
    """Draws Minimal Sand & Charcoal header bar, rules, metadata and footer."""
    img = Image.new("RGB", (WIDTH, HEIGHT), SAND_BG)
    draw = ImageDraw.Draw(img)

    # Top Brand / Header details
    draw.text((60, 32), "KCC INSTITUTE OF TECHNOLOGY & MANAGEMENT", font=FONT_BOLD, fill=CHARCOAL)
    
    # Category badge in center
    badge_text = f"ACADEMIC MINI PROJECT  //  {category.upper()}"
    center_x = WIDTH // 2 - int(draw.textlength(badge_text, font=FONT_SMALL)) // 2
    draw.text((center_x, 34), badge_text, font=FONT_SMALL, fill=TEXT_MUTED)

    # Slide Counter right
    counter_text = f"SLIDE {slide_num:02d} / {total_slides:02d}"
    draw.text((WIDTH - 180, 32), counter_text, font=FONT_BOLD, fill=CHARCOAL)

    # Top Header Rule (Solid Architectural Line)
    draw.line([(60, 68), (WIDTH - 60, 68)], fill=CHARCOAL, width=2)

    # Bottom Footer Bar
    draw.line([(60, HEIGHT - 52), (WIDTH - 60, HEIGHT - 52)], fill=SAND_BORDER, width=1)
    draw.text((60, HEIGHT - 38), "Voice-Based Personal Virtual Assistant (JARVIS) | Academic Mini Project 2026-2027", font=FONT_SMALL, fill=TEXT_MUTED)
    draw.text((WIDTH - 360, HEIGHT - 38), "KCC Institute of Technology and Management", font=FONT_SMALL, fill=CHARCOAL)

    return img, draw


def draw_sand_card(draw, x, y, w, h, title="", subtitle="", badge="", dark=False):
    """Draws an architectural block card in sand or charcoal style."""
    if dark:
        fill_color = CHARCOAL
        border_color = CHARCOAL
        t_color = TEXT_LIGHT
        sub_color = TEXT_LIGHT_MUTED
    else:
        fill_color = SAND_CARD
        border_color = SAND_BORDER
        t_color = TEXT_DARK
        sub_color = TEXT_MUTED

    draw.rounded_rectangle([(x, y), (x + w, y + h)], radius=4, fill=fill_color, outline=border_color, width=1)

    if title:
        draw.text((x + 28, y + 22), title, font=FONT_CARD_TITLE, fill=t_color)
    if subtitle:
        draw.text((x + 28, y + 54), subtitle, font=FONT_SMALL, fill=sub_color)
    if badge:
        badge_w = int(draw.textlength(badge, font=FONT_BADGE)) + 24
        bx2 = x + w - 24
        bx1 = bx2 - badge_w
        if dark:
            draw.rounded_rectangle([(bx1, y + 20), (bx2, y + 48)], radius=2, fill=(50, 54, 60))
            draw.text((bx1 + 12, y + 27), badge, font=FONT_BADGE, fill=TEXT_LIGHT)
        else:
            draw.rounded_rectangle([(bx1, y + 20), (bx2, y + 48)], radius=2, fill=CHARCOAL)
            draw.text((bx1 + 12, y + 27), badge, font=FONT_BADGE, fill=SAND_BG)


# =============================================================================
# SLIDE 1: TITLE SLIDE (TEAM & GUIDE - MINIMAL SAND & CHARCOAL)
# =============================================================================
def make_slide_1():
    img, draw = create_sand_base_slide(1, category="PROJECT OVERVIEW & TEAM")

    # Pill category
    draw.rounded_rectangle([(60, 105), (320, 138)], radius=4, fill=CHARCOAL)
    draw.text((75, 114), "AI & VOICE INTELLIGENCE", font=FONT_BADGE, fill=SAND_BG)

    # Main Project Title in Impact
    draw.text((60, 155), "VOICE-BASED PERSONAL VIRTUAL ASSISTANT", font=FONT_TITLE, fill=CHARCOAL)
    draw.text((60, 225), "Project JARVIS (Just A Rather Very Intelligent System)", font=FONT_HEADING, fill=CHARCOAL)
    draw.text((60, 270), "A Context-Aware, Hands-Free Intelligent Assistant & Operating System Automation Agent", font=FONT_SUBTITLE, fill=TEXT_MUTED)

    # Right Header: Official KCC Logo
    if os.path.exists("kcc_official_logo.png"):
        kcc = Image.open("kcc_official_logo.png")
        if kcc.mode == "RGBA":
            bg = Image.new("RGB", kcc.size, SAND_BG)
            bg.paste(kcc, mask=kcc.split()[3])
            kcc = bg
        kcc_w = 110
        kcc_h = int(kcc_w * (kcc.height / kcc.width))
        kcc_res = kcc.resize((kcc_w, kcc_h), Image.Resampling.LANCZOS)
        img.paste(kcc_res, (WIDTH - 180, 130))
        draw.rectangle([(WIDTH - 182, 128), (WIDTH - 182 + kcc_w + 4, 128 + kcc_h + 4)], outline=CHARCOAL, width=1)

    # Card 1: Project Guide Card (Left Box - Charcoal for high contrast)
    draw.rounded_rectangle([(60, 340), (620, 950)], radius=4, fill=CHARCOAL)
    draw.text((90, 370), "PROJECT GUIDE & MENTOR", font=FONT_CARD_TITLE, fill=SAND_BG)
    draw.text((90, 402), "Faculty Direction & Supervision", font=FONT_SMALL, fill=TEXT_LIGHT_MUTED)

    # Inner Guide Highlight Box
    draw.rounded_rectangle([(90, 440), (590, 560)], radius=4, fill=CHARCOAL_SUBBOX)
    draw.text((115, 460), "Mr. Mundigonda Sanjay", font=FONT_HEADING, fill=TEXT_LIGHT)
    draw.text((115, 510), "Assistant Professor | Project Guide", font=FONT_BOLD, fill=SAND_BG)

    draw.text((90, 595), "Department of Computer Science & Engineering", font=FONT_BOLD, fill=TEXT_LIGHT)
    draw.text((90, 630), "Academic Session: 2026 – 2027", font=FONT_BODY, fill=TEXT_LIGHT_MUTED)
    draw.text((90, 665), "College Code: 492 | KCC ITM, Greater Noida", font=FONT_BODY, fill=TEXT_LIGHT_MUTED)
    draw.text((90, 700), "Project Domain: Artificial Intelligence & NLP", font=FONT_BODY, fill=TEXT_LIGHT_MUTED)

    draw.line([(90, 750), (590, 750)], fill=CHARCOAL_BORDER, width=1)
    draw.text((90, 770), "Assessment Status: APPROVED", font=FONT_BOLD, fill=(130, 215, 145))

    # Clickable link buttons inside Guide Box
    draw.rounded_rectangle([(90, 810), (590, 852)], radius=3, fill=CHARCOAL_SUBBOX, outline=CHARCOAL_BORDER, width=1)
    draw.text((105, 822), "// GITHUB REPO : github.com/ashutosh18-web", font=FONT_MONO, fill=TEXT_LIGHT)

    draw.rounded_rectangle([(90, 868), (590, 910)], radius=3, fill=CHARCOAL_SUBBOX, outline=CHARCOAL_BORDER, width=1)
    draw.text((105, 880), "// LIVE DEMO   : ashutosh18-web.github.io", font=FONT_MONO, fill=SAND_BG)

    # Card 2: Team Members Card (Right Box - Sand Card Container)
    draw.rounded_rectangle([(660, 340), (1860, 950)], radius=4, fill=SAND_CARD, outline=SAND_BORDER, width=1)
    draw.text((695, 370), "PROJECT TEAM MEMBERS", font=FONT_HEADING, fill=CHARCOAL)
    draw.text((695, 405), "Group Contributors & Roll Numbers", font=FONT_SMALL, fill=TEXT_MUTED)

    members = [
        ("1", "Ashutosh Chaudhari", "2504921530087", "Lead Developer – Core Architecture & NLP"),
        ("2", "Pranav", "2504921530255", "Speech Synthesis & Audio Processing Pipeline"),
        ("3", "Mohd Yasir", "2504921520132", "Web Interface & UI Visualizer Design"),
        ("4", "Dhruv Sharma", "2504920100223", "System Automation & Integration Testing")
    ]

    card_y = 445
    for idx, name, roll, role in members:
        # Member Box (Charcoal background with Sand text for sharp editorial aesthetic)
        draw.rounded_rectangle([(695, card_y), (1825, card_y + 102)], radius=4, fill=CHARCOAL)

        # Number Badge
        draw.rounded_rectangle([(715, card_y + 16), (775, card_y + 86)], radius=2, fill=SAND_BG)
        draw.text((735, card_y + 24), idx, font=FONT_HEADING, fill=CHARCOAL)

        # Name and Roll
        draw.text((800, card_y + 20), name, font=FONT_CARD_TITLE, fill=TEXT_LIGHT)
        draw.text((800, card_y + 58), f"Roll Number: {roll}", font=FONT_BODY, fill=SAND_BG)

        # Role badge right side
        draw.rounded_rectangle([(1270, card_y + 28), (1805, card_y + 74)], radius=2, fill=CHARCOAL_SUBBOX)
        draw.text((1295, card_y + 40), role, font=FONT_SMALL, fill=TEXT_LIGHT)

        card_y += 120

    return img


# =============================================================================
# SLIDE 2: PURPOSE OF THE PROJECT (MINIMAL SAND & CHARCOAL)
# =============================================================================
def make_slide_2():
    img, draw = create_sand_base_slide(2, category="PROJECT MOTIVATION & OBJECTIVES")

    # Pill category
    draw.rounded_rectangle([(60, 95), (280, 128)], radius=4, fill=CHARCOAL)
    draw.text((75, 104), "PROBLEM & PURPOSE", font=FONT_BADGE, fill=SAND_BG)

    draw.text((60, 142), "PURPOSE OF THE PROJECT", font=FONT_TITLE, fill=CHARCOAL)
    draw.text((60, 205), "Addressing the limitations of conventional mouse-and-keyboard computing through touchless speech intelligence.", font=FONT_SUBTITLE, fill=TEXT_MUTED)

    goals = [
        ("01", "Hands-Free Desktop Accessibility",
         "Eliminates dependency on physical peripherals by allowing users to operate their PC entirely via spoken voice commands, significantly benefiting accessibility and rapid multitasking.",
         "ACCESSIBILITY"),
        ("02", "Unified Intelligent Ecosystem",
         "Combines disparate desktop actions (opening apps, file editing, volume, screen lock) with cloud capabilities (weather, music streaming, Google search) into a single voice-driven dashboard.",
         "INTEGRATION"),
        ("03", "Dual Deployment Platform",
         "Engineered as both a full-featured Windows desktop application (Tkinter, local OS hooks) and a zero-install 1-click Web application deployed on GitHub Pages for mobile & web users.",
         "VERSATILITY"),
        ("04", "Echo-Suppressed Continuous Recognition",
         "Solves real-world virtual assistant problems: eliminates audio echo feedback loops while keeping speech recognition continuous so multi-word Indian phrases are never cut short.",
         "RELIABILITY")
    ]

    card_coords = [
        (60, 260, 870, 320),
        (980, 260, 880, 320),
        (60, 620, 870, 320),
        (980, 620, 880, 320)
    ]

    for (num, title, desc, badge), (x, y, w, h) in zip(goals, card_coords):
        # Sand card container
        draw.rounded_rectangle([(x, y), (x + w, y + h)], radius=4, fill=SAND_CARD, outline=SAND_BORDER, width=1)
        
        # Large architectural number box
        draw.rounded_rectangle([(x + 24, y + 24), (x + 84, y + 84)], radius=2, fill=CHARCOAL)
        draw.text((x + 36, y + 36), num, font=FONT_BIG_NUM, fill=SAND_BG)

        # Title & Badge
        draw.text((x + 104, y + 28), title, font=FONT_CARD_TITLE, fill=CHARCOAL)
        
        badge_w = int(draw.textlength(badge, font=FONT_BADGE)) + 24
        draw.rounded_rectangle([(x + 104, y + 62), (x + 104 + badge_w, y + 88)], radius=2, fill=CHARCOAL_SUBBOX)
        draw.text((x + 116, y + 68), badge, font=FONT_BADGE, fill=TEXT_LIGHT)

        # Divider
        draw.line([(x + 24, y + 108), (x + w - 24, y + 108)], fill=SAND_BORDER, width=1)

        # Description wrapped
        lines = wrap_text(desc, FONT_BODY, w - 50, draw)
        line_y = y + 130
        for line in lines:
            draw.text((x + 26, line_y), line, font=FONT_BODY, fill=TEXT_DARK)
            line_y += 32

    return img


# =============================================================================
# SLIDE 3: TECHNOLOGIES USED (MINIMAL SAND & CHARCOAL)
# =============================================================================
def make_slide_3():
    img, draw = create_sand_base_slide(3, category="TECHNOLOGY STACK & TOOLS")

    draw.rounded_rectangle([(60, 95), (280, 128)], radius=4, fill=CHARCOAL)
    draw.text((75, 104), "STACK & DEPENDENCIES", font=FONT_BADGE, fill=SAND_BG)

    draw.text((60, 142), "TECHNOLOGIES & TOOLS USED", font=FONT_TITLE, fill=CHARCOAL)
    draw.text((60, 205), "Modern hybrid architecture combining Python 3.13 backend with HTML5 Web Speech engines.", font=FONT_SUBTITLE, fill=TEXT_MUTED)

    techs = [
        ("01", "Python 3.13 Runtime",
         "Core programming language powering desktop assistant, system automation, multi-threaded audio pipelines, and OS hooks.",
         ["pyttsx3 (SAPI5)", "SpeechRecognition", "PyAudio Driver", "ctypes / win32"]),
        ("02", "Modern Web & GUI",
         "Futuristic 60 FPS animated Arc-Reactor interface with glowing soundwave audio visualizers and diagnostic consoles.",
         ["HTML5 Canvas 2D", "CSS3 Flex/Grid", "JavaScript ES6+", "Tkinter Desktop GUI"]),
        ("03", "Speech AI & REST APIs",
         "Continuous multi-word speech recognition, live meteorological forecasts, and encyclopedic knowledge queries.",
         ["Web Speech API", "Google Speech API", "Wikipedia REST API", "wttr.in Weather API"]),
        ("04", "Vision & Productivity",
         "Biometric facial verification scanning, desktop screenshot automation, and structured persistent databases.",
         ["OpenCV (cv2)", "PIL / Pillow", "Haar Cascades", "JSON / LocalStorage"])
    ]

    xs = [60, 520, 980, 1440]
    w = 420
    h = 710
    y = 250

    for (num, title, desc, tools), x in zip(techs, xs):
        draw.rounded_rectangle([(x, y), (x + w, y + h)], radius=4, fill=SAND_CARD, outline=SAND_BORDER, width=1)
        
        # Header Badge
        draw.rounded_rectangle([(x + 24, y + 24), (x + 74, y + 68)], radius=2, fill=CHARCOAL)
        draw.text((x + 32, y + 28), num, font=FONT_HEADING, fill=SAND_BG)

        draw.text((x + 90, y + 32), title, font=FONT_CARD_TITLE, fill=CHARCOAL)

        # Description
        lines = wrap_text(desc, FONT_BODY, w - 48, draw)
        line_y = y + 90
        for line in lines:
            draw.text((x + 24, line_y), line, font=FONT_BODY, fill=TEXT_DARK)
            line_y += 28

        # Divider line
        draw.line([(x + 20, y + 265), (x + w - 20, y + 265)], fill=SAND_BORDER, width=1)
        draw.text((x + 24, y + 285), "CORE LIBRARIES / ENGINES:", font=FONT_SMALL_BOLD, fill=CHARCOAL)

        # Tool Badges
        pill_y = y + 325
        for tool in tools:
            draw.rounded_rectangle([(x + 24, pill_y), (x + w - 24, pill_y + 60)], radius=3, fill=CHARCOAL)
            
            # Left accent block
            draw.rounded_rectangle([(x + 24, pill_y), (x + 32, pill_y + 60)], radius=1, fill=SAND_BORDER_DARK)
            draw.text((x + 48, pill_y + 18), tool, font=FONT_BOLD, fill=TEXT_LIGHT)
            pill_y += 76

    return img


# =============================================================================
# SLIDE 4: CONCEPT USED IN THIS PROJECT (MINIMAL SAND & CHARCOAL)
# =============================================================================
def make_slide_4():
    img, draw = create_sand_base_slide(4, category="CORE CONCEPTS & METHODOLOGY")

    draw.rounded_rectangle([(60, 95), (280, 128)], radius=4, fill=CHARCOAL)
    draw.text((75, 104), "METHODOLOGY & LOGIC", font=FONT_BADGE, fill=SAND_BG)

    draw.text((60, 142), "CONCEPTS USED IN THIS PROJECT", font=FONT_TITLE, fill=CHARCOAL)
    draw.text((60, 205), "Key software engineering paradigms, acoustic feedback management, and multi-turn NLP logic.", font=FONT_SUBTITLE, fill=TEXT_MUTED)

    concepts = [
        ("01", "Acoustic Echo Suppression (Feedback Loop Barrier)",
         "A major challenge in voice assistants is the microphone hearing the assistant's own speaker output, triggering infinite speech loops. JARVIS implements an active state lock (isSpeaking) that dynamically mutes and aborts recognition during TTS playback, completely eliminating feedback loops.",
         "SIGNAL PROCESSING"),
        ("02", "Continuous Multi-Word Streaming & Debounce Threshold",
         "Standard speech recognition often prematurely truncates queries after the first word (e.g. cutting 'Play Bhojpuri song' into just 'Play'). JARVIS utilizes continuous streaming with a 1.3-second silence debounce timer, allowing multi-word natural queries and regional names to be captured fully.",
         "STREAMING RECOGNITION"),
        ("03", "Intent Classification & Rule-Heuristic Normalization",
         "Spoken queries undergo regex cleaning (lowercasing, punctuation stripping, stop-word reduction) before classification into action domains (Media Playback, Application Launch, IoT Control, Weather, Math, and Wikipedia knowledge lookup).",
         "NATURAL LANGUAGE PROCESSING"),
        ("04", "Dual-State Persistent Memory Matrix",
         "Maintains conversational context, user preferences (e.g. favorite music, location, and preferred language), to-do task items, and smart home device toggles using structured JSON storage on desktop and persistent LocalStorage in the browser.",
         "PERSISTENT STORAGE")
    ]

    card_y = 250
    for num, title, desc, tag in concepts:
        draw.rounded_rectangle([(60, card_y), (1860, card_y + 155)], radius=4, fill=SAND_CARD, outline=SAND_BORDER, width=1)
        
        # Architectural Number
        draw.rounded_rectangle([(84, card_y + 20), (140, card_y + 68)], radius=2, fill=CHARCOAL)
        draw.text((95, card_y + 25), num, font=FONT_HEADING, fill=SAND_BG)

        # Title
        draw.text((160, card_y + 28), title, font=FONT_CARD_TITLE, fill=CHARCOAL)

        # Category Badge Right
        tag_w = int(draw.textlength(tag, font=FONT_BADGE)) + 24
        draw.rounded_rectangle([(1836 - tag_w, card_y + 24), (1836, card_y + 54)], radius=2, fill=CHARCOAL_SUBBOX)
        draw.text((1848 - tag_w, card_y + 31), tag, font=FONT_BADGE, fill=TEXT_LIGHT)

        # Description wrapped
        lines = wrap_text(desc, FONT_BODY, 1720, draw)
        line_y = card_y + 78
        for line in lines:
            draw.text((88, line_y), line, font=FONT_BODY, fill=TEXT_DARK)
            line_y += 28

        card_y += 175

    return img


# =============================================================================
# SLIDE 5: MODULES NEEDED (MINIMAL SAND & CHARCOAL)
# =============================================================================
def make_slide_5():
    img, draw = create_sand_base_slide(5, category="SYSTEM ARCHITECTURE & MODULES")

    draw.rounded_rectangle([(60, 95), (280, 128)], radius=4, fill=CHARCOAL)
    draw.text((75, 104), "SYSTEM DECOMPOSITION", font=FONT_BADGE, fill=SAND_BG)

    draw.text((60, 142), "MODULES NEEDED IN JARVIS", font=FONT_TITLE, fill=CHARCOAL)
    draw.text((60, 205), "Modular decomposition ensuring separation of concerns, scalability, and robust error tolerance.", font=FONT_SUBTITLE, fill=TEXT_MUTED)

    modules = [
        ("01", "Speech & Audio Module",
         "Manages dual-channel voice input and output with real-time acoustic echo suppression and continuous listening.",
         ["Speech-to-Text (STT Engine)", "Text-to-Speech (TTS Synthesizer)", "Continuous Listener Thread", "Accent Support (en-IN / hi-IN)"]),
        ("02", "Automation & Launcher Module",
         "Dispatches native desktop commands, opens local applications, triggers browser searches, and controls media playback.",
         ["App Launcher (Notepad, Calc, CMD)", "Google Search Dispatcher", "YouTube Music Player", "Volume & Screen Lock Hooks"]),
        ("03", "Smart Home & IoT Hub",
         "Monitors and toggles smart home appliances with real-time state synchronization, voice triggers, and visual controls.",
         ["Living Room & Bedroom Lights", "AC Thermostat Temperature", "Main Door Security Lock", "State Persistence Engine"]),
        ("04", "Productivity & Vision Module",
         "Provides intelligent workflow tools including to-do task management, voice notes, math evaluations, and face scanning.",
         ["To-Do Task Scheduler", "Quick Note Taker (.txt)", "Math Expression Evaluator", "OpenCV Biometric Face Scanner"])
    ]

    card_coords = [
        (60, 260, 870, 320),
        (980, 260, 880, 320),
        (60, 620, 870, 320),
        (980, 620, 880, 320)
    ]

    for (num, title, desc, bullets), (x, y, w, h) in zip(modules, card_coords):
        draw.rounded_rectangle([(x, y), (x + w, y + h)], radius=4, fill=SAND_CARD, outline=SAND_BORDER, width=1)
        
        # Number Block
        draw.rounded_rectangle([(x + 24, y + 20), (x + 74, y + 64)], radius=2, fill=CHARCOAL)
        draw.text((x + 32, y + 24), num, font=FONT_HEADING, fill=SAND_BG)

        draw.text((x + 90, y + 28), title, font=FONT_CARD_TITLE, fill=CHARCOAL)

        lines = wrap_text(desc, FONT_BODY, w - 50, draw)
        desc_y = y + 74
        for l in lines:
            draw.text((x + 24, desc_y), l, font=FONT_BODY, fill=TEXT_MUTED)
            desc_y += 24

        draw.line([(x + 20, y + 132), (x + w - 20, y + 132)], fill=SAND_BORDER, width=1)

        bullet_y = y + 150
        for b in bullets:
            draw.rectangle([(x + 32, bullet_y + 4), (x + 40, bullet_y + 12)], fill=CHARCOAL)
            draw.text((x + 55, bullet_y), b, font=FONT_BOLD, fill=TEXT_DARK)
            bullet_y += 38

    return img


# =============================================================================
# SLIDE 6: WORKING & DATA FLOW ARCHITECTURE (MINIMAL SAND & CHARCOAL)
# =============================================================================
def make_slide_6():
    img, draw = create_sand_base_slide(6, category="SYSTEM EXECUTION WORKFLOW")

    draw.rounded_rectangle([(60, 95), (280, 128)], radius=4, fill=CHARCOAL)
    draw.text((75, 104), "PIPELINE EXECUTION", font=FONT_BADGE, fill=SAND_BG)

    draw.text((60, 142), "WORKING & DATA FLOW ARCHITECTURE", font=FONT_TITLE, fill=CHARCOAL)
    draw.text((60, 205), "End-to-end lifecycle of a voice command from microphone capture to physical system execution.", font=FONT_SUBTITLE, fill=TEXT_MUTED)

    steps = [
        ("STEP 01", "Acoustic Audio Capture", "Microphone continuously samples user voice using dynamic energy thresholding & noise reduction.", CHARCOAL),
        ("STEP 02", "Speech-to-Text Conversion", "Audio stream converted into clean textual transcript via Google Speech / Web Speech engines.", CHARCOAL),
        ("STEP 03", "Intent Dispatching", "NLP engine normalizes string, matches intents (Media, Apps, Weather, System), and routes execution.", CHARCOAL),
        ("STEP 04", "Command Execution & OS Hook", "Executes action: launches desktop app, opens YouTube song, queries Wikipedia API, or toggles IoT device.", CHARCOAL),
        ("STEP 05", "Voice Output & HUD Feedback", "Synthesizes voice reply via TTS while Arc-Reactor soundwave visualizer animates in real-time.", CHARCOAL)
    ]

    card_y = 250
    for step_num, title, desc, color in steps:
        draw.rounded_rectangle([(60, card_y), (1860, card_y + 115)], radius=4, fill=SAND_CARD, outline=SAND_BORDER, width=1)
        
        # Step Badge (Charcoal Box)
        draw.rounded_rectangle([(84, card_y + 20), (220, card_y + 95)], radius=2, fill=CHARCOAL)
        draw.text((105, card_y + 40), step_num, font=FONT_CARD_TITLE, fill=SAND_BG)

        # Title and details
        draw.text((250, card_y + 25), title, font=FONT_CARD_TITLE, fill=CHARCOAL)
        draw.text((250, card_y + 65), desc, font=FONT_BODY, fill=TEXT_DARK)

        # Subtle downward connector indicator between steps
        if card_y < 700:
            arrow_y = card_y + 115
            draw.text((950, arrow_y - 6), "▼", font=FONT_BODY, fill=CHARCOAL)

        card_y += 140

    return img


# =============================================================================
# SLIDE 7: CONCLUSION & FUTURE SCOPE (MINIMAL SAND & CHARCOAL)
# =============================================================================
def make_slide_7():
    img, draw = create_sand_base_slide(7, category="PROJECT SUMMARY & ROADMAP")

    draw.rounded_rectangle([(60, 95), (280, 128)], radius=4, fill=CHARCOAL)
    draw.text((75, 104), "IMPACT & ROADMAP", font=FONT_BADGE, fill=SAND_BG)

    draw.text((60, 142), "CONCLUSION & FUTURE SCOPE", font=FONT_TITLE, fill=CHARCOAL)
    draw.text((60, 205), "Reflecting on system milestones achieved and outlining future engineering enhancements.", font=FONT_SUBTITLE, fill=TEXT_MUTED)

    # Left Box: Achievements (Charcoal container for editorial contrast)
    draw.rounded_rectangle([(60, 250), (930, 960)], radius=4, fill=CHARCOAL)
    draw.text((90, 280), "PROJECT ACHIEVEMENTS & RESULTS", font=FONT_CARD_TITLE, fill=SAND_BG)
    draw.text((90, 314), "Key Project Milestones Reached", font=FONT_SMALL, fill=TEXT_LIGHT_MUTED)

    achievements = [
        "Successfully developed a dual-environment virtual assistant operable both as a Windows desktop software and a globally accessible Web app.",
        "Engineered robust audio echo suppression, preventing infinite feedback loops during live microphone voice interactions.",
        "Integrated multi-word streaming with silence debouncing to accurately capture regional phrases like 'Play Bhojpuri song'.",
        "Deployed 100% zero-install client live on GitHub Pages with real-time responsive 60 FPS animated Arc-Reactor HUD.",
        "Achieved seamless integration with live APIs (Wikipedia knowledge base, wttr.in weather forecasts, YouTube media search)."
    ]

    ach_y = 360
    for a in achievements:
        draw_checkmark(draw, 90, ach_y + 4, size=18, color=SAND_BG)
        
        lines = wrap_text(a, FONT_BODY, 730, draw)
        line_y = ach_y
        for line in lines:
            draw.text((125, line_y), line, font=FONT_BODY, fill=TEXT_LIGHT)
            line_y += 28

        ach_y += 114

    # Right Box: Future Scope (Sand container)
    draw.rounded_rectangle([(970, 250), (1860, 960)], radius=4, fill=SAND_CARD, outline=SAND_BORDER, width=1)
    draw.text((1000, 280), "FUTURE SCOPE & ROADMAP", font=FONT_CARD_TITLE, fill=CHARCOAL)
    draw.text((1000, 314), "Upcoming Architectural Innovations", font=FONT_SMALL, fill=TEXT_MUTED)

    future_items = [
        ("Offline Local LLMs (Llama 3 / Gemma)", "Embedding quantized small language models directly on the client machine for 100% offline intelligence without cloud reliance."),
        ("Physical IoT Hardware Integration", "Bridging simulated smart devices to physical microcontrollers (ESP32/Raspberry Pi) and home automation systems via MQTT protocols."),
        ("Voice Biometric Authentication", "Upgrading from webcam face detection to deep learning voiceprint identification for biometric security clearance."),
        ("Multi-Lingual NLP Synthesis", "Expanding full spoken conversational fluency into Indian regional languages (Hindi, Bhojpuri, Tamil) natively.")
    ]

    fut_y = 360
    for title, desc in future_items:
        draw.rounded_rectangle([(1000, fut_y), (1830, fut_y + 120)], radius=4, fill=SAND_BG, outline=SAND_BORDER, width=1)
        
        # Left accent block
        draw.rounded_rectangle([(1000, fut_y), (1008, fut_y + 120)], radius=1, fill=CHARCOAL)
        draw.text((1030, fut_y + 18), title, font=FONT_BOLD, fill=CHARCOAL)
        
        lines = wrap_text(desc, FONT_SMALL, 770, draw)
        line_y = fut_y + 52
        for line in lines:
            draw.text((1030, line_y), line, font=FONT_SMALL, fill=TEXT_DARK)
            line_y += 24

        fut_y += 145

    return img


# =============================================================================
# SLIDE 8: REFERENCES & REPOSITORY (MINIMAL SAND & CHARCOAL & INTERACTIVE LINKS)
# =============================================================================
def make_slide_8():
    img, draw = create_sand_base_slide(8, category="REFERENCES & REPOSITORIES")

    draw.rounded_rectangle([(60, 95), (280, 128)], radius=4, fill=CHARCOAL)
    draw.text((75, 104), "SOURCES & DEMOS", font=FONT_BADGE, fill=SAND_BG)

    draw.text((60, 142), "REFERENCES & INTERACTIVE ACCESS", font=FONT_TITLE, fill=CHARCOAL)
    draw.text((60, 205), "Academic references, open-source documentation, and interactive project deployment links.", font=FONT_SUBTITLE, fill=TEXT_MUTED)

    # Column 1: Academic References
    draw.rounded_rectangle([(60, 250), (620, 960)], radius=4, fill=SAND_CARD, outline=SAND_BORDER, width=1)
    draw.text((85, 280), "ACADEMIC REFERENCES", font=FONT_CARD_TITLE, fill=CHARCOAL)
    draw.text((85, 314), "Standards & Research Specs", font=FONT_SMALL, fill=TEXT_MUTED)

    refs = [
        ("1. Python Software Foundation Docs", "Official Language & Standard Library Reference Manual (Python 3.13)."),
        ("2. W3C Web Speech API Specification", "Browser-native SpeechRecognition & SpeechSynthesis Interfaces."),
        ("3. Google Cloud Speech Documentation", "Best practices for acoustic speech processing & streaming models."),
        ("4. OpenCV Machine Vision Library", "Haar Feature-based Cascade Classifier Object Detection Guide."),
        ("5. Wikipedia REST API Reference", "Wikimedia Foundation Knowledge Graph & Structured Query Services.")
    ]
    ref_y = 360
    for r_title, r_desc in refs:
        draw.text((85, ref_y), r_title, font=FONT_BOLD, fill=CHARCOAL)
        lines = wrap_text(r_desc, FONT_SMALL, 490, draw)
        desc_y = ref_y + 24
        for l in lines:
            draw.text((85, desc_y), l, font=FONT_SMALL, fill=TEXT_DARK)
            desc_y += 22
        ref_y = desc_y + 16

    # Column 2: Libraries & Frameworks
    draw.rounded_rectangle([(660, 250), (1220, 960)], radius=4, fill=SAND_CARD, outline=SAND_BORDER, width=1)
    draw.text((685, 280), "LIBRARIES & FRAMEWORKS", font=FONT_CARD_TITLE, fill=CHARCOAL)
    draw.text((685, 314), "Open Source Ecosystem & Dependencies", font=FONT_SMALL, fill=TEXT_MUTED)

    libs = [
        ("• Pyttsx3 (v2.99)", "Offline text-to-speech engine using Windows SAPI5 drivers."),
        ("• SpeechRecognition (v3.17)", "Microphone audio processing with Google Speech backend."),
        ("• PyAudio (v0.2.14)", "PortAudio cross-platform low-latency microphone I/O."),
        ("• Pillow (PIL v12.3)", "Digital imaging pipeline for HUD generation and screenshots."),
        ("• Tkinter GUI & Web Canvas", "Dual UI interface with 60 FPS animated Arc-Reactor HUD.")
    ]
    lib_y = 360
    for l_title, l_desc in libs:
        draw.text((685, lib_y), l_title, font=FONT_BOLD, fill=CHARCOAL)
        lines = wrap_text(l_desc, FONT_SMALL, 490, draw)
        desc_y = lib_y + 24
        for l in lines:
            draw.text((685, desc_y), l, font=FONT_SMALL, fill=TEXT_DARK)
            desc_y += 22
        lib_y = desc_y + 16

    # Column 3: Project Repository & Interactive Links (Right Box)
    draw.rounded_rectangle([(1260, 250), (1860, 960)], radius=4, fill=SAND_CARD, outline=SAND_BORDER, width=1)
    draw.text((1285, 280), "PROJECT REPOSITORY & DEMO", font=FONT_CARD_TITLE, fill=CHARCOAL)
    draw.text((1285, 314), "Click Any Box Below to Open in Browser", font=FONT_SMALL, fill=TEXT_MUTED)

    # 1. GitHub Repository Box (Solid Charcoal for high contrast)
    draw.rounded_rectangle([(1290, 355), (1830, 485)], radius=4, fill=CHARCOAL)
    draw.text((1315, 372), "GITHUB REPOSITORY", font=FONT_CARD_TITLE, fill=SAND_BG)
    draw.text((1315, 410), "github.com/ashutosh18-web/", font=FONT_MONO, fill=TEXT_LIGHT)
    draw.text((1315, 440), "Voice-Based-personal-Virtual-Assistant-Jarvis-", font=FONT_SMALL, fill=TEXT_LIGHT_MUTED)
    
    # Action Pill
    draw.rounded_rectangle([(1640, 370), (1805, 405)], radius=2, fill=SAND_BG)
    draw.text((1655, 378), "[VISIT REPO >>]", font=FONT_BADGE, fill=CHARCOAL)

    # 2. 1-Click Live Web Client Box (Solid Charcoal)
    draw.rounded_rectangle([(1290, 515), (1830, 645)], radius=4, fill=CHARCOAL)
    draw.text((1315, 532), "1-CLICK LIVE WEB CLIENT", font=FONT_CARD_TITLE, fill=SAND_BG)
    draw.text((1315, 570), "ashutosh18-web.github.io/", font=FONT_MONO, fill=TEXT_LIGHT)
    draw.text((1315, 600), "Voice-Based-personal-Virtual-Assistant-Jarvis-", font=FONT_SMALL, fill=TEXT_LIGHT_MUTED)

    # Action Pill
    draw.rounded_rectangle([(1630, 530), (1805, 565)], radius=2, fill=SAND_BG)
    draw.text((1645, 538), "[LAUNCH DEMO >>]", font=FONT_BADGE, fill=CHARCOAL)

    # 3. Thank You Card (Architectural Charcoal Box)
    draw.rounded_rectangle([(1290, 675), (1830, 935)], radius=4, fill=SAND_BG, outline=SAND_BORDER_DARK, width=2)
    ty_center_x = (1290 + 1830) // 2

    t1 = "THANK YOU!"
    w1 = int(draw.textlength(t1, font=FONT_TITLE))
    draw.text((ty_center_x - w1 // 2, 715), t1, font=FONT_TITLE, fill=CHARCOAL)

    t2 = "Voice-Based Personal Virtual Assistant"
    w2 = int(draw.textlength(t2, font=FONT_CARD_TITLE))
    draw.text((ty_center_x - w2 // 2, 785), t2, font=FONT_CARD_TITLE, fill=CHARCOAL)

    t3 = "Questions & Discussion"
    w3 = int(draw.textlength(t3, font=FONT_BODY))
    draw.text((ty_center_x - w3 // 2, 830), t3, font=FONT_BODY, fill=TEXT_MUTED)

    t4 = "Developed by Ashutosh, Pranav, Yasir & Dhruv"
    w4 = int(draw.textlength(t4, font=FONT_SMALL_BOLD))
    draw.text((ty_center_x - w4 // 2, 880), t4, font=FONT_SMALL_BOLD, fill=CHARCOAL)

    return img


# =============================================================================
# COMPILE ALL SLIDES TO MULTI-PAGE PDF WITH INTERACTIVE HYPERLINKS
# =============================================================================
def generate_all_sand_slides():
    print("Generating Minimal Sand & Charcoal Slide 1: Title & Team Details...")
    s1 = make_slide_1()
    s1_path = "slide_1_sand.png"
    s1.save(s1_path)

    print("Generating Minimal Sand & Charcoal Slide 2: Purpose & Objectives...")
    s2 = make_slide_2()
    s2_path = "slide_2_sand.png"
    s2.save(s2_path)

    print("Generating Minimal Sand & Charcoal Slide 3: Technologies Used...")
    s3 = make_slide_3()
    s3_path = "slide_3_sand.png"
    s3.save(s3_path)

    print("Generating Minimal Sand & Charcoal Slide 4: Concepts Used...")
    s4 = make_slide_4()
    s4_path = "slide_4_sand.png"
    s4.save(s4_path)

    print("Generating Minimal Sand & Charcoal Slide 5: Modules Needed...")
    s5 = make_slide_5()
    s5_path = "slide_5_sand.png"
    s5.save(s5_path)

    print("Generating Minimal Sand & Charcoal Slide 6: Working & Workflow...")
    s6 = make_slide_6()
    s6_path = "slide_6_sand.png"
    s6.save(s6_path)

    print("Generating Minimal Sand & Charcoal Slide 7: Conclusion & Scope...")
    s7 = make_slide_7()
    s7_path = "slide_7_sand.png"
    s7.save(s7_path)

    print("Generating Minimal Sand & Charcoal Slide 8: References & Interactive Links...")
    s8 = make_slide_8()
    s8_path = "slide_8_sand.png"
    s8.save(s8_path)

    output_pdf_path = os.path.abspath("Voice_Based_Personal_Virtual_Assistant_Jarvis_Presentation_Sand_Charcoal.pdf")
    print(f"Compiling into Minimal Sand & Charcoal presentation PDF: {output_pdf_path}...")

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
            (1290, 355, 540, 130, "https://github.com/ashutosh18-web/Voice-Based-personal-Virtual-Assistant-Jarvis-"),
            (1290, 515, 540, 130, "https://ashutosh18-web.github.io/Voice-Based-personal-Virtual-Assistant-Jarvis-/")
        ])
    ]

    for img_path, links in slides_info:
        pdf.add_page()
        pdf.image(img_path, x=0, y=0, w=1920, h=1080)
        for lx, ly, lw, lh, url in links:
            pdf.link(lx, ly, lw, lh, url)

    pdf.output(output_pdf_path)
    print(f"Minimal Sand & Charcoal PDF generated successfully: {output_pdf_path} ({os.path.getsize(output_pdf_path) / 1024:.2f} KB)")


if __name__ == "__main__":
    generate_all_sand_slides()
