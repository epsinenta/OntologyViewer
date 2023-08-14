""" Модули для отрисовки окна """
import pygame
from pygame import Surface

import settings# pylint: disable=E0401
from Classes.textlink import TextLink# pylint: disable=E0401
from settings import colors, MAIN_FONT# pylint: disable=E0401
from utils import morph_convert# pylint: disable=E0401
from Classes.windowstring import WindowString# pylint: disable=E0401


class SliderWindow:
    """ Класс окна с панелью листания """

    def __init__(self, params: tuple,
                 params_with_text: tuple, screen: Surface,
                 text_color: tuple = colors['dark_purple']):
        """Инициализация кнопки
        :param params: геометрические параметры
        :type params: tuple
        :param screen: Экран, где рисуется окно
        :type screen: Surface
        :param text_color: Цвет строк
        :type text_color: tuple
        """
        self.x_coordinate = params[0]
        self.y_coordinate = params[1]
        self.width = params[2]
        self.height = params[3]
        self.lines = sorted(params_with_text[0])
        self.limit = params_with_text[1]
        self.word =  params_with_text[2]
        self.screen = screen
        self.links = []
        self.vertical_delta = 0
        self.horizontal_delta = 0
        self.slider_y = 0
        self.slider_x = 0
        self.vertical_pressed = False
        self.horizontal_pressed = False
        self.surf = pygame.Surface((self.width, self.height), pygame.RESIZABLE)# pylint: disable=E1101
        self.pos = [self.x_coordinate, self.y_coordinate]
        self.vertical_slider_size = 0
        self.horizontal_slider_size = 0
        self.pressed_link = None
        self.text_color = text_color
        self.old_y = None
        self.old_lines = None
        self.old_x = None
        self.texts = []
        self.old_texts = None

    def is_over_vertical(self, pos):
        """ Функция проверки нахождения мыши на ползунке """
        if self.width - 20 * settings.WIDTH_SCALE < pos[0] - self.x_coordinate < self.width:
            if 0 < pos[1] - self.y_coordinate < self.height:
                return True
        return False

    def is_over_horizontal(self, pos):
        """ Функция проверки нахождения мыши на ползунке """
        if self.height - 20 * settings.HEIGHT_SCALE < pos[1] - self.y_coordinate < self.height:
            if 0 < pos[0] - self.x_coordinate < self.width:
                return True
        return False

    def draw(self):
        """ Функция отрисовки окна """
        self.surf.fill(colors['background'])
        if self.lines:
            max_len = 1
            font = pygame.font.SysFont(MAIN_FONT,
                                       int(30 * settings.HEIGHT_SCALE * settings.WIDTH_SCALE))
            for line in self.lines:
                if isinstance(line, list):
                    line = line[0]
                render_line = font.render(line, True, colors['black'])
                if render_line.get_width() > max_len:
                    max_len = render_line.get_width()
            self.vertical_slider_size = self.limit * settings.HEIGHT_SCALE\
                                        * self.height / len(self.lines)
            self.horizontal_slider_size = self.width * self.width * settings.WIDTH_SCALE / max_len
            self.vertical_delta = -self.slider_y * len(self.lines) / self.limit
            self.horizontal_delta = -self.slider_x * max_len / self.width * settings.WIDTH_SCALE
            x_coordinate = int(self.horizontal_delta + 2) * settings.WIDTH_SCALE
            y_coordinate = int(self.vertical_delta + 2) * settings.HEIGHT_SCALE
            y_coordinate = min(y_coordinate, 0)
            if self.text_color == colors['dark_blue']:
                if self.old_y != self.vertical_delta or self.old_x != self.horizontal_delta\
                        or self.old_lines != self.lines or self.old_texts != self.texts:
                    self.links = []
                    self.texts = []
                    for line in self.lines:
                        if -40 < y_coordinate < self.height + 50:
                            result = line
                            pygame.font.init()
                            font = pygame.font.SysFont(MAIN_FONT, int(30 * settings.HEIGHT_SCALE
                                                                      * settings.WIDTH_SCALE))
                            result1 = morph_convert(result[0], result[0])[:-1]
                            text = WindowString(x_coordinate, y_coordinate, result1, self.surf)
                            self.texts.append(text)
                            text.draw()
                            link = TextLink((x_coordinate, y_coordinate),
                                            (result[1],
                                            int(30 * settings.HEIGHT_SCALE * settings.WIDTH_SCALE),
                                            self.text_color), self.surf,
                                            (self.x_coordinate, self.y_coordinate))
                            link.draw()
                            self.links.append(link)
                            for index in range(len(result1)):
                                if result1[index:] == result[2].replace('_', ' ').replace('№', '#'):
                                    render = font.render(result1[:index], True, colors['black'])
                                    width = render.get_width()
                                    link = TextLink((x_coordinate + width, y_coordinate),
                                                    (result[2].replace('_', ' ').replace('№', '#'),
                                                     int(30 * settings.HEIGHT_SCALE *
                                                         settings.WIDTH_SCALE),
                                                     self.text_color), self.surf,
                                                    (self.x_coordinate, self.y_coordinate))
                                    link.draw()
                                    self.links.append(link)
                            y_coordinate += 35 * settings.HEIGHT_SCALE * settings.WIDTH_SCALE
                        else:
                            y_coordinate += 35 * settings.HEIGHT_SCALE * settings.WIDTH_SCALE
                else:
                    for text in self.texts:
                        text.draw()
                    for link in self.links:
                        link.draw()
            else:
                if (self.old_y != self.vertical_delta or self.old_x != self.horizontal_delta)\
                        or self.old_lines != self.lines:
                    self.links = []
                    for line in self.lines:
                        if -40 < y_coordinate < self.height + 50:
                            link = TextLink((x_coordinate, y_coordinate), (line,
                                            int(30 * settings.HEIGHT_SCALE * settings.WIDTH_SCALE),
                                            self.text_color), self.surf,
                                            (self.x_coordinate, self.y_coordinate), self.word)
                            y_coordinate += 35 * settings.HEIGHT_SCALE * settings.WIDTH_SCALE
                            self.links.append(link)
                            link.draw()
                        else:
                            y_coordinate += 35 * settings.HEIGHT_SCALE * settings.WIDTH_SCALE
                else:
                    for link in self.links:
                        link.draw()
            self.old_x = self.horizontal_delta
            self.old_y = self.vertical_delta
            self.old_lines = self.lines
            self.old_texts = self.texts
            if int(self.limit) <= len(self.lines):
                slider = pygame.Surface((10 * settings.WIDTH_SCALE, self.vertical_slider_size),
                                        pygame.SRCALPHA)# pylint: disable=E1101
                slider.fill((200, 200, 200, 100))
                self.surf.blit(slider, (self.width - 10 * settings.WIDTH_SCALE, self.slider_y))
            if int(max_len) > self.width:
                slider = pygame.Surface((self.horizontal_slider_size, 10 * settings.HEIGHT_SCALE),
                                        pygame.SRCALPHA)# pylint: disable=E1101
                slider.fill((200, 200, 200, 100))
                self.surf.blit(slider, (self.slider_x, self.height - 10 * settings.HEIGHT_SCALE))
        if self.pressed_link is not None:
            link = self.pressed_link
            x_coordinate = link.x_coordinate + self.horizontal_delta
            y_coordinate = link.y_coordinate - 35 * settings.HEIGHT_SCALE
            font = pygame.font.SysFont(MAIN_FONT, link.font_size)
            for line in [link.text.replace('_', ' ')]:
                if len(line) > 0:
                    if line[-1] == ' ':
                        line = line[:-1]
                    if self.word:
                        line = morph_convert(line, self.word)
                    render_line = font.render(line, True, link.over_color)
                    self.surf.blit(
                        render_line,
                        (
                            x_coordinate, y_coordinate
                        )
                    )
                    y_coordinate += 35 * settings.HEIGHT_SCALE
        self.screen.blit(self.surf, (self.x_coordinate, self.y_coordinate))
