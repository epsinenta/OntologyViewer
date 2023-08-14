""" Модуль для отрисовки таблички """
import pygame
from pygame import Surface
from utils import cut_the_string, is_over # pylint: disable=E0401
import settings# pylint: disable=E0401

from settings import colors, MAIN_FONT# pylint: disable=E0401

class Docket:
    """ Класс таблички для классификатора или экземпляра """

    def __init__(self, params: tuple,
                 other_params: tuple,
                 screen: Surface):
        """Инициализация таблички

        :param params: все геометрические параметры
        :type params: tuple(int, int, int, int)
        :param other_params: остальные параметры
        :type other_params: tuple
        :param screen: Поверхность, на которой будет происходить отрисовка
        :type screen: Surface
        """
        self.x_coordinate = params[0]
        self.y_coordinate = params[1]
        self.width = params[2]
        self.height = params[3]
        self.other_params = other_params
        self.screen = screen

    def draw(self):
        """ Метод отрисовки таблички на экран """
        if is_over(self, pygame.mouse.get_pos()):
            color = colors['very_light_grey']
        else:
            color = colors['background']

        pygame.draw.rect(self.screen, self.other_params[0], (self.x_coordinate - 2,
                                                     self.y_coordinate - 2,
                                                     self.width + 4, self.height + 4),
                         0)
        pygame.draw.rect(self.screen, color, (self.x_coordinate, self.y_coordinate,
                                              self.width, self.height), 0)

        pygame.font.init()
        font = pygame.font.SysFont(MAIN_FONT,
                                   int(30 * settings.HEIGHT_SCALE * settings.WIDTH_SCALE))
        delta_y = 30 * settings.HEIGHT_SCALE
        second_delta_y = 25 * settings.HEIGHT_SCALE
        result = self.other_params[1]
        if len(result) > int(25):
            result = self.other_params[1][:int(25)] + '...'
        if len(cut_the_string(result, 19)) == 1:
            delta_y = 10 * settings.HEIGHT_SCALE
            second_delta_y = 15 * settings.HEIGHT_SCALE
        strings = cut_the_string(result, 19)
        if len(strings) > 2:
            strings = strings[:2]
            strings[1] += '...'
        for line in strings:
            if len(line) > 19:
                if line[-1] != '.':
                    line = line[:int(17)] + '...'
            render_line = font.render(line, True, colors['black'])
            self.screen.blit(
                render_line,
                (
                    self.x_coordinate + (self.width / 2 - render_line.get_width() / 2),
                    self.y_coordinate + (self.height / 2 - render_line.get_height() / 2) - delta_y
                )
            )
            delta_y -= 30 * settings.HEIGHT_SCALE

        font = pygame.font.SysFont(MAIN_FONT,
                                   int(20 * settings.HEIGHT_SCALE * settings.WIDTH_SCALE))
        render_line = font.render(self.other_params[2], True, self.other_params[3])
        self.screen.blit(
            render_line,
            (
                self.x_coordinate + (self.width / 2 - render_line.get_width() / 2),
                self.y_coordinate + (self.height / 2 - render_line.get_height() / 2)
                + second_delta_y
            )
        )

    def docket_on_window(self) -> bool:
        """Метод проверки на наличие таблички на экране
        :return True, если кнопка видна, иначе False
        """
        if self.y_coordinate + self.height > 0 and self.x_coordinate + self.width > 0:
            return True
        return False
