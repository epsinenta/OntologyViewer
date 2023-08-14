""" Модули для рисования текста """
import pygame
import settings
from settings import MAIN_FONT
from settings import colors

class WindowString:
    """ Класс строки, является костылем """
    def __init__(self, x_coordinate, y_coordinate, text, screen):
        """ Метод инициализации строки """
        self.x_coordinate = x_coordinate
        self.y_coordinate = y_coordinate
        self.text = text
        self.screen = screen

    def draw(self):
        """ метод рисования строки"""
        pygame.font.init()
        font = pygame.font.SysFont(MAIN_FONT, int(30 * settings.HEIGHT_SCALE
                                                  * settings.WIDTH_SCALE))
        render_line = font.render(self.text, True, colors['black'])
        self.screen.blit(
            render_line,
            (
               self.x_coordinate, self.y_coordinate
            )
        )
