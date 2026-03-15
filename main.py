import pygame
import sys
import random
from pathlib import Path
import importlib.util
import tempfile
import os
from Speedometer import draw_gauge
from settings import *
from world import World
from car import Car
from camera import Camera
from minimap import MiniMap
from mission import Mission
from particles import *
from Enemy import Enemy
from CombatSystem import CombatSystem
from SoundManager import SoundManager
from ui import *
from Buff import *

# Optional video playback for intro story
try:
    import cv2  # type: ignore
except Exception:
    cv2 = None

try:
    from moviepy.editor import VideoFileClip  # type: ignore
except Exception:
    VideoFileClip = None

# --- INITIALIZATION ---
pygame.init()
pygame.display.set_caption("Santa's Winter Journey - AI Defense")
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Buff System Setup
buffs = pygame.sprite.Group()
BUFF_SPAWN_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(BUFF_SPAWN_EVENT, 5000) 

# 1. Initialize World & UI
ui = UI()
world = World()
sounds = SoundManager()

# 2. Initialize Objects
car = Car(world.random_road_position())
combat_system = CombatSystem(car, sounds)
camera = Camera()
mission = Mission(world)
minimap = MiniMap(world)
particle_manager = ParticleManager()
snow = Snow()

# --- STORY VIDEO SETUP ---
class StoryVideo:
    def __init__(self, path: str, size, play_audio=False):
        self.path = Path(path)
        self.size = size
        self.cap = None
        self.fps = 30
        self.ms_per_frame = int(1000 / self.fps)
        self.last_tick = 0
        self.done = False
        self.last_surface = None
        self.play_audio = play_audio
        self.audio_path = None
        self.audio_started = False

        if cv2 is None or not self.path.exists():
            self.done = True
            return

        self.cap = cv2.VideoCapture(str(self.path))
        if not self.cap.isOpened():
            self.done = True
            self.cap = None
            return

        fps = self.cap.get(cv2.CAP_PROP_FPS)
        if fps and fps > 0:
            self.fps = fps
            self.ms_per_frame = int(1000 / self.fps)

        if self.play_audio and VideoFileClip is not None:
            try:
                clip = VideoFileClip(str(self.path))
                if clip.audio is not None:
                    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
                    tmp.close()
                    clip.audio.write_audiofile(tmp.name, logger=None)
                    self.audio_path = tmp.name
                clip.close()
            except Exception:
                self.audio_path = None
                self.play_audio = False

    def update(self, surface):
        if self.done or self.cap is None:
            return True

        now = pygame.time.get_ticks()
        if now - self.last_tick >= self.ms_per_frame:
            self.last_tick = now
            ret, frame = self.cap.read()
            if not ret:
                self.done = True
                self.cap.release()
                return True

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, self.size)
            self.last_surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))

        if self.last_surface is not None:
            surface.blit(self.last_surface, (0, 0))
        return False

    def start_audio(self):
        if self.audio_started or self.audio_path is None:
            return
        try:
            pygame.mixer.music.load(self.audio_path)
            pygame.mixer.music.play()
            self.audio_started = True
        except Exception:
            self.audio_started = False

    def stop_audio(self):
        if not self.audio_started:
            return
        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
        except Exception:
            pass
        self.audio_started = False
        if self.audio_path and os.path.exists(self.audio_path):
            try:
                os.remove(self.audio_path)
            except Exception:
                pass

story_video = StoryVideo("assets/story.mp4", (WIDTH, HEIGHT))

class LoopVideo:
    def __init__(self, path: str, size):
        self.path = Path(path)
        self.size = size
        self.cap = None
        self.fps = 30
        self.ms_per_frame = int(1000 / self.fps)
        self.last_tick = 0
        self.done = False
        self.last_surface = None
        self.last_size = None

        if cv2 is None or not self.path.exists():
            self.done = True
            return

        self.cap = cv2.VideoCapture(str(self.path))
        if not self.cap.isOpened():
            self.done = True
            self.cap = None
            return

        fps = self.cap.get(cv2.CAP_PROP_FPS)
        if fps and fps > 0:
            self.fps = fps
            self.ms_per_frame = int(1000 / self.fps)

    def _fit_size(self, frame_w, frame_h):
        sw, sh = self.size
        scale = min(sw / frame_w, sh / frame_h)
        return int(frame_w * scale), int(frame_h * scale)

    def update(self, surface):
        if self.done or self.cap is None:
            return

        now = pygame.time.get_ticks()
        if now - self.last_tick >= self.ms_per_frame:
            self.last_tick = now
            ret, frame = self.cap.read()
            if not ret:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = self.cap.read()
                if not ret:
                    self.done = True
                    self.cap.release()
                    return

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w = frame.shape[:2]
            target_w, target_h = self._fit_size(w, h)
            self.last_size = (target_w, target_h)
            frame = cv2.resize(frame, self.last_size)
            self.last_surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))

        if self.last_surface is not None:
            sw, sh = self.size
            fw, fh = self.last_surface.get_size()
            x = (sw - fw) // 2
            y = (sh - fh) // 2
            surface.blit(self.last_surface, (x, y))

_title_path = "assets/title_video.mp4"
if not Path(_title_path).exists():
    _title_path = "assets/title video.mp4"
title_video = LoopVideo(_title_path, (WIDTH, HEIGHT))

def run_level1():
    level1_path = Path("game (1).py")
    if not level1_path.exists():
        return False

    spec = importlib.util.spec_from_file_location("level1", str(level1_path))
    if spec is None or spec.loader is None:
        return False

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not hasattr(module, "run_level1"):
        return False

    return module.run_level1(screen, clock)

# 3. AI Enemies
enemies = pygame.sprite.Group()
def spawn_enemies():
    enemies.empty()
    for i in range(5):
        spawn_point = world.random_road_position()
        enemies.add(Enemy(spawn_point))

spawn_enemies()

# States
font = pygame.font.SysFont("arial", 32)
GAME_STATE = "STORY" if not story_video.done else "MENU"
score = 0
path_update_counter = 0
music_started = False
fade_alpha = 0
story2_video = StoryVideo("assets/story2.mp4", (WIDTH, HEIGHT), play_audio=True)
story2_sound_path = Path("assets/sounds/story2_sound.mp3")
story2_sound = pygame.mixer.Sound(str(story2_sound_path)) if story2_sound_path.exists() else None
story2_channel = None
story2_sound_started = False

paused = False
pause_mode = "MENU"

pause_title_font = pygame.font.SysFont("arial", 48, bold=True)
pause_font = pygame.font.SysFont("arial", 28)

def pause_ui_layout():
    panel = pygame.Rect(0, 0, 420, 360)
    panel.center = (WIDTH // 2, HEIGHT // 2)
    btn_w, btn_h = 220, 42
    resume = pygame.Rect(0, 0, btn_w, btn_h)
    options = pygame.Rect(0, 0, btn_w, btn_h)
    exit_btn = pygame.Rect(0, 0, btn_w, btn_h)
    resume.center = (panel.centerx, panel.y + 130)
    options.center = (panel.centerx, panel.y + 190)
    exit_btn.center = (panel.centerx, panel.y + 250)

    options_panel = pygame.Rect(0, 0, 380, 220)
    options_panel.center = (WIDTH // 2, HEIGHT // 2)
    options_close = pygame.Rect(options_panel.right - 38, options_panel.y + 10, 24, 24)

    music_minus = pygame.Rect(options_panel.x + 40, options_panel.y + 90, 30, 30)
    music_plus = pygame.Rect(options_panel.right - 70, options_panel.y + 90, 30, 30)
    sfx_minus = pygame.Rect(options_panel.x + 40, options_panel.y + 140, 30, 30)
    sfx_plus = pygame.Rect(options_panel.right - 70, options_panel.y + 140, 30, 30)

    return {
        "panel": panel,
        "resume": resume,
        "options": options,
        "exit": exit_btn,
        "options_panel": options_panel,
        "options_close": options_close,
        "music_minus": music_minus,
        "music_plus": music_plus,
        "sfx_minus": sfx_minus,
        "sfx_plus": sfx_plus,
    }

def draw_pause_panel(surface, mode):
    layout = pause_ui_layout()
    panel = layout["panel"]
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 120))
    surface.blit(overlay, (0, 0))
    pygame.draw.rect(surface, (180, 180, 180), panel, border_radius=12)
    pygame.draw.rect(surface, (100, 100, 100), panel, 2, border_radius=12)
    title = pause_title_font.render("PAUSED", True, (30, 30, 30))
    surface.blit(title, (panel.centerx - title.get_width() // 2, panel.y + 30))

    def draw_button(rect, text):
        pygame.draw.rect(surface, (230, 230, 230), rect, border_radius=8)
        pygame.draw.rect(surface, (120, 120, 120), rect, 2, border_radius=8)
        label = pause_font.render(text, True, (20, 20, 20))
        surface.blit(label, (rect.centerx - label.get_width() // 2, rect.centery - label.get_height() // 2))

    draw_button(layout["resume"], "RESUME")
    draw_button(layout["options"], "OPTIONS")
    draw_button(layout["exit"], "EXIT")

    if mode == "OPTIONS":
        opt = layout["options_panel"]
        pygame.draw.rect(surface, (190, 190, 190), opt, border_radius=10)
        pygame.draw.rect(surface, (100, 100, 100), opt, 2, border_radius=10)
        close_rect = layout["options_close"]
        pygame.draw.rect(surface, (230, 230, 230), close_rect, border_radius=6)
        pygame.draw.rect(surface, (120, 120, 120), close_rect, 2, border_radius=6)
        x_label = pause_font.render("X", True, (20, 20, 20))
        surface.blit(x_label, (close_rect.centerx - x_label.get_width() // 2, close_rect.centery - x_label.get_height() // 2))

        music = pause_font.render(f"Music: {int(sounds.music_volume * 100)}%", True, (30, 30, 30))
        sfx = pause_font.render(f"SFX: {int(sounds.sfx_volume * 100)}%", True, (30, 30, 30))
        surface.blit(music, (opt.x + 80, opt.y + 90))
        surface.blit(sfx, (opt.x + 80, opt.y + 140))

        for key in ("music_minus", "music_plus", "sfx_minus", "sfx_plus"):
            rect = layout[key]
            pygame.draw.rect(surface, (230, 230, 230), rect, border_radius=6)
            pygame.draw.rect(surface, (120, 120, 120), rect, 2, border_radius=6)
        minus = pause_font.render("-", True, (20, 20, 20))
        plus = pause_font.render("+", True, (20, 20, 20))
        surface.blit(minus, (layout["music_minus"].centerx - minus.get_width() // 2, layout["music_minus"].centery - minus.get_height() // 2))
        surface.blit(plus, (layout["music_plus"].centerx - plus.get_width() // 2, layout["music_plus"].centery - plus.get_height() // 2))
        surface.blit(minus, (layout["sfx_minus"].centerx - minus.get_width() // 2, layout["sfx_minus"].centery - minus.get_height() // 2))
        surface.blit(plus, (layout["sfx_plus"].centerx - plus.get_width() // 2, layout["sfx_plus"].centery - plus.get_height() // 2))
    return layout
# --- MAIN LOOP ---
while True:
    dt = clock.tick(FPS) / 1000
    keys = pygame.key.get_pressed()

    # --- 1. EVENT HANDLING ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        # UNIVERSAL SPAWN LOGIC (Checks every 5s regardless of state, but we only add if playing)
        if event.type == BUFF_SPAWN_EVENT and GAME_STATE == "PLAYING" and not paused:
            if len(buffs) < 10:
                spawn_pos = world.random_road_position()
                b_type = random.choice(["NITRO", "REPAIR", "SHIELD"])
                buffs.add(Buff(spawn_pos, b_type))

        if GAME_STATE == "PLAYING" and event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            paused = not paused
            pause_mode = "MENU"

        if GAME_STATE == "PLAYING" and paused and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            layout = pause_ui_layout()
            if layout["resume"].collidepoint(event.pos):
                paused = False
            elif layout["options"].collidepoint(event.pos):
                pause_mode = "OPTIONS" if pause_mode == "MENU" else "MENU"
            elif layout["exit"].collidepoint(event.pos):
                pygame.quit()
                sys.exit()

            if pause_mode == "OPTIONS":
                if layout["options_close"].collidepoint(event.pos):
                    pause_mode = "MENU"
                elif layout["music_minus"].collidepoint(event.pos):
                    sounds.set_music_volume(max(0.0, sounds.music_volume - 0.1))
                elif layout["music_plus"].collidepoint(event.pos):
                    sounds.set_music_volume(min(1.0, sounds.music_volume + 0.1))
                elif layout["sfx_minus"].collidepoint(event.pos):
                    sounds.set_sfx_volume(max(0.0, sounds.sfx_volume - 0.1))
                elif layout["sfx_plus"].collidepoint(event.pos):
                    sounds.set_sfx_volume(min(1.0, sounds.sfx_volume + 0.1))

        if GAME_STATE == "STORY":
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_SPACE, pygame.K_ESCAPE, pygame.K_RETURN):
                GAME_STATE = "MENU"
                if not music_started:
                    sounds.play_music("assets/sounds/bgm.mp3")
                    music_started = True

        elif GAME_STATE == "MENU":
            if event.type == pygame.KEYDOWN:
                GAME_STATE = "FADE_TO_HOWTO_L1"
                fade_alpha = 0
        
        elif GAME_STATE == "HOWTO_L1":
            if event.type == pygame.KEYDOWN:
                GAME_STATE = "LAUNCH_LEVEL1"

        elif GAME_STATE == "HOWTO_L2":
            if event.type == pygame.KEYDOWN:
                GAME_STATE = "FADE_TO_PLAYING"
                fade_alpha = 0

        elif GAME_STATE == "GAMEOVER":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                # Reset Logic
                car.health = 100
                car.nitro_charge = 100
                score = 0
                car.pos = pygame.math.Vector2(world.random_road_position())
                car.vel = pygame.math.Vector2(0,0)
                buffs.empty()
                spawn_enemies()
                GAME_STATE = "PLAYING"

    # --- 2. DRAWING PREP ---
    screen.fill((0, 0, 0)) 

    # ---------------- STATE: MENU ----------------
    if GAME_STATE == "STORY":
        screen.fill((0, 0, 0))
        finished = story_video.update(screen)
        if finished:
            GAME_STATE = "MENU"
            if not music_started:
                sounds.play_music("assets/sounds/bgm.mp3")
                music_started = True

    elif GAME_STATE == "MENU":
        screen.fill((0, 0, 0))
        if not title_video.done:
            title_video.update(screen)
        ui.draw_menu(screen, draw_bg=title_video.done)
        snow.update()
        snow.draw(screen)

    # ---------------- STATE: FADE TO HOWTO (L1) ----------------
    elif GAME_STATE == "FADE_TO_HOWTO_L1":
        screen.fill((0, 0, 0))
        if not title_video.done:
            title_video.update(screen)
        ui.draw_menu(screen, draw_bg=title_video.done)
        snow.update()
        snow.draw(screen)

        fade_alpha = min(fade_alpha + 6, 255)
        fade = pygame.Surface((WIDTH, HEIGHT))
        fade.fill((0, 0, 0))
        fade.set_alpha(fade_alpha)
        screen.blit(fade, (0, 0))
        if fade_alpha >= 255:
            GAME_STATE = "HOWTO_L1"

    # ---------------- STATE: HOWTO (L1) ----------------
    elif GAME_STATE == "HOWTO_L1":
        ui.draw_howto_level1(screen)

    # ---------------- STATE: LAUNCH LEVEL 1 ----------------
    elif GAME_STATE == "LAUNCH_LEVEL1":
        level1_won = run_level1()
        pygame.display.set_caption("Santa's Winter Journey - AI Defense")
        if level1_won is None:
            pygame.quit()
            sys.exit()
        if level1_won:
            pygame.mixer.music.stop()
            story2_video = StoryVideo("assets/story2.mp4", (WIDTH, HEIGHT), play_audio=True)
            story2_sound_started = False
            story2_channel = None
            if story2_video.done:
                sounds.play_music("assets/sounds/bgm.mp3")
                GAME_STATE = "HOWTO_L2"
            else:
                GAME_STATE = "STORY2"
        else:
            GAME_STATE = "MENU"

    # ---------------- STATE: STORY2 ----------------
    elif GAME_STATE == "STORY2":
        screen.fill((0, 0, 0))
        if not story2_sound_started and story2_sound is not None:
            story2_channel = story2_sound.play()
            story2_sound_started = True
        story2_video.start_audio()
        finished = story2_video.update(screen)
        if finished:
            story2_video.stop_audio()
            if story2_channel is not None:
                story2_channel.stop()
                story2_channel = None
            sounds.play_music("assets/sounds/bgm.mp3")
            GAME_STATE = "HOWTO_L2"

    # ---------------- STATE: HOWTO (L2) ----------------
    elif GAME_STATE == "HOWTO_L2":
        ui.draw_howto_level2(screen)

    # ---------------- STATE: FADE TO PLAYING ----------------
    elif GAME_STATE == "FADE_TO_PLAYING":
        ui.draw_howto_level2(screen)
        fade_alpha = min(fade_alpha + 6, 255)
        fade = pygame.Surface((WIDTH, HEIGHT))
        fade.fill((0, 0, 0))
        fade.set_alpha(fade_alpha)
        screen.blit(fade, (0, 0))
        if fade_alpha >= 255:
            GAME_STATE = "PLAYING"
            mission.generate_path(car.pos)

    # ---------------- STATE: PLAYING ----------------
    elif GAME_STATE == "PLAYING":
        if not paused:
            # --- LOGIC ---
            path_update_counter += 1
            speed_ratio = min(car.vel.length() / 10, 1.0)
            sounds.play_engine(speed_ratio)
            
            car.update(world, particle_manager)
            camera.update(car, world)
            particle_manager.update()
            combat_system.update(enemies) 
    
            # Buff Collisions
            hit_buffs = pygame.sprite.spritecollide(car, buffs, True)
            for buff in hit_buffs:
                buff.apply(car)
                sounds.play_sfx("pickup") 
            buffs.update()
    
            # Screech Logic
            is_on_road = world.is_road(car.pos.x, car.pos.y)
            if keys[pygame.K_SPACE] and car.vel.length() > 2.5 and is_on_road:
                vol = min((car.vel.length() - 2.5) / 5, 0.6)
                sounds.play_screech(vol)
            else:
                sounds.stop_screech()
    
            # Enemy Logic
            for enemy in enemies:
                enemy.update(car.pos)
                dist_vec = enemy.pos - car.pos
                if not enemy.is_dead and dist_vec.length() < 60:
                    if enemy.state == "attack":
                        car.health -= 10 * dt
                        if car.health <= 0: GAME_STATE = "GAMEOVER"
                    
                    # Physical Push
                    if dist_vec.length() < 35:
                        enemy.pos += dist_vec.normalize() * (35 - dist_vec.length())
    
            # Mission Logic
            if path_update_counter >= 30:
                mission.generate_path(car.pos)
                path_update_counter = 0
            if mission.check(car):
                score += 1
                mission.generate_path(car.pos)
            
            snow.update()
    
        # --- DRAWING ---
        world.draw(screen, camera)
        mission.draw(screen, camera)
        particle_manager.draw(screen, camera)
        combat_system.draw(screen, camera)
        
        # Draw Buffs
        for buff in buffs:
            screen.blit(buff.image, camera.apply(buff.rect))
            
        # Draw Enemies
        for enemy in enemies:
            screen.blit(enemy.image, camera.apply(enemy.rect))
            enemy.draw_health(screen, camera)

        # Draw Player
        screen.blit(car.image, camera.apply(car.rect))
        
        # UI Overlay
        ui.draw_hud(screen, car, score)
        ui.draw_nitro_bar(screen, car)
        draw_gauge(screen, car.smooth_speed, font)
        snow.draw(screen)
        minimap.draw(screen, car, mission)

        if paused:
            draw_pause_panel(screen, pause_mode)

    # ---------------- STATE: GAMEOVER ----------------
    elif GAME_STATE == "GAMEOVER":
        world.draw(screen, camera)
        ui.draw_game_over(screen, score)

    pygame.display.update()



