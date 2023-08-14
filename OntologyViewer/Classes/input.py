""" Модули для визуализации поля ввода """
import pygame
from pygame import Surface
import settings# pylint: disable=E0401
from settings import colors, MAIN_FONT# pylint: disable=E0401

class Input:
    """ Класс поля ввода """

    def __init__(self, params: tuple,
                 outline: tuple, screen: Surface, description: str = ''):
        """Инициализация поля ввода

        :param params: геометрические параметры
        :type params: tuple
        :param outline: Цвет обводки поля
        :type outline: COLOR
        :param screen: Поверхность, на которой будет происходить отрисовка
        :type screen: Surface
        :param description: Объяснение поля
        :type description: str
        """
        self.x_coordinate = params[0]
        self.y_coordinate = params[1]
        self.width = params[2]
        self.height = params[3]
        self.text = ''
        self.other_params = [outline, False, 0, description]
        self.screen = screen

    def draw(self):
        """Метод отрисовки поля ввода на экране """
        pygame.font.init()
        font = pygame.font.SysFont(MAIN_FONT,
                                   int(30 * settings.WIDTH_SCALE * settings.HEIGHT_SCALE))
        if self.other_params[0]:
            pygame.draw.rect(self.screen, self.other_params[0], (self.x_coordinate - 2,
                                                         self.y_coordinate - 2,
                                                         self.width + 4, self.height + 4),
                             0)

        color = colors['background']
        pygame.draw.rect(self.screen, color, (self.x_coordinate, self.y_coordinate,
                                              self.width, self.height), 0)

        result = ''
        if self.text != "":
            result = self.text
            render_line = font.render(result, True, colors['black'])
            while render_line.get_width() > self.width * 0.9:
                result = f'...{result[4:]}'
                render_line = font.render(result, True, colors['black'])

        elif not self.other_params[1] and self.text == '':
            result = self.other_params[3]

        if self.other_params[1]:
            self.other_params[2] += 1
            if self.other_params[2] % 80 < 40:
                result += '|'
            else:
                result += ' '
        if self.text != '' or self.other_params[1]:
            color = colors['black']
        else:
            color = colors['light_grey']
        render_line = font.render(result, True, color)
        self.screen.blit(
            render_line,
            (
                self.x_coordinate + (self.width / 2 - render_line.get_width() / 2),
                self.y_coordinate + (self.height / 2 - render_line.get_height() / 2)
            )
        )

    def input_on_window(self) -> bool:
        """Метод проверки на наличие поля ввода на экране
        :return True, если кнопка видна, иначе False
        """
        if self.y_coordinate + self.height > 0 and self.x_coordinate + self.width > 0:
            return True
        return False
