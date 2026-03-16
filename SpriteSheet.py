import pygame

class SpriteSheet:
    def __init__(self, filename, total_frames):
        self.sheet = pygame.image.load(filename).convert_alpha()
        
        # Calculate width: total width divided by number of frames
        self.frame_width = self.sheet.get_width() // total_frames
        
        # Height is just the full height of the PNG
        self.frame_height = self.sheet.get_height()
        
        self.total_frames = total_frames

    def get_image(self, frame_index, scale=1.0):
        # Create a blank surface for the frame
        image = pygame.Surface((self.frame_width, self.frame_height), pygame.SRCALPHA)
        
        # Slice the frame out
        image.blit(self.sheet, (0, 0), (frame_index * self.frame_width, 0, self.frame_width, self.frame_height))
        
        # Scale it up
        new_size = (int(self.frame_width * scale), int(self.frame_height * scale))
        return pygame.transform.scale(image, new_size)