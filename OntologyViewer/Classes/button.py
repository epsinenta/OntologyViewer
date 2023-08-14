""" Модули для визуализации """
import pygame
from pygame import Surface
from settings import MAIN_FONT# pylint: disable=E0401
from utils import is_over# pylint: disable=E0401
import settings# pylint: disable=E0401

class Button:
    """ Класс кнопки """

    def __init__(self, params: tuple, colors: tuple, text: str, screen: Surface):
        """Инициализация кнопки
        :param params: все геометрические параметры
        :type params: tuple(int, int, int, int)
        :param colors: Цвета заливки кнопки
        :type colors: tuple
        :param text: Текст кнопки
        :type text: str
        :param screen: Поверхность, на которой будет происходить отрисовка
        :type screen: Surface
        """
        self.x_coordinate = params[0]
        self.y_coordinate = params[1]
        self.width = params[2]
        self.height = params[3]
        self.colors = colors
        self.text = text
        self.screen = screen

    def draw(self):
        """ Метод отрисовки кнопки на экране """
        if is_over(self, pygame.mouse.get_pos()):
            color = self.colors[1]
            outline = self.colors[2]
            if self.colors[0] == self.colors[2]:
                outline = color
        else:
            outline = self.colors[2]
            color = self.colors[0]

        pygame.draw.rect(self.screen, outline, (self.x_coordinate - 2,
                                                self.y_coordinate - 2,
                                                self.width + 4, self.height + 4), 0)
        pygame.draw.rect(self.screen, color, (self.x_coordinate, self.y_coordinate,
                                              self.width, self.height), 0)

        pygame.font.init()
        font = pygame.font.SysFont(MAIN_FONT,
                                   int(30 * settings.WIDTH_SCALE * settings.HEIGHT_SCALE))
        render_line = font.render(self.text, True, self.colors[3])
        self.screen.blit(
            render_line,
            (
                self.x_coordinate + (self.width / 2 - render_line.get_width() / 2),
                self.y_coordinate + (self.height / 2 - render_line.get_height() / 2)
            )
        )

    def button_on_window(self) -> bool:
        """Метод проверки на наличие кнопки на экране
        :return True, если кнопка видна, иначе False
        """
        if self.x_coordinate + self.width > 0 and self.y_coordinate + self.height > 0:
            return True
        return False
