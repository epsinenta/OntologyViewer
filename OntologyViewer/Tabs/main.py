""" Модули для взаимодействия и визуализации данных модели """
import webbrowser
import os
import sys
import pygame
import easygui
import owlready2
from pygame import Surface

from Classes.docket import Docket# pylint: disable=E0401
from Classes.sliderwindow import SliderWindow# pylint: disable=E0401
from utils import draw_menu_bar, is_over, model_request,\
    convert_to_python, next_page, last_page# pylint: disable=E0401
from settings import colors, MAIN_FONT, size# pylint: disable=E0401
import settings# pylint: disable=E0401
from Classes.button import Button # pylint: disable=E0401, C0412


class Main:
    """ Класс главной страницы """

    def __init__(self, screen: Surface, onto):
        """Инициализация главной вкладки
        :param screen: Поверхность, на которой будет происходить отрисовка
        :type screen: Surface
        """
        self.screen = screen
        self.name = ''
        self.description = ''
        self.main_color = colors['dark_green']
        self.second_color = colors['light_green']
        self.background_color = colors['background']
        self.description = ''
        self.menu_buttons = []
        self.manager = None
        self.name = onto.split('/')[-1][:-4]
        self.onto = owlready2.get_ontology(f'{onto}').load()
        self.last_request_links = []
        self.last_dockets = []
        self.windows = []
        self.request_window = None
        self.page = 1
        old_surface_saved = self.screen
        width = size[0]
        height = size[1] - 75
        self.screen = pygame.display.set_mode((width, height),
                                              pygame.RESIZABLE)  # pylint: disable=E1101
        self.screen.blit(old_surface_saved, (0, 0))
        settings.WIDTH_SCALE = width / size[0]
        settings.HEIGHT_SCALE = height / size[1]
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
        self.screen.fill(self.background_color)
        pygame.font.init()
        font = pygame.font.SysFont(MAIN_FONT,
                                   int(66 * settings.HEIGHT_SCALE * settings.WIDTH_SCALE))
        render_line = font.render(self.name, True, colors['black'])
        self.screen.blit(
            render_line,
            (
                50 * settings.WIDTH_SCALE, 100 * settings.HEIGHT_SCALE
            )
        )
        x_coordinate = 52
        y_coordinate = 280
        width = 1094
        height = 210
        pygame.draw.rect(self.screen, self.main_color, ((x_coordinate - 2) * settings.WIDTH_SCALE,
                                                        (y_coordinate - 2) * settings.HEIGHT_SCALE,
                                                        (width + 4) * settings.WIDTH_SCALE,
                                                        (height + 4) * settings.HEIGHT_SCALE),
                         0)
        pygame.draw.rect(self.screen, self.background_color, (x_coordinate * settings.WIDTH_SCALE,
                                                              y_coordinate * settings.HEIGHT_SCALE,
                                                              width * settings.WIDTH_SCALE,
                                                              height * settings.HEIGHT_SCALE), 0)

        font = pygame.font.SysFont(MAIN_FONT,
                                   int(30 * settings.HEIGHT_SCALE * settings.WIDTH_SCALE))
        x_coordinate = 50 * settings.WIDTH_SCALE
        y_coordinate = 160 * settings.HEIGHT_SCALE
        for line in self.description.split('\n'):
            render_line = font.render(line, True, colors['black'])
            self.screen.blit(
                render_line,
                (
                    x_coordinate, y_coordinate
                )
            )
            y_coordinate += 30 * settings.HEIGHT_SCALE
        y_coordinate -= 10 * settings.HEIGHT_SCALE
        x_coordinate = 50 * settings.WIDTH_SCALE
        font = pygame.font.SysFont(MAIN_FONT,
                                   int(40 * settings.HEIGHT_SCALE * settings.WIDTH_SCALE))
        render_line = font.render("История запросов:", True, colors['black'])
        self.screen.blit(
            render_line,
            (
                x_coordinate, y_coordinate + 30 * settings.HEIGHT_SCALE
            )
        )
        render_line = font.render("История экземпляров:", True, colors['black'])
        self.screen.blit(
            render_line,
            (
                x_coordinate, 515 * settings.HEIGHT_SCALE
            )
        )
        x_coordinate = 52 * settings.WIDTH_SCALE
        y_coordinate = 560 * settings.HEIGHT_SCALE
        with open('last_instances.txt', 'r') as file: # pylint: disable=W1514
            lines = file.readlines()[::-1]
        self.last_dockets = []
        for docket_name in lines[(self.page - 1) * 8: (min(len(lines), self.page * 8))]:
            if docket_name[-1] == '\n':
                docket_name = docket_name[:-1]
            docket = Docket((x_coordinate,
                            y_coordinate, 236 * settings.WIDTH_SCALE,
                            100 * settings.HEIGHT_SCALE), (colors['dark_green'],
                                                           docket_name.replace('_', ' '),
                            'Экземпляр',
                                                           colors['light_green']),
                            self.screen)
            x_coordinate += (286 * settings.WIDTH_SCALE)
            if x_coordinate >= 1100 * settings.WIDTH_SCALE:
                x_coordinate = 50 * settings.WIDTH_SCALE
                y_coordinate += (150 * settings.HEIGHT_SCALE)
            docket.draw()
            self.last_dockets.append(docket)
        file.close()
        font = pygame.font.SysFont(MAIN_FONT,
                                   int(30 * settings.HEIGHT_SCALE * settings.WIDTH_SCALE))
        max_pages = len(lines) // 8
        if len(lines) % 8 != 0:
            max_pages += 1
        if max_pages > 1:
            x_coordinate = 583 * settings.WIDTH_SCALE
            if len(str(max_pages)) > 1:
                x_coordinate = 580 * settings.WIDTH_SCALE
            if len(str(max_pages)) > 2:
                x_coordinate = 574 * settings.WIDTH_SCALE
            render_line = font.render(f'{self.page}/{max_pages}', True, colors['black'])
            if max_pages != 0:
                self.screen.blit(
                    render_line,
                    (
                        x_coordinate, 845 * settings.HEIGHT_SCALE
                    )
                )
        for window in self.windows:
            window.draw()
        if not self.request_window.lines:
            font = pygame.font.SysFont(MAIN_FONT,
                                       int(60 * settings.HEIGHT_SCALE * settings.WIDTH_SCALE))
            render_line = font.render('Пока здесь пусто', True, colors['light_grey'])
            self.screen.blit(
                render_line,
                (
                    430 * settings.WIDTH_SCALE, 365 * settings.HEIGHT_SCALE
                )
            )
        if not self.last_dockets:
            font = pygame.font.SysFont(MAIN_FONT,
                                       int(60 * settings.HEIGHT_SCALE * settings.WIDTH_SCALE))
            render_line = font.render('Пока здесь пусто', True, colors['light_grey'])
            self.screen.blit(
                render_line,
                (
                    430 * settings.WIDTH_SCALE, 665 * settings.HEIGHT_SCALE
                )
            )
        self.select_button.draw()
        draw_menu_bar(self.screen, self.main_color, self.menu_buttons)
        pygame.display.flip()

    def update(self):
        """ Метод обработки событий """
        with open('last_requests.txt', 'r') as file: # pylint: disable=W1514
            lines = file.readlines()
        self.last_request_links = []
        for line in lines[::-1]:
            if line[-1] == '\n':
                line = line[:-1]
            self.last_request_links.append(line)
        file.close()
        self.request_window.lines = self.last_request_links
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
                        for link in self.request_window.links:
                            if link.is_over(pygame.mouse.get_pos()):
                                self.manager.get_tab('request').page = 1
                                request = []
                                for i, string in enumerate(link.text):
                                    if string == '[':
                                        for j, k in enumerate(link.text):
                                            if k == ']' and j > i:
                                                request.append(link.text[i + 1:j])
                                                break
                                for i,_ in enumerate(self.manager.get_tab('request').inputs):
                                    self.manager.get_tab('request').inputs[i].text = request[i]
                                main_object = request[0]
                                object_property = request[1]
                                sub_objects = request[2]
                                self.manager.get_tab('request').request_results = []
                                for result in model_request(main_object,
                                                            object_property,
                                                            sub_objects,
                                                            self.onto):
                                    self.manager.get_tab('request').request_results.append(result
                                                                                              )
                                return 'request'
                        if window.is_over_vertical(pygame.mouse.get_pos()):
                            window.vertical_pressed = True
                            if 0 <= window.slider_y <= window.height - window.vertical_slider_size:
                                new_pos = pygame.mouse.get_pos()
                                window.slider_y = new_pos[1] - window.y_coordinate\
                                                  - window.vertical_slider_size / 2
                                window.slider_y = min(max(window.slider_y, 0),
                                                      window.height - window.vertical_slider_size)
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
                                if 0 <= window.slider_y <= window.height\
                                        - window.vertical_slider_size:
                                    window.slider_y -= window.vertical_slider_size / 10
                                    window.slider_y = min(max(window.slider_y, 0),
                                                          window.height
                                                          - window.vertical_slider_size)
                    if event.button == 5:
                        if window.is_over_horizontal(pygame.mouse.get_pos()):
                            if 0 <= window.slider_x <= window.width\
                                    - window.horizontal_slider_size:
                                window.slider_x += window.horizontal_slider_size / 10
                                window.slider_x = min(max(window.slider_x, 0),
                                                      window.width
                                                      - window.horizontal_slider_size)
                        else:
                            if is_over(window, pygame.mouse.get_pos()):
                                if 0 <= window.slider_y <= window.height\
                                        - window.vertical_slider_size:
                                    window.slider_y += window.vertical_slider_size / 10
                                    window.slider_y = min(max(window.slider_y, 0),
                                                          window.height
                                                          - window.vertical_slider_size)
            if event.type == pygame.MOUSEMOTION:# pylint: disable=E1101
                for window in self.windows:
                    if window.vertical_pressed:
                        if 0 <= window.slider_y <= window.height - window.vertical_slider_size:
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
                if is_over(self.select_button, pygame.mouse.get_pos()):
                    new_onto = easygui.fileopenbox()
                    if new_onto:
                        if '.owl' in new_onto:
                            return new_onto

                for button in self.menu_buttons:
                    if is_over(button, pygame.mouse.get_pos()):
                        if button.text == 'Просмотр':
                            return 'view'
                        if button.text == 'Запрос':
                            return 'request'
                        if button.text == 'Выход':
                            return 'exit'

                for docket in self.last_dockets:
                    if is_over(docket, pygame.mouse.get_pos()):
                        result_dfs = self.manager.get_tab('instance').find_docket(
                            docket.other_params[1].replace(' ', '_').replace('#', '№')
                        )
                        if result_dfs:
                            name = convert_to_python(result_dfs[1])
                            for file_format in os.listdir(f'{os.getcwd()}\\Docs'):
                                if file_format.lower() in name.lower():
                                    webbrowser.open(
                                        f'{os.getcwd()}\\Docs\\{file_format}\\{name}',
                                                    new=2)
                            self.manager.get_tab('view').current_path = result_dfs[0]
                            self.manager.get_tab('view').instance_name =\
                                convert_to_python(result_dfs[1])
                            self.manager.get_tab('view').instance = result_dfs[1]
                            self.manager.get_tab('instance').clicked_communication = None
                            with open('last_instances.txt', 'a') as file: # pylint: disable=W1514
                                with open('last_instances.txt', 'r') as string: # pylint: disable=W1514
                                    if string.readlines()[-1] !=\
                                            f'{convert_to_python(result_dfs[1])}\n':
                                        file.write(f'{convert_to_python(result_dfs[1])}\n')
                            return 'instance'
            if event.type == pygame.KEYDOWN:# pylint: disable=E1101
                with open('last_instances.txt', 'r') as file: # pylint: disable=W1514
                    lines = file.readlines()
                if event.key in [pygame.K_d, pygame.K_RIGHT]:# pylint: disable=E1101
                    self.page = next_page(self.page, lines, 8)
                if event.key in [pygame.K_a, pygame.K_LEFT]:# pylint: disable=E1101
                    self.page = last_page(self.page, lines, 8)
                if event.key == pygame.K_ESCAPE:# pylint: disable=E1101
                    return 'exit'
        return 'main'

    def build(self):
        """ Метод инициализации всего необходимого для загрузки страницы """
        self.description = ''
        self.menu_buttons = [
            Button((0 * settings.WIDTH_SCALE, 0 * settings.HEIGHT_SCALE,
                    120 * settings.WIDTH_SCALE, 30 * settings.HEIGHT_SCALE),
                   (self.background_color, self.background_color,
                   self.background_color, colors['black']),
                   'Главная', self.screen),
            Button((120 * settings.WIDTH_SCALE, 0 * settings.HEIGHT_SCALE,
                    120 * settings.WIDTH_SCALE, 30 * settings.HEIGHT_SCALE),
                   (self.main_color, self.second_color, self.main_color, colors['background']),
                   'Просмотр', self.screen),
            Button((240 * settings.WIDTH_SCALE, 0 * settings.HEIGHT_SCALE,
                    120 * settings.WIDTH_SCALE, 30 * settings.HEIGHT_SCALE),
                   (self.main_color, self.second_color, self.main_color, colors['background']),
                   'Запрос', self.screen)
        ]
        self.select_button = Button((1000 * settings.WIDTH_SCALE, 105 * settings.HEIGHT_SCALE,
                                     150 * settings.WIDTH_SCALE, 30 * settings.HEIGHT_SCALE),
                                    (self.main_color, self.second_color,
                                     self.main_color, colors['background']),
                   'Выбрать', self.screen)
        self.request_window = SliderWindow((52 * settings.WIDTH_SCALE, 280 * settings.HEIGHT_SCALE,
                                            1094 * settings.WIDTH_SCALE,
                                            210 * settings.HEIGHT_SCALE),
                                           ([], 6, ''), self.screen, colors['dark_green'])
        self.windows = [self.request_window]
