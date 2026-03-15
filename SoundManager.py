
import pygame
import os

class SoundManager:
    def __init__(self):
        # Initialize the mixer if not already done
        if not pygame.mixer.get_init():
            pygame.mixer.init()

        # Storage for sound effect objects
        self.sounds = {}
        
        # Volume settings (0.0 to 1.0)
        self.sfx_volume = 0.5
        self.music_volume = 0.3

        # Load sounds - Replace paths with your actual filenames
        self.load_sfx("shoot", "assets/sounds/shoot.mp3")
        self.load_sfx("hit", "assets/sounds/hit.mp3")
        self.load_sfx("zombie_die", "assets/sounds/death.mp3")
        self.load_sfx("engine", "assets/sounds/engine.mp3")
        self.load_sfx("pickup", "assets/sounds/pickup.mp3")
        self.engine_channel = None
        self.screech_sound = pygame.mixer.Sound("assets/sounds/screech.mp3")
        self.screech_channel = pygame.mixer.Channel(2)
    def play_sfx(self, name):
            """Plays a sound effect by its dictionary key."""
            if name in self.sounds:
                # We use the current sfx_volume setting
                self.sounds[name].set_volume(self.sfx_volume)
                self.sounds[name].play()
            else:
                # CS Tip: Print a debug message if you try to play a missing sound
                print(f"Logic Error: Sound '{name}' not loaded in SoundManager")
    def play_engine(self, speed_ratio):
        """Manages the continuous engine loop."""
        if "engine" in self.sounds:
            # 1. Start the sound if it's not already playing
            if self.engine_channel is None or not self.engine_channel.get_busy():
                # -1 means loop forever
                self.engine_channel = self.sounds["engine"].play(loops=-1)
            
            # 2. Dynamic Volume: The faster you go, the louder it gets
            # We add a base volume (0.2) so it doesn't go silent when idling
            if self.engine_channel:
                volume = 0.2 + (speed_ratio * 0.8)
                self.engine_channel.set_volume(volume * self.sfx_volume)
    def load_sfx(self, name, path):
        if os.path.exists(path):
            self.sounds[name] = pygame.mixer.Sound(path)
            self.sounds[name].set_volume(self.sfx_volume)
        else:
            print(f"Warning: Sound file not found at {path}")

    def play_music(self, path, loops=-1):
        """Starts background music streaming."""
        if os.path.exists(path):
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(loops)

    def play_sfx(self, name):
        """Plays a sound effect by its dictionary key."""
        if name in self.sounds:
            self.sounds[name].play()

    def set_sfx_volume(self, volume):
        self.sfx_volume = volume
        for sound in self.sounds.values():
            sound.set_volume(volume)

    def set_music_volume(self, volume):
        self.music_volume = volume
        pygame.mixer.music.set_volume(volume)

    def play_screech(self, volume):
        if not self.screech_channel.get_busy():
            self.screech_channel.play(self.screech_sound, loops=-1)
        self.screech_channel.set_volume(volume)

    def stop_screech(self):
        self.screech_channel.stop()