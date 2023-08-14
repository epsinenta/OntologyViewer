""" Модули для использования и отображения данных модули """
import sys
import os
import webbrowser
import pygame
import pyperclip
import owlready2
from pygame import Surface# pylint: disable=E0401
import settings# pylint: disable=E0401
from utils import model_request, next_page, last_page, draw_menu_bar, \
    convert_to_python, is_over# pylint: disable=E0401
from settings import colors, size# pylint: disable=E0401
from Classes.button import Button# pylint: disable=E0401, C0412
from Classes.input import Input# pylint: disable=E0401, C0412
from Classes.sliderwindow import SliderWindow# pylint: disable=E0401, C0412


class Request:
    """ Класс страницы запросов """

    def __init__(self, screen: Surface, onto):
        """Инициализация страницы запросов
        :param screen: Поверхность, на которой будет происходить отрисовка
        :type screen: Surface
        """
        self.screen = screen
        self.main_color = colors['dark_blue']
        self.second_color = colors['light_blue']
        self.background_color = colors['background']
        self.menu_buttons = []
        self.inputs = []
        self.send_button = None
        self.next_button = None
        self.last_button = None
        self.buttons = []
        self.now_pressed = None
        self.page = 1
        self.request_results = []
        self.request = []
        self.manager = None
        self.onto = owlready2.get_ontology(f'{onto}').load()
        self.shift_pressed = False
        self.ctrl_pressed = False
        self.backspace_pressed = False
        self.links = []
        self.windows = []
        self.main_window = None
        self.build()

    def run(self, manager):
        """ Метод запуска страницы
        :param manager: менеджер управления приложением
        :type manager: Manager
        :return возвращает название страницы на которую требуется перейти
        """
        self.manager = manager
        result_update = self.update()
        self.draw()
        return result_update

    def draw(self):
        """ Метод отрисовки страницы """
        self.screen.fill(colors['background'])

        self.send_button.draw()
        for inp in self.inputs:
            inp.draw()

        x_coordinate = 50 * settings.WIDTH_SCALE
        y_coordinate = 250 * settings.HEIGHT_SCALE
        width = 1100 * settings.WIDTH_SCALE
        height = 600 * settings.HEIGHT_SCALE
        pygame.draw.rect(self.screen, self.main_color, (x_coordinate - 2, y_coordinate - 2,
                                                        width + 4, height + 4), 0)
        pygame.draw.rect(self.screen, self.background_color, (x_coordinate, y_coordinate,
                                                              width, height), 0)
        for window in self.windows:
            window.draw()
        draw_menu_bar(self.screen, self.main_color, self.menu_buttons)
        pygame.display.flip()

    def update(self):
        """ Метод обработки событий """
        self.main_window.lines = self.request_results
        if self.backspace_pressed:
            for inp in self.inputs:
                if inp.other_params[1]:
                    inp.text = inp.text[:-1]
                    pygame.time.wait(200)
        for event in pygame.event.get():
            if event.type == pygame.VIDEORESIZE:# pylint: disable=E1101
                old_surface_saved = self.screen
                self.screen = pygame.display.set_mode((event.w, event.h),
                                                      pygame.RESIZABLE)# pylint: disable=E1101
                self.screen.blit(old_surface_saved, (0, 0))
                settings.WIDTH_SCALE = event.w / size[0]
                settings.HEIGHT_SCALE = event.h / size[1]
                self.build()
            if event.type == pygame.QUIT:# pylint: disable=E1101
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:# pylint: disable=E1101
                for window in self.windows:
                    if event.button == 1:
                        if window.is_over_vertical(pygame.mouse.get_pos()):
                            window.vertical_pressed = True
                            if 0 <= int(window.slider_y) <= int(window.height)\
                                    - int(window.vertical_slider_size):
                                new_pos = pygame.mouse.get_pos()
                                window.slider_y = new_pos[1] - window.y_coordinate\
                                                  - window.vertical_slider_size / 2
                                window.slider_y = min(max(window.slider_y, 0),
                                                      window.height - window.vertical_slider_size)
                                if window.slider_y > window.height - window.vertical_slider_size:
                                    window.slider_y = window.height - window.vertical_slider_size
                        if window.is_over_horizontal(pygame.mouse.get_pos()):
                            window.horizontal_pressed = True
                            if 0 <= window.slider_x <= window.width - window.horizontal_slider_size:
                                new_pos = pygame.mouse.get_pos()
                                window.slider_x = new_pos[0] - window.x_coordinate\
                                                  - window.horizontal_slider_size / 2
                                window.slider_x = min(max(window.slider_x, 0),
                                                      window.width - window.horizontal_slider_size)
                                if window.slider_x > window.width - window.horizontal_slider_size:
                                    window.slider_x = window.width - window.horizontal_slider_size
                        for link in window.links:
                            if link.is_over(pygame.mouse.get_pos()):
                                result_dfs = self.manager.get_tab('instance').find_docket(
                                    link.text.replace(' ', '_').replace(
                                        '#', '№'
                                    )
                                )
                                if result_dfs:
                                    name = convert_to_python(result_dfs[1])
                                    for file_format in os.listdir(f'{os.getcwd()}\\Docs'):
                                        if file_format.lower() in name.lower():
                                            webbrowser.open(
                                                f'{os.getcwd()}\\Docs\\{file_format}\\{name}',
                                                new=2)
                                    self.manager.get_tab('view').current_path = result_dfs[0]
                                    self.manager.get_tab('view').instance_name = \
                                        convert_to_python(result_dfs[1])
                                    self.manager.get_tab('view').instance = result_dfs[1]
                                    self.manager.get_tab('instance').clicked_communication = None
                                    with open('last_instances.txt', 'a') as file:  # pylint: disable=W1514
                                        with open('last_instances.txt', 'r') as string:  # pylint: disable=W1514
                                            name = string.readlines()[-1]
                                            if name[:-1] != convert_to_python(result_dfs[1]):
                                                file.write(f'{convert_to_python(result_dfs[1])}\n')
                                    return 'instance'
                    if event.button == 4:
                        if is_over(window, pygame.mouse.get_pos()):
                            if window.is_over_horizontal(pygame.mouse.get_pos()):
                                if 0 <= window.slider_x <= window.width\
                                        - window.horizontal_slider_size:
                                    window.slider_x -= window.horizontal_slider_size / 10
                                    window.slider_x = min(max(window.slider_x, 0),
                                                          window.width
                                                          - window.horizontal_slider_size)
                            else:
                                if 0 <= int(window.slider_y) <= int(window.height)\
                                        - int(window.vertical_slider_size):
                                    window.slider_y -= window.vertical_slider_size / 10
                                    window.slider_y = min(max(window.slider_y, 0),
                                                          window.height
                                                          - window.vertical_slider_size)
                    if event.button == 5:
                        if window.is_over_horizontal(pygame.mouse.get_pos()):
                            if 0 <= window.slider_x <= window.width \
                                    - window.horizontal_slider_size:
                                window.slider_x += window.horizontal_slider_size / 10
                                window.slider_x = min(max(window.slider_x, 0),
                                                      window.width - window.horizontal_slider_size)
                        else:
                            if is_over(window, pygame.mouse.get_pos()):
                                if 0 <= int(window.slider_y) <= int(window.height)\
                                        - int(window.vertical_slider_size):
                                    window.slider_y += window.vertical_slider_size / 10
                                    window.slider_y = min(max(window.slider_y, 0),
                                                          window.height
                                                          - window.vertical_slider_size)
            if event.type == pygame.MOUSEMOTION:# pylint: disable=E1101
                for window in self.windows:
                    if window.vertical_pressed:
                        if 0 <= int(window.slider_y) <= int(window.height)\
                                - int(window.vertical_slider_size):
                            new_pos = list(pygame.mouse.get_pos())
                            window.slider_y = new_pos[1] - window.y_coordinate\
                                              - window.vertical_slider_size / 2
                            window.slider_y = min(max(window.slider_y, 0),
                                                  window.height - window.vertical_slider_size)
                    if window.horizontal_pressed:
                        if 0 <= window.slider_x <= window.width - window.horizontal_slider_size:
                            new_pos = list(pygame.mouse.get_pos())
                            window.slider_x = new_pos[0] - window.x_coordinate\
                                              - window.horizontal_slider_size / 2
                            window.slider_x = min(max(window.slider_x, 0),
                                                  window.width - window.horizontal_slider_size)
            if event.type == pygame.MOUSEBUTTONUP:# pylint: disable=E1101
                if event.button == 1:
                    for window in self.windows:
                        window.vertical_pressed = False
                        window.horizontal_pressed = False
            if event.type == pygame.MOUSEBUTTONDOWN:# pylint: disable=E1101
                for button in self.menu_buttons:
                    if is_over(button, pygame.mouse.get_pos()):
                        if button.text == 'Просмотр':
                            return 'view'
                        if button.text == 'Главная':
                            return 'main'
                        if button.text == 'Выход':
                            return 'exit'

            if event.type == pygame.KEYDOWN:# pylint: disable=E1101
                if event.key == pygame.K_ESCAPE:# pylint: disable=E1101
                    if self.inputs[0].other_params[1] or self.inputs[1].other_params[1]\
                            or self.inputs[2].other_params[1]:
                        self.inputs[0].other_params[1] = self.inputs[1].other_params[1] = \
                            self.inputs[2].other_params[1] = False
                        self.now_pressed = None
                    else:
                        return 'main'

                if event.key == pygame.K_TAB:# pylint: disable=E1101
                    self.inputs[0].other_params[1] =\
                        self.inputs[1].other_params[1] = self.inputs[2].other_params[1] = False
                    if self.now_pressed is None:
                        self.inputs[0].other_params[1] = True
                        self.now_pressed = 0
                    else:
                        self.inputs[self.now_pressed].other_params[1] = False
                        self.now_pressed += 1
                        self.now_pressed %= 3
                        self.inputs[self.now_pressed].other_params[1] = True
                if event.key in [pygame.K_d, pygame.K_RIGHT]:# pylint: disable=E1101
                    if not (self.inputs[0].other_params[1] or
                            self.inputs[1].other_params[1] or self.inputs[2].other_params[1]):
                        self.page = next_page(self.page, self.request_results, 16)
                if event.key in [pygame.K_a, pygame.K_LEFT]:# pylint: disable=E1101
                    if not (self.inputs[0].other_params[1] or
                            self.inputs[1].other_params[1] or self.inputs[2].other_params[1]):
                        self.page = last_page(self.page, self.request_results, 16)
                if event.key == pygame.K_RETURN:# pylint: disable=E1101
                    self.request = []
                    self.page = 1
                    for inp in self.inputs:
                        self.request.append(inp.text)
                    main_object = self.request[0]
                    object_property = self.request[1]
                    sub_objects = self.request[2]
                    self.request_results = []
                    for result in model_request(main_object,
                                                object_property,
                                                sub_objects,
                                                self.onto):
                        self.request_results.append(result)
                    if len(self.request_results) > 0:
                        with open('last_requests.txt', 'a') as file: # pylint: disable=W1514
                            with open('last_requests.txt', 'r') as string:  # pylint: disable=W1514
                                strings = string.readlines()
                                if strings:
                                    name = strings[-1]
                                    if name[:-1] != f'[{self.request[0]}]'\
                                                   f' [{self.request[1]}] [{self.request[2]}]':
                                        file.write(f'[{self.request[0]}]'
                                                   f' [{self.request[1]}] [{self.request[2]}]\n')
                else:
                    for inp in self.inputs:
                        if inp.other_params[1]:
                            if event.key == pygame.K_BACKSPACE:# pylint: disable=E1101
                                self.backspace_pressed = True
                            elif event.key == pygame.K_RETURN:# pylint: disable=E1101
                                inp.other_params[1] = False
                            elif pygame.key.name(event.key) == 'left shift':
                                self.shift_pressed = True
                            elif pygame.key.name(event.key) == 'left ctrl':
                                self.ctrl_pressed = True
                            else:
                                if self.ctrl_pressed:
                                    if event.key in [pygame.K_v]:
                                        inp.text += pyperclip.paste()
                                else:
                                    if event.unicode != '\t':
                                        inp.text += event.unicode
            if event.type == pygame.KEYUP:# pylint: disable=E1101
                if pygame.key.name(event.key) == 'left shift':
                    self.shift_pressed = False
                if event.key == pygame.K_BACKSPACE:# pylint: disable=E1101
                    self.backspace_pressed = False
                if pygame.key.name(event.key) == 'left ctrl':
                    self.ctrl_pressed = False
            if event.type == pygame.MOUSEBUTTONDOWN:# pylint: disable=E1101
                if is_over(self.send_button, pygame.mouse.get_pos()):
                    self.request = []
                    for inp in self.inputs:
                        self.request.append(inp.text)
                    self.page = 1
                    main_object = self.request[0]
                    object_property = self.request[1]
                    sub_objects = self.request[2]
                    self.request_results = []
                    for result in model_request(main_object,
                                                object_property,
                                                sub_objects,
                                                self.onto):
                        self.request_results.append(result)
                    if len(self.request_results) > 0:
                        with open('last_requests.txt', 'a') as file: # pylint: disable=W1514
                            with open('last_requests.txt', 'r') as string:  # pylint: disable=W1514
                                strings = string.readlines()
                                if strings:
                                    name = strings[-1]
                                    if name[:-1] != f'[{self.request[0]}]' \
                                                    f' [{self.request[1]}] [{self.request[2]}]':
                                        file.write(f'[{self.request[0]}]'
                                                   f' [{self.request[1]}] [{self.request[2]}]\n')
                                else:
                                    file.write(f'[{self.request[0]}]'
                                               f' [{self.request[1]}] [{self.request[2]}]\n')
                for i,_ in enumerate(self.inputs):
                    inp = self.inputs[i]
                    inp.other_params[1] = is_over(inp, pygame.mouse.get_pos())
                    if inp.other_params[1]:
                        self.now_pressed = i
        return 'request'

    def build(self):
        """ Метод инициализации всего необходимого для загрузки страницы """
        first = ''
        second = ''
        third = ''
        if self.inputs:
            first = self.inputs[0].text
            second = self.inputs[1].text
            third = self.inputs[2].text
        self.inputs = [
            Input((50 * settings.WIDTH_SCALE, 50 * settings.HEIGHT_SCALE,
                   300 * settings.WIDTH_SCALE, 70 * settings.HEIGHT_SCALE),
                  self.main_color, self.screen, 'Субъект'),
            Input((450 * settings.WIDTH_SCALE, 50 * settings.HEIGHT_SCALE,
                   300 * settings.WIDTH_SCALE, 70 * settings.HEIGHT_SCALE),
                  self.main_color, self.screen, 'Связь'),
            Input((850 * settings.WIDTH_SCALE, 50 * settings.HEIGHT_SCALE,
                   300 * settings.WIDTH_SCALE, 70 * settings.HEIGHT_SCALE),
            self.main_color, self.screen, 'Объект'),
        ]
        self.inputs[0].text = first
        self.inputs[1].text = second
        self.inputs[2].text = third
        self.main_window = SliderWindow((50 * settings.WIDTH_SCALE, 250 * settings.HEIGHT_SCALE,
                                         1100 * settings.WIDTH_SCALE, 600 * settings.HEIGHT_SCALE),
                                        ([], 18, ''), self.screen, self.main_color)
        self.windows = [self.main_window]
        self.send_button = Button((450 * settings.WIDTH_SCALE, 150 * settings.HEIGHT_SCALE,
                                   300 * settings.WIDTH_SCALE, 70 * settings.HEIGHT_SCALE),
                                  (self.background_color, colors['very_light_grey'],
                                  self.main_color, colors['black']),
                                  'Запросить', self.screen)
        self.next_button = Button(((356 + 286) * settings.WIDTH_SCALE, 827 * settings.HEIGHT_SCALE,
                                   200 * settings.WIDTH_SCALE, 50 * settings.HEIGHT_SCALE),
                                  (self.background_color, colors['very_light_grey'],
                                  self.main_color, colors['black']),
                                  'Следущая', self.screen)
        self.last_button = Button((356 * settings.WIDTH_SCALE, 827 * settings.HEIGHT_SCALE,
                                   200 * settings.WIDTH_SCALE, 50 * settings.HEIGHT_SCALE),
                                  (self.background_color, colors['very_light_grey'],
                                  self.main_color, colors['black']),
                                  'Предыдущая', self.screen)
        self.buttons = [
            self.send_button,
            self.next_button,
            self.last_button
        ]
        self.menu_buttons = [
            Button((0,
                   0, 120 * settings.WIDTH_SCALE,
                   30 * settings.HEIGHT_SCALE),
                   (self.main_color, self.second_color, self.main_color, colors['background']),
                   'Главная', self.screen),
            Button((120 * settings.WIDTH_SCALE,
                   0, 120 * settings.WIDTH_SCALE,
                   30 * settings.HEIGHT_SCALE),
                   (self.main_color, self.second_color, self.main_color, colors['background']),
                   'Просмотр', self.screen),
            Button((240 * settings.WIDTH_SCALE,
                   0, 120 * settings.WIDTH_SCALE,
                   30 * settings.HEIGHT_SCALE), (self.background_color, self.background_color,
                                                 self.background_color, colors['black']),
                   'Запрос', self.screen)
        ]
