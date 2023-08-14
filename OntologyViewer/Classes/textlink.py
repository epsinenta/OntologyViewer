""" Моудль отрисовки ссылок """
import pygame
from pygame import Surface
import settings # pylint: disable=E0401
from settings import colors, MAIN_FONT# pylint: disable=E0401
from utils import morph_convert# pylint: disable=E0401

class TextLink:
    """ Класс текста-ссылки"""

    def __init__(self, coordinates: tuple, other_params: tuple,
                 screen: Surface, delts: tuple, word = ''):
        """Инициализатор текста-ссылки
        :param coordinates: Координаты размещения текста
        :type coordinates: tuple
        :param other_params: стальные параметры ссылки
        :type other_params: tuple
        :param screen: Поверхность, на которой будет происходить отрисовка
        :type screen: Surface
        """
        self.x_coordinate = coordinates[0]
        self.y_coordinate = coordinates[1]
        self.text = other_params[0]
        self.font_size = other_params[1]
        self.over_color = other_params[2]
        self.screen = screen
        self.delts = delts
        self.word = word
        self.alt_text = ''
        self.start_y = self.y_coordinate

    def draw(self):
        """ Метод отрисовки текста-ссылки """
        pygame.font.init()
        font = pygame.font.SysFont(MAIN_FONT, self.font_size)
        if self.is_over(pygame.mouse.get_pos()):
            color = self.over_color
            line_color = color
        else:
            color = colors['black']
            line_color = colors['background']

        for line in [self.text.replace('_', ' ').replace('№', '#')]:
            if len(line) > 0:
                if line[-1] == ' ':
                    line = line[:-1]
                if self.word:
                    if not self.alt_text:
                        line = morph_convert(line, self.word)[:-1]
                        self.alt_text = line
                    else:
                        line = self.alt_text
                        self.y_coordinate = self.start_y
                else:
                    self.y_coordinate = self.start_y
                render_line = font.render(line, True, color)
                self.screen.blit(
                    render_line,
                    (
                        self.x_coordinate, self.y_coordinate
                    )
                )
                width = render_line.get_width()
                height = render_line.get_height()
                if self.over_color != colors['black']:
                    pygame.draw.line(self.screen, line_color,
                                     [self.x_coordinate, self.y_coordinate + height],
                                     [self.x_coordinate + width, self.y_coordinate + height], 2)
                self.y_coordinate += 35 * settings.HEIGHT_SCALE

    def is_over(self, pos: tuple):
        """ Проверка координат на нахождение внутри области текста-ссылки
        :param pos: Координаты курсора на экране
        :type pos: tuple
        :return: True, если Абсцисса и Ордината находится в области текста-ссылки, иначе False.
        """
        pygame.font.init()
        coefficient = 1
        font = pygame.font.SysFont(MAIN_FONT, self.font_size)
        render_line = font.render(self.text, True, colors['black'])
        width = render_line.get_width()
        height = render_line.get_height()
        if self.x_coordinate < pos[0] - self.delts[0] < self.x_coordinate + width:
            if self.y_coordinate - 35 * settings.HEIGHT_SCALE < pos[1] - self.delts[1]\
                    < self.y_coordinate - 35 * settings.HEIGHT_SCALE + height * coefficient:
                return True
        return False
