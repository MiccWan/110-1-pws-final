import pygame
from .BasicObject import BasicObject
from pygame.color import THECOLORS

pygame.font.init()

fonts = {
    'Title': pygame.font.SysFont('Arial', 56),
    'Normal': pygame.font.SysFont('Arial', 32)
}


class Text(BasicObject):
    def __init__(self, content, font_type, center_x, center_y, color=THECOLORS["white"], background_color=None):
        self.color = color
        self.geometry = fonts[font_type].render(
            content, True, color, background_color)
        self.center = (center_x, center_y)

    def render(self, screen):
        screen.blit(self.geometry, self.geometry.get_rect(center=self.center))
