import pygame
import sys
import os
import asyncio
import ctypes
try:
    import cv2
    from ffpyplayer.player import MediaPlayer
    CAN_PLAY_VIDEO = True
except ImportError:
    CAN_PLAY_VIDEO = False
from minigames import SentinelsGame, MediaGame, LogisticsGame, FinanceGame, DocumentationGame, DevOpsGame

# Fix for high DPI displays on Windows to ensure correct resolution
ctypes.windll.user32.SetProcessDPIAware()

# Initialize pygame & mixer
pygame.init()
pygame.mixer.init()

# Game Constants
WIDTH, HEIGHT = 1280, 720
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
GREEN = (0, 255, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Founder's Retreat")
clock = pygame.time.Clock()

# Fonts (Trying to load custom font if it exists)
font_path = "images/PixelifySans-VariableFont_wght.ttf"
if os.path.exists(font_path):
    body_font = pygame.font.Font(font_path, 28)
    title_font = pygame.font.Font(font_path, 40)
    name_font = pygame.font.Font(font_path, 36)
else:
    body_font = pygame.font.Font(None, 32)
    title_font = pygame.font.Font(None, 48)
    name_font = pygame.font.Font(None, 40)

# States
STATE_SPLASH = "SPLASH"
STATE_VN = "VN"
STATE_MINIGAME_MENU = "MINIGAME_MENU"
STATE_MINIGAME_ACTIVE = "ACTIVE_MINIGAME"
STATE_CREDITS = "CREDITS"

# Load Images mapped to Ren'Py scene tags
BG_CACHE = {}
def get_bg(name):
    if name not in BG_CACHE:
        try:
            img = pygame.image.load(f"images/{name}.png").convert_alpha()
            BG_CACHE[name] = pygame.transform.scale(img, (WIDTH, HEIGHT))
        except:
            # Fallback to black surface if missing
            surf = pygame.Surface((WIDTH, HEIGHT))
            surf.fill(BLACK)
            BG_CACHE[name] = surf
    return BG_CACHE[name]

# Load CUIE Logo once
try:
    cuie_logo = pygame.image.load("images/logo.png").convert_alpha()
    cuie_logo = pygame.transform.scale(cuie_logo, (100, 92)) # Scale appropriately to cover gemini mark
except:
    cuie_logo = None

# Character Colors
CHAR_COLORS = {
    "FOUNDER": (132, 30, 70),  # #841e46
    "Count Roller": (132, 30, 70), # #841e46
    "Director": (74, 144, 226), # #4a90e2
    "Ex-Pres.": (200, 200, 200),
    "System": (0, 255, 255),
    "Intern": (255, 255, 255)
}

games_completed = {
    "Logistics": False,
    "DevOps": False, 
    "Sentinels": False,
    "Finance": False,
    "Media": False,
    "Documentation": False
}

recruited_vertical = None

# For testing, mark others true to skip ahead easier? 
# In a real build, these start False and you must beat them all.
def check_all_completed():
    return all(games_completed.values())

# Simple Visual Novel Manager
class VNEngine:
    def __init__(self):
        # Format: {"bg": bg_name, "speaker": name, "text": dialogue, "music": path, "sound": path, "next": None, "choices": []}
        self.script = [
            # ACT 0 & 1 Start
            {"bg": "01doorknock", "speaker": "", "text": "", "sound": "soundefx/doorknocksound.mp3", "next": None},
            {"bg": "02founderin", "speaker": "FOUNDER", "text": "Hey! You must be the new intern. I'm the Founder of CUIE. Listen, I've got an urgent situation.", "music": "audio/damnn.mp3", "next": None},
            {"bg": "02founderin", "speaker": "FOUNDER", "text": "There's a major ESports competition happening today. Our team qualified and I need to be there to support them. This is huge for the club!", "next": None},
            {"bg": "03founderhappy", "speaker": "FOUNDER", "text": "So here's the deal, you're going to be the Founder for the day.", "next": None},
            {"bg": "04foundershy", "speaker": "FOUNDER", "text": "I know it sounds crazy, but the Director will guide you through everything. Just handle two simple tasks that'll come your way. You got this!", "next": None},
            {"bg": "03founderhappy", "speaker": "FOUNDER", "text": "Good luck! The club is in your hands now!", "next": None},
            {"bg": "black", "speaker": "", "text": "", "next": None},
            
            # Mascot Intro
            {"bg": "05mascotpeek", "speaker": "Count Roller", "text": "Whoa, whoa, whoa! Did he just leave you in charge? Hi there! I'm Count Roller, the club's official mascot and your guide for today!", "next": None},
            {"bg": "06mascotshow", "speaker": "Count Roller", "text": "Let me give you the quick rundown about CUIE... We're Christ University Interactive Entertainment - the official ESports and Game Development Club.", "next": None},
            {"bg": "06mascotshow", "speaker": "Count Roller", "text": "We operate under SWO - the Student Welfare Office. We host tournaments, gaming events, development workshops, and pretty much anything gaming-related!", "next": None},
            {"bg": "06mascotshow", "speaker": "Count Roller", "text": "We've got an amazing community of gamers, developers, designers, and enthusiasts. From casual players to hardcore competitors, everyone's welcome here!", "next": None},
            {"bg": "05mascotpeek", "speaker": "Count Roller", "text": "Alright, the Director should be messaging you soon with your tasks. Don't worry, I'll be here to help you through this. Let's do this!", "next": None},
            
            # Director Task
            {"bg": "07directorintro", "speaker": "", "text": "", "sound": "soundefx/notificationsound.mp3", "next": None},
            {"bg": "08directortasks", "speaker": "", "text": "", "next": None},
            
            # Branches simulated for standard path
            {"bg": "09vendingmascot", "speaker": "Count Roller", "text": "Fuel up! You'll need energy for what's coming. What's your pick?", "next": None},
            {"bg": "11stangchoice", "speaker": "", "text": "", "next": None},
            {"bg": "12mansterchoice", "speaker": "", "text": "", "next": None},
            {"bg": "10vendingtask", "speaker": "Count Roller", "text": "So, what'll it be?", "choices": ["Manstar - Energy boost", "Stang - Maximum power"], "next": None},
            
            # Candidate Selection
            {"bg": "black", "speaker": "", "text": "", "next": None},
            {"bg": "15candidatemascot", "speaker": "Count Roller", "text": "Alright, let's see who we've got for the candidate selection...", "sound": "soundefx/notificationsound.mp3", "next": None},
            {"bg": "16candidatealex", "speaker": "", "text": "", "next": None},
            {"bg": "17candidatemarcus", "speaker": "", "text": "", "next": None},
            {"bg": "18candidatefelix", "speaker": "", "text": "", "next": None},
            {"bg": "19candidatechoice", "speaker": "Count Roller", "text": "Who do you think would be the best fit?", "choices": ["Alex - Sentinels", "Marcus - Logistics", "Felix - Content Creator"], "next": None},
            
            # Act 2
            {"bg": "20finaltask", "speaker": "", "text": "", "next": None},
            {"bg": "21firingtask", "speaker": "", "text": "", "next": None},
            {"bg": "22directorfinal", "speaker": "", "text": "", "sound": "soundefx/doorknocksound.mp3", "next": None},
            {"bg": "23expresident", "speaker": "", "text": "", "next": None},
            {"bg": "23expresident", "speaker": "Ex-Pres.", "text": "Hi! The director told me to talk to you, she told me that you are the new interim head of the club? I would love t....", "next": None},
            {"bg": "23expresident", "speaker": "", "text": "", "choices": ["YOU'RE FIRED!"], "music": "audio/endmusic.mp3", "next": None},
            {"bg": "24clubfire", "speaker": "Ex-Pres.", "text": "WHAT?! You can't do this to me!", "next": None},
            {"bg": "24clubfire", "speaker": "", "text": "", "sound": "soundefx/firesound.mp3", "next": None},
            {"bg": "25founderfire", "speaker": "FOUNDER", "text": "WHAT HAVE YOU DONE? THE WHOLE CLUB IS DEAD", "next": None},
            {"bg": "26clubover", "speaker": "FOUNDER", "text": "WE ARE SO COOKED", "next": None},
            {"bg": "27gameover", "speaker": "", "text": "", "music": "None", "sound": "soundefx/gameoversound.mp3", "next": None},
            
            # ACT 3 Setup
            {"bg": "28darkroom", "speaker": "Count Roller", "text": "Wait... what's happening?!", "music": "None", "sound": None, "next": None},
            {"bg": "28darkroom", "speaker": "Count Roller", "text": "You're not done yet. CUIE may be suspended in the real world... But in the DIGITAL VOID, the club still exists!", "next": None},
            {"bg": "28darkroom", "speaker": "Count Roller", "text": "Welcome to the DIGITAL REGISTRY - where the TRUE essence of CUIE lives!", "next": None},
            {"bg": "28darkroom", "speaker": "Count Roller", "text": "The room is locked, but the club is in the code. Let's reboot the Save State.", "next": None},
            {"bg": "verticals", "speaker": "System", "text": "Transitioning to Act 3: THE SYSTEM REGISTRY...", "next": STATE_MINIGAME_MENU},
            
            # ACT 4 Setup (Triggered once all games beat)
            {"bg": "35facultycoordinator", "speaker": "Count Roller", "text": "Verticals restored. Signal is green. Let’s go talk to the Final Boss.", "next": None},
            {"bg": "35facultycoordinator", "speaker": "Intern", "text": "Sir, you think CUIE is just a room in the Central Block. But we just rebuilt every vertical in the dark, with no power, in ten minutes.", "next": None},
            {"bg": "35facultycoordinator", "speaker": "Director", "text": "It’s a liability...", "next": None},
            {"bg": "35facultycoordinator", "speaker": "Intern", "text": "It’s the pulse of the campus. It’s where the misfits become leaders. You can't delete the players.", "next": None},
            {"bg": "35facultycoordinator", "speaker": "Count Roller", "text": "The kid’s got a High Score, Director. You gonna let 'em play, or is it Game Over for the best thing on campus?", "next": None},
            {"bg": "35facultycoordinator", "speaker": "Director", "text": "Fine. The suspension is lifted. Don't make me regret this.", "next": None},
            
            # ACT 5 Setup
            {"bg": "36clubrestore", "speaker": "System", "text": "ACT 5: THE HEROIC ENDING", "music": "audio/undertaleost.mp3", "next": None},
            {"bg": "37finalscene", "speaker": "System", "text": "The Rebuilt CUIE Office. Golden hour sunlight streaming in. Members are laughing and gaming.", "next": None},
            {"bg": "37finalscene", "speaker": "Count Roller", "text": "Not bad, kid. You handled the lag, beat the boss, and kept your cool.", "next": None},
            {"bg": "37finalscene", "speaker": "System", "text": "*Count Roller taps his gold joystick cane twice on the floor. CLACK-CLACK.*", "next": None},
            {"bg": "38theend", "speaker": "System", "text": "*A ring of neon light pulses out. Every monitor flashes the CUIE Logo.*", "next": None},
            {"bg": "38theend", "speaker": "System", "text": "THE CREDITS...", "next": STATE_CREDITS}
        ]
        self.current_line = 0
        self.active_choices = None

    def _fade_to_black(self, surface, speed=16):
        fade = pygame.Surface((WIDTH, HEIGHT))
        fade.fill(BLACK)
        for alpha in range(0, 256, speed):
            fade.set_alpha(alpha)
            surface.blit(fade, (0, 0))
            pygame.display.flip()
            clock.tick(FPS)

    def _fade_from_black(self, surface, speed=16):
        fade = pygame.Surface((WIDTH, HEIGHT))
        fade.fill(BLACK)
        for alpha in range(255, -1, -speed):
            self.draw(surface)
            fade.set_alpha(alpha)
            surface.blit(fade, (0, 0))
            pygame.display.flip()
            clock.tick(FPS)
        
    def start(self):
        self.handle_current_line()
        
    def handle_current_line(self):
        if self.current_line < len(self.script):
            line = self.script[self.current_line]
            
            if "music" in line:
                if line["music"] == "None" or line["music"] is None:
                    pygame.mixer.music.stop()
                else:
                    if os.path.exists(line["music"]):
                        pygame.mixer.music.load(line["music"])
                        pygame.mixer.music.play(-1)
            
            if "sound" in line and line["sound"]:
                if os.path.exists(line["sound"]):
                    s = pygame.mixer.Sound(line["sound"])
                    s.play()
                    
            if "choices" in line and line["choices"]:
                self.active_choices = line["choices"]
            else:
                self.active_choices = None

    def advance(self, surface=None):
        if self.active_choices: return STATE_VN # Prevent skip when choices exist
        
        if self.current_line < len(self.script):
            next_state = self.script[self.current_line].get("next")
            
            # Move to next line if we are not at the very end
            if self.current_line < len(self.script) - 1:
                self.current_line += 1
                self.handle_current_line()

                # Auto-handle transition markers: pure black, no text, no choices.
                if self.current_line < len(self.script):
                    line = self.script[self.current_line]
                    is_transition_black = (
                        line.get("bg") == "black"
                        and line.get("text", "").strip() == ""
                        and not line.get("choices")
                    )

                    if is_transition_black and self.current_line < len(self.script) - 1:
                        if surface is not None:
                            self._fade_to_black(surface)

                        # Skip the transition marker and move to next actual scene line.
                        self.current_line += 1
                        self.handle_current_line()

                        if surface is not None:
                            self._fade_from_black(surface)
            
            if next_state:
                return next_state
                
        return STATE_VN
        
    def select_choice(self, index, surface=None):
        self.active_choices = None
        
        # Inject dynamic branches
        if self.current_line < len(self.script):
            current_bg = self.script[self.current_line].get("bg", "")
            if current_bg == "10vendingtask":
                # Index 0 indicates Manstar, Index 1 indicates Stang
                if index == 0:
                    self.script.insert(self.current_line + 1, {"bg": "14mansterdirector", "speaker": "", "text": "", "next": None})
                else:
                    self.script.insert(self.current_line + 1, {"bg": "13stangdirector", "speaker": "", "text": "", "next": None})
            
            elif current_bg == "19candidatechoice":
                global recruited_vertical
                if index == 0:
                    recruited_vertical = "Sentinels"
                    self.script.insert(self.current_line + 1, {"bg": "19candidatechoice", "speaker": "Count Roller", "text": "Nice! They'll definitely boost our competitive scene!", "next": None})
                elif index == 1:
                    recruited_vertical = "Logistics"
                    self.script.insert(self.current_line + 1, {"bg": "19candidatechoice", "speaker": "Count Roller", "text": "Excellent! We need more technical talent on the team!", "next": None})
                elif index == 2:
                    recruited_vertical = "Media"
                    self.script.insert(self.current_line + 1, {"bg": "19candidatechoice", "speaker": "Count Roller", "text": "Great pick! Our online presence is about to level up!", "next": None})
                    
        return self.advance(surface)

    def draw_text_wrapped(self, surface, text, color, rect, font):
        words = text.split(' ')
        space_width = font.size(' ')[0]
        max_width, max_height = rect[2], rect[3]
        x, y = rect[0], rect[1]
        for word in words:
            word_surface = font.render(word, True, color)
            word_width, word_height = word_surface.get_size()
            if x + word_width >= rect[0] + max_width:
                x = rect[0]
                y += word_height
            surface.blit(word_surface, (x, y))
            x += word_width + space_width

    def draw(self, surface):
        if self.current_line < len(self.script):
            line = self.script[self.current_line]
            
            # BG
            if line["bg"] != "black":
                bg = get_bg(line["bg"])
                surface.blit(bg, (0, 0))
            else:
                surface.fill(BLACK)
            
            # Modern Cyber-Academia Text Box
            if line.get("text", "").strip() != "":
                box_width = WIDTH - 200
                box_height = 160
                box_x = 100
                box_y = HEIGHT - 180

                # Main Box Background with rounded corners
                s = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
                s.fill((15, 15, 25, 220)) # Deep dark blueish-black
                # Subtle inner highlight
                pygame.draw.rect(s, (255, 255, 255, 20), s.get_rect(), 4, border_radius=12)
                surface.blit(s, (box_x, box_y))
                
                # Glowing border effect
                pygame.draw.rect(surface, (0, 200, 255), (box_x, box_y, box_width, box_height), 2, border_radius=12)

                # Name Tag Window
                if line["speaker"]:
                    speaker_color = CHAR_COLORS.get(line["speaker"], WHITE)
                    name_w, name_h = name_font.size(line["speaker"])
                    name_rect = pygame.Rect(box_x + 30, box_y - name_h - 15, name_w + 60, name_h + 20)
                    
                    ns = pygame.Surface((name_rect.width, name_rect.height), pygame.SRCALPHA)
                    ns.fill((10, 10, 15, 240))
                    # Add a colored accent line at the bottom of the name tag
                    pygame.draw.rect(ns, speaker_color, (0, name_rect.height-4, name_rect.width, 4))
                    
                    surface.blit(ns, name_rect.topleft)
                    pygame.draw.rect(surface, speaker_color, name_rect, 2, border_radius=8)

                    speaker_surf = name_font.render(line["speaker"], True, speaker_color)
                    surface.blit(speaker_surf, (name_rect.x + 30, name_rect.y + 8))

                # Wrapped text (adjusted margins for new box)
                self.draw_text_wrapped(surface, line["text"], WHITE, (box_x + 40, box_y + 35, box_width - 80, box_height - 50), body_font)
            
            # Choices UI
            if self.active_choices:
                for i, choice in enumerate(self.active_choices):
                    y_pos = HEIGHT // 2 - (len(self.active_choices)*30) + (i * 70)
                    choice_rect = pygame.Rect(WIDTH//4, y_pos, WIDTH//2, 50)
                    
                    mouse_pos = pygame.mouse.get_pos()
                    color = (80, 80, 120) if choice_rect.collidepoint(mouse_pos) else (30, 30, 60)
                    
                    pygame.draw.rect(surface, color, choice_rect, border_radius=10)
                    pygame.draw.rect(surface, WHITE, choice_rect, 2, border_radius=10)
                    
                    t_surf = body_font.render(choice, True, WHITE)
                    t_rect = t_surf.get_rect(center=choice_rect.center)
                    surface.blit(t_surf, t_rect)

font = body_font # Fallback reference for minigames

vn_engine = VNEngine()
current_state = STATE_SPLASH
active_minigame = None
active_minigame_name = ""
active_minigame_start_time = 0

credit_index = 0
credits_data = [
    {"img": "39foundercredit", "text": "The Founder: Still hasn't figured out what he was\nactually doing during his Speedrun.\nHe's currently stuck on Level 1.\nHe is still very bad at it."},
    {"img": "40exprescredit", "text": "The Ex-President: Last seen trying to lead a club\nof one (himself).\nHe is currently arguing with his own reflection."},
    {"img": "41directorcredit", "text": "The Director: Currently trying to figure out how to\n'install Minecraft' for his nephew.\nHe still thinks the \"Creepers\" are a glitch."},
    {"img": "42mascotcredit", "text": "Count Roller: Has officially petitioned to be recognized\nas a faculty member. The petition was ignored.\nHe is currently \"borrowing\" the staff lounge's coffee machine."},
    {"img": "43interncredit", "text": "The Intern: Finally got their attendance sorted. Maybe.\nThe Registry is still \"Processing.\""},
    {"img": None, "text": "Thank you for playing.\nNow go join a vertical.\nWe need help with the next event."}
]

player = None
if CAN_PLAY_VIDEO and os.path.exists("images/booting_animation.webm"):
    try:
        player = MediaPlayer("images/booting_animation.webm")
    except Exception as e:
        print("Could not load video:", e)

async def fade_out_and_quit(surface):
    global running
    fade = pygame.Surface((WIDTH, HEIGHT))
    fade.fill((0, 0, 0))
    for alpha in range(0, 255, 5):
        fade.set_alpha(alpha)
        surface.blit(fade, (0, 0))
        pygame.display.flip()
        await asyncio.sleep(0.03)
    running = False

# Main loop

async def main():
    global current_state, active_minigame, active_minigame_name, active_minigame_start_time
    global credit_index, recruited_vertical, running, video_playing

    running = True
    video_playing = player is not None

    if not video_playing:
        vn_engine.start()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    if current_state == STATE_SPLASH:
                        current_state = STATE_VN
                        video_playing = False
                        if player: player.close_player()
                        vn_engine.start()
                    elif current_state == STATE_VN:
                        if not vn_engine.active_choices:
                            current_state = vn_engine.advance(screen)
                    elif current_state == STATE_CREDITS:
                        if credit_index < len(credits_data) - 1:
                            credit_index += 1
                        else:
                            await fade_out_and_quit(screen)
                    
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if current_state == STATE_SPLASH:
                    current_state = STATE_VN
                    video_playing = False
                    if player: player.close_player()
                    vn_engine.start()

                elif current_state == STATE_VN:
                    if vn_engine.active_choices:
                        # Handle VN Choice Clicking
                        for i, choice in enumerate(vn_engine.active_choices):
                            y_pos = HEIGHT // 2 - (len(vn_engine.active_choices)*30) + (i * 70)
                            choice_rect = pygame.Rect(WIDTH//4, y_pos, WIDTH//2, 50)
                            if choice_rect.collidepoint(event.pos):
                                current_state = vn_engine.select_choice(i, screen)
                                break
                    else:
                        current_state = vn_engine.advance(screen)

                elif current_state == STATE_MINIGAME_MENU:
                    mouse_x, mouse_y = event.pos
                    games = ["Logistics", "DevOps", "Sentinels", "Finance", "Media", "Documentation"]
                    for i, g in enumerate(games):
                        rect_x, rect_y = 260 + (i%3)*280, 250 + (i//3)*180
                        if rect_x <= mouse_x <= rect_x + 220 and rect_y <= mouse_y <= rect_y + 100:
                            if not games_completed[g]:
                                if g == "Sentinels":
                                    active_minigame = SentinelsGame()
                                elif g == "Media":
                                    active_minigame = MediaGame()
                                elif g == "Logistics":
                                    active_minigame = LogisticsGame()
                                elif g == "Finance":
                                    active_minigame = FinanceGame()
                                elif g == "Documentation":
                                    active_minigame = DocumentationGame()
                                elif g == "DevOps":
                                    active_minigame = DevOpsGame()
                                
                                active_minigame_name = g
                                current_state = STATE_MINIGAME_ACTIVE
                                active_minigame_start_time = pygame.time.get_ticks()
                                if globals().get('recruited_vertical') == active_minigame_name:
                                    active_minigame.impossible_mode = True
                            
                elif current_state == STATE_CREDITS:
                    if credit_index < len(credits_data) - 1:
                        credit_index += 1
                    else:
                        await fade_out_and_quit(screen)
                                
            if current_state == STATE_MINIGAME_ACTIVE and active_minigame:
                # Delegate event to the active game class
                won = active_minigame.handle_event(event)
                if won:
                    games_completed[active_minigame_name] = True
                    if check_all_completed():
                        current_state = STATE_VN # Move to Act 4
                    else:
                        current_state = STATE_MINIGAME_MENU # Go back to hub
                    active_minigame = None

        # Update logic (independent of events)
        if current_state == STATE_MINIGAME_ACTIVE and active_minigame:
            won = active_minigame.update()
        
            # Check for recruited vertical impossible mode threshold (30-40 misses)
            if globals().get('recruited_vertical') == active_minigame_name:
                if getattr(active_minigame, 'miss_count', 0) >= 35:
                
                    speaker_name = "Recruit"
                    dialog_text = "Hey boss, looks like you're struggling. Let me use my skills to handle this vertical for you!"
                    if active_minigame_name == "Sentinels":
                        speaker_name = "Alex"
                    elif active_minigame_name == "Logistics":
                        speaker_name = "Marcus"
                    elif active_minigame_name == "Media":
                        speaker_name = "Felix"

                    return_state = STATE_MINIGAME_MENU
                
                    new_line_1 = {"bg": "19candidatechoice", "speaker": speaker_name, "text": "Hey boss, looks like you're struggling.", "next": None}
                
                    # Mark complete so next state logic handles it correctly
                    games_completed[active_minigame_name] = True
                
                    if check_all_completed():
                        return_state = STATE_VN
                    else:
                        return_state = STATE_MINIGAME_MENU

                    new_line_2 = {"bg": "19candidatechoice", "speaker": speaker_name, "text": "Let me use my skills to handle this vertical for you!", "next": return_state}
                
                    vn_engine.current_line += 1
                    vn_engine.script.insert(vn_engine.current_line, new_line_1)
                    vn_engine.script.insert(vn_engine.current_line + 1, new_line_2)
                
                    # Make sure check_all_completed is updated before we end the script snippet
                    if check_all_completed():
                        new_line_2["next"] = STATE_VN
                
                    vn_engine.handle_current_line()
                    current_state = STATE_VN
                    active_minigame = None
                    won = False

            # Some games evaluate win condition in update
            if won:
                games_completed[active_minigame_name] = True
                if check_all_completed():
                    current_state = STATE_VN
                else:
                    current_state = STATE_MINIGAME_MENU
                active_minigame = None

        # Update & Render based on State
        if current_state == STATE_SPLASH:
            if video_playing and player:
                frame, val = player.get_frame()
                if val == 'eof':
                    video_playing = False
                    player.close_player()
                    current_state = STATE_VN
                    vn_engine.start()
                elif frame is not None:
                    img, t = frame
                    data = img.to_memoryview()[0]
                    surf = pygame.image.frombuffer(data, img.get_size(), 'RGB')
                    surf = pygame.transform.scale(surf, (WIDTH, HEIGHT))
                    screen.blit(surf, (0, 0))
            elif not video_playing:
                current_state = STATE_VN
                vn_engine.start()

        elif current_state == STATE_VN:
            vn_engine.draw(screen)
        
        elif current_state == STATE_MINIGAME_MENU:
            # Hub Image matching vertical theme
            bg = get_bg("verticals")
            screen.blit(bg, (0, 0))
        
            # Semi-transparent overlay to make buttons readable
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0,0))
        
            title = title_font.render("ACT 3: THE SYSTEM REGISTRY (MINIGAMES)", True, (0, 255, 255))
            instruction = body_font.render("Click a vertical to restore it. Restore all 6 to proceed!", True, WHITE)
        
            screen.blit(title, (WIDTH//2 - title.get_width()//2, 80))
            screen.blit(instruction, (WIDTH//2 - instruction.get_width()//2, 140))
        
            # Draw minigame alpha boxes
            games = ["Logistics", "DevOps", "Sentinels", "Finance", "Media", "Documentation"]
            for i, g in enumerate(games):
                rect = pygame.Rect(260 + (i%3)*280, 250 + (i//3)*180, 220, 100)
            
                btn_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                if games_completed[g]:
                    btn_surf.fill((0, 255, 0, 180)) # Translucent Green
                else:
                    btn_surf.fill((0, 100, 100, 180)) # Translucent Teal
                
                screen.blit(btn_surf, rect.topleft)
                pygame.draw.rect(screen, WHITE, rect, 3, border_radius=10)
                
                g_text = name_font.render(g, True, BLACK if games_completed[g] else WHITE)
                text_rect = g_text.get_rect(center=rect.center)
                screen.blit(g_text, text_rect)
            
        elif current_state == STATE_MINIGAME_ACTIVE and active_minigame:
            bg_mapping = {
                "Logistics": "29logisticsgame",
                "Finance": "30financegame",
                "DevOps": "31devopsgame",
                "Media": "32mediagame",
                "Sentinels": "33sentinelsgame",
                "Documentation": "34documentationgame"
            }
            bg = get_bg(bg_mapping.get(active_minigame_name, "28darkroom"))
            screen.blit(bg, (0, 0))
        
            # Transparent overlay for visibility
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0,0))
        
            active_minigame.draw(screen, font)
        
        elif current_state == STATE_CREDITS:
            screen.fill(BLACK)
            if credit_index < len(credits_data):
                c_data = credits_data[credit_index]
            
                # Left half for image, scaled gracefully to max half-screen size
                if c_data.get("img"):
                    bg_image = get_bg(c_data["img"])
                    iw, ih = bg_image.get_size()
                
                    # Limit the image bounding box to fit cleanly in the left 50% of screen
                    max_w = (WIDTH // 2) - 100
                    max_h = HEIGHT - 200
                    scale = min(max_w / iw, max_h / ih)
                
                    new_w, new_h = int(iw * scale), int(ih * scale)
                    scaled_img = pygame.transform.scale(bg_image, (new_w, new_h))
                
                    # Center the image vertically and horizontally within the left half
                    img_x = (WIDTH // 4) - (new_w // 2)
                    img_y = (HEIGHT // 2) - (new_h // 2)
                    screen.blit(scaled_img, (img_x, img_y))
            
                # Right half for text
                words = c_data["text"].split(": ", 1)
                if len(words) == 2:
                    name_surf = title_font.render(words[0].upper(), True, (0, 255, 255))
                
                    # Base Y coordinate to center the entire text block roughly
                    base_y = HEIGHT // 2 - 80 
                    screen.blit(name_surf, (WIDTH//2 + 20, base_y))
                
                    # Handle multi-line descriptions manually separated by \n
                    desc_lines = words[1].split("\n")
                    for i, d_line in enumerate(desc_lines):
                        desc_surf = body_font.render(d_line, True, WHITE)
                        screen.blit(desc_surf, (WIDTH//2 + 20, base_y + 50 + i * 35))
                else:
                    desc_lines = c_data["text"].split("\n")
                    for i, d_line in enumerate(desc_lines):
                        text_surf = title_font.render(d_line, True, WHITE)
                        screen.blit(text_surf, (WIDTH//2 - text_surf.get_width()//2, HEIGHT//2 - 50 + i * 45))
            
                instr = name_font.render("Click anywhere to continue...", True, (100, 100, 100))
                screen.blit(instr, (WIDTH - instr.get_width() - 50, HEIGHT - 50))

        if current_state != STATE_SPLASH and cuie_logo is not None:
            screen.blit(cuie_logo, (WIDTH - 120, HEIGHT - 110))

        pygame.display.flip()
        await asyncio.sleep(0)
        clock.tick(FPS)


    pygame.quit()

if __name__ == '__main__':
    asyncio.run(main())
