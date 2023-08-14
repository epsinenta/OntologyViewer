""" Модули для использования и визуализации данных модели """
import webbrowser
import sys
import os
from threading import Thread

import pygame
import owlready2
from pygame import Surface

from Classes.button import Button# pylint: disable=E0401
from Classes.sliderwindow import SliderWindow# pylint: disable=E0401
from settings import colors, MAIN_FONT, size# pylint: disable=E0401
import settings# pylint: disable=E0401
from utils import draw_menu_bar, convert_to_python, cut_the_string, is_over, run_graph# pylint: disable=E0401


class Instance:
    """ Класс страницы просмотра информации об экземпляре """

    def __init__(self, screen: Surface, onto):
        """Инициализация главной вкладки
        :param screen: Поверхность, на которой будет происходить отрисовка
        :type screen: Surface
        """
        self.communication_window = None
        self.object_window = None
        self.data_window = None
        self.screen = screen
        self.main_color = colors['main_purple']
        self.second_color = colors['second_purple']
        self.background_color = colors['background']
        self.buttons = []
        self.menu_buttons = []
        self.manager = None
        self.communication_page = 1
        self.object_page = 1
        self.instance_name = ''
        self.path = []
        self.objects_communication = {}
        self.communications = []
        self.objects = []
        self.instance = None
        self.data = []
        self.clicked_communication = None
        self.onto = owlready2.get_ontology(f'{onto}').load()
        self.windows = []
        self.build()

    def run(self, manager) -> str:
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
        x_coordinate = 600 * settings.WIDTH_SCALE
        y_coordinate = 150 * settings.HEIGHT_SCALE
        width = 550 * settings.WIDTH_SCALE
        height = 150 * settings.HEIGHT_SCALE
        pygame.draw.rect(self.screen, colors['dark_purple'], (x_coordinate - 2,
                                                              y_coordinate - 2,
                                                              width + 4, height + 4), 0)
        pygame.draw.rect(self.screen, self.background_color, (x_coordinate, y_coordinate,
                                                              width, height), 0)

        x_coordinate = 50 * settings.WIDTH_SCALE
        y_coordinate = 375 * settings.HEIGHT_SCALE
        width = 1100 * settings.WIDTH_SCALE
        height = 475 * settings.HEIGHT_SCALE
        pygame.draw.rect(self.screen, colors['dark_purple'], (x_coordinate - 2,
                                                              y_coordinate - 2,
                                                              width + 4, height + 4), 0)
        pygame.draw.rect(self.screen, self.background_color, (x_coordinate, y_coordinate,
                                                              width, height), 0)
        font = pygame.font.SysFont(MAIN_FONT,
                                   int(40 * settings.HEIGHT_SCALE * settings.WIDTH_SCALE))
        render_line = font.render('Связь', True, colors['black'])
        point = 275 + render_line.get_width() / 2
        pygame.draw.polygon(self.screen, colors['dark_purple'],
                            [((point - 15 / 3 * 2) * settings.WIDTH_SCALE,
                              150 * settings.HEIGHT_SCALE),
                             ((point + 15 / 3 * 2) * settings.WIDTH_SCALE,
                              150 * settings.HEIGHT_SCALE),
                             ((point + 15 / 3 * 2) * settings.WIDTH_SCALE,
                              250 * settings.HEIGHT_SCALE),
                             ((point + 30 / 3 * 2) * settings.WIDTH_SCALE,
                              250 * settings.HEIGHT_SCALE),
                             (point * settings.WIDTH_SCALE, 300 * settings.HEIGHT_SCALE),
                             ((point - 30 / 3 * 2) * settings.WIDTH_SCALE,
                              250 * settings.HEIGHT_SCALE),
                             ((point - 15 / 3 * 2) * settings.WIDTH_SCALE,
                              250 * settings.HEIGHT_SCALE)],
                            2)
        point = 325 + render_line.get_height() / 2
        x_coordinate = (1100 + render_line.get_width() / 2) / 2 - 62.5
        pygame.draw.polygon(self.screen, colors['dark_purple'],
                            [(x_coordinate * settings.WIDTH_SCALE,
                              (point - 15 / 3 * 2) * settings.HEIGHT_SCALE),
                             (x_coordinate * settings.WIDTH_SCALE,
                              (point + 15 / 3 * 2) * settings.HEIGHT_SCALE),
                             (
                                 (x_coordinate + 150) * settings.WIDTH_SCALE,
                                 (point + 15 / 3 * 2) * settings.HEIGHT_SCALE),
                             (
                                 (x_coordinate + 150) * settings.WIDTH_SCALE,
                                 (point + 30 / 3 * 2) * settings.HEIGHT_SCALE),
                             ((x_coordinate + 200) * settings.WIDTH_SCALE,
                              point * settings.HEIGHT_SCALE),
                             (
                                 (x_coordinate + 150) * settings.WIDTH_SCALE,
                                 (point - 30 / 3 * 2) * settings.HEIGHT_SCALE),
                             ((x_coordinate + 150) * settings.WIDTH_SCALE,
                              (point - 15 / 3 * 2) * settings.HEIGHT_SCALE)],
                            2)

        pygame.font.init()
        path_text = 'Классификатор: '
        for sub_path in self.path[1:]:
            path_text += '/'
            name = str(sub_path[0].is_a)[1:-1].split('.')[1:]
            for part in name:
                path_text += part
        if len(path_text) > 50 and len(self.path[1:]) > 2:
            path_text = 'Классификатор: /'
            sub_path = self.path[1]
            name = str(sub_path[0].is_a)[1:-1].split('.')[1:]
            for part in name:
                path_text += part
            path_text += '/.../'
            sub_path = self.path[-1]
            name = str(sub_path[0].is_a)[1:-1].split('.')[1:]
            for part in name:
                path_text += part
        font = pygame.font.SysFont(MAIN_FONT,
                                   int(50 * settings.WIDTH_SCALE * settings.HEIGHT_SCALE))
        render_line = font.render(path_text, True, colors['black'])
        self.screen.blit(
            render_line,
            (
                50 * settings.WIDTH_SCALE, 50 * settings.HEIGHT_SCALE
            )
        )
        font = pygame.font.SysFont(MAIN_FONT,
                                   int(50 * settings.WIDTH_SCALE * settings.HEIGHT_SCALE))
        render_line = font.render(f'Объект:'
                                  f' {self.instance_name.replace("_", " ").replace("№", "#")}',
                                  True, colors['black'])
        self.screen.blit(
            render_line,
            (
                50 * settings.WIDTH_SCALE, 95 * settings.HEIGHT_SCALE
            )
        )
        if render_line.get_width() < 700 * settings.WIDTH_SCALE:
            font = pygame.font.SysFont(MAIN_FONT,
                                       int(40 * settings.WIDTH_SCALE * settings.HEIGHT_SCALE))
            render_line = font.render('Свойство',
                                      True, colors['black'])
            self.screen.blit(
                render_line,
                (
                    815 * settings.WIDTH_SCALE, 100 * settings.HEIGHT_SCALE
                )
            )

        render_line = font.render('Связь', True, colors['black'])
        self.screen.blit(
            render_line,
            (
                275 * settings.WIDTH_SCALE, 325 * settings.HEIGHT_SCALE
            )
        )
        render_line = font.render('Объект', True, colors['black'])
        self.screen.blit(
            render_line,
            (
                825 * settings.WIDTH_SCALE, 325 * settings.HEIGHT_SCALE
            )
        )

        for window in self.windows:
            window.draw()
        pygame.draw.line(self.screen, (52, 1, 115),
                         (600 * settings.WIDTH_SCALE, 375 * settings.HEIGHT_SCALE),
                         (600 * settings.WIDTH_SCALE, 375 * settings.HEIGHT_SCALE + height), 2)
        draw_menu_bar(self.screen, self.main_color, self.menu_buttons)
        pygame.display.flip()

    def update(self):
        """ Метод обработки событий """
        current_instance_name = self.manager.get_tab('view').instance_name
        current_path = self.manager.get_tab('view').current_path
        if self.path != current_path or self.instance_name != current_instance_name:
            self.instance_name = current_instance_name
            self.communication_window.word = self.instance_name
            self.instance = self.manager.get_tab('view').instance
            self.path = current_path
            self.object_page = 1
            self.communication_page = 1
            self.communications = []
            self.objects = []
            self.data = []
            self.objects_communication = {}
            for data_property in list(self.instance.get_properties()):
                if data_property in list(self.onto.data_properties()):
                    for pair in list(data_property.get_relations()):
                        value = convert_to_python(pair[1])
                        if pair[0] == self.instance:
                            string = value
                            for cut_string in cut_the_string(string, 95 * settings.WIDTH_SCALE):
                                self.data.append(cut_string)
                            string = data_property.python_name
                            for cut_string in cut_the_string(string, 95 * settings.WIDTH_SCALE):
                                self.data.append(cut_string)
                else:
                    self.communications.append(data_property)
                    self.objects_communication[data_property] = []
            for communication in self.communications:
                for pair in list(communication.get_relations()):
                    value = convert_to_python(pair[1])
                    if pair[0] == self.instance:
                        if value not in self.objects_communication[communication]:
                            self.objects_communication[communication].append(value)
            lines = []
            for i in self.communications:
                result = i.python_name
                value = ''
                for pair in i.get_relations():
                    value = pair[1]
                    if convert_to_python(value) in self.objects_communication[i]:
                        value = f' [{convert_to_python(value.is_a[0])}]'
                        if 'Снятие' in value or 'Установка' in value or 'Обслуживание' in value:
                            value = ' [Ремонтная работа]'
                        if len(self.objects_communication[i]) > 1:
                            if 'ТМ' in value:
                                value = ' [ТМ]'
                            if 'ЕО' in value:
                                value = ' [ЕО]'
                            if 'НН' in value:
                                value = ' [НН]'
                        break
                result += value
                lines.append(result)
            self.communication_window.lines = lines
            self.object_window.lines = []
            self.object_window.slider_y = 0
            self.object_window.slider_x = 0
            self.communication_window.pressed_link = None
            lines = []
            for i in range(1, len(self.data), 2):
                string = self.data[i]
                lines.append(f'{string}: {self.data[i - 1]}')
            self.data_window.lines = lines
        for event in pygame.event.get():
            if event.type == pygame.QUIT:# pylint: disable=E1101
                sys.exit()
            if event.type == pygame.VIDEORESIZE:# pylint: disable=E1101
                old_surface_saved = self.screen
                self.screen = pygame.display.set_mode((event.w, event.h),
                                                      pygame.RESIZABLE)# pylint: disable=E1101
                self.screen.blit(old_surface_saved, (0, 0))
                settings.WIDTH_SCALE = event.w / size[0]
                settings.HEIGHT_SCALE = event.h / size[1]
                self.build()
                self.update()
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
                        if window.is_over_horizontal(pygame.mouse.get_pos()):
                            window.horizontal_pressed = True
                            if 0 <= window.slider_x <= window.width\
                                    - window.horizontal_slider_size:
                                new_pos = pygame.mouse.get_pos()
                                window.slider_x = new_pos[0] - window.x_coordinate\
                                                  - window.horizontal_slider_size / 2
                                window.slider_x = min(max(window.slider_x, 0),
                                                      window.width - window.horizontal_slider_size)
                                if window.slider_x > window.width - window.horizontal_slider_size:
                                    window.slider_x = window.width - window.horizontal_slider_size
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
                                if 0 <= int(window.slider_y) / 2 <=\
                                        int(window.height) - int(window.vertical_slider_size):
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
                                                      window.width - window.horizontal_slider_size)
                        else:
                            if is_over(window, pygame.mouse.get_pos()):
                                if 0 <= int(window.slider_y)<= int(window.height)\
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
                            window.slider_x = new_pos[
                                                  0] - window.x_coordinate\
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
                        if button.text == 'Главная':
                            return 'main'
                        if button.text == 'Просмотр':
                            return 'view'
                        if button.text == 'Запрос':
                            return 'request'
                        if button.text == 'Граф':
                            thread = Thread(target=run_graph, args=(self.instance_name, self.onto))
                            thread.start()
            if event.type == pygame.KEYDOWN:# pylint: disable=E1101
                if event.key == pygame.K_ESCAPE:# pylint: disable=E1101
                    return 'view'
            if event.type == pygame.MOUSEBUTTONDOWN:# pylint: disable=E1101
                if event.button == 1:
                    for link in self.communication_window.links:
                        pos = list(pygame.mouse.get_pos())
                        if link.is_over(pos):
                            self.communication_window.pressed_link = link
                            self.clicked_communication = link
                            result = None
                            for object_property in self.onto.properties():
                                if object_property.python_name == link.text.split('[')[0][:-1]:
                                    result = object_property
                                    break
                            self.objects = []
                            self.objects = self.objects_communication[result]
                            lines = []
                            for line in self.objects:
                                lines.append(convert_to_python(line))
                            self.object_window.lines = lines
                            self.object_page = 1
                    for link in self.object_window.links:
                        if link.is_over(pygame.mouse.get_pos()):
                            result_dfs = \
                                self.find_docket(link.text.replace(' ', '_').replace('#', '№'))
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
                                with open('last_instances.txt', 'a') as file: # pylint: disable=W1514
                                    file.write(f'{convert_to_python(result_dfs[1])}\n')
                                return 'instance'
        return 'instance'

    def build(self):
        """ Метод инициализации всего необходимого для загрузки страницы """
        self.menu_buttons = [
            Button((0, 0, 120 * settings.WIDTH_SCALE, 30 * settings.HEIGHT_SCALE),
                   (self.main_color, self.second_color, self.main_color, colors['background']),
                   'Главная', self.screen),
            Button((120 * settings.WIDTH_SCALE, 0,
                    120 * settings.WIDTH_SCALE, 30 * settings.HEIGHT_SCALE),
                   (self.main_color, self.second_color, self.main_color, colors['background']),
                   'Просмотр', self.screen),
            Button((240 * settings.WIDTH_SCALE, 0, 120 * settings.WIDTH_SCALE,
                    30 * settings.HEIGHT_SCALE),
                   (self.main_color, self.second_color, self.main_color, colors['background']),
                   'Запрос', self.screen),
            Button((360 * settings.WIDTH_SCALE, 0, 120 * settings.WIDTH_SCALE,
                    30 * settings.HEIGHT_SCALE),
                   (self.background_color, self.background_color,
                   self.background_color, colors['black']),
                   'Экземпляр', self.screen),
            Button((480 * settings.WIDTH_SCALE, 0, 120 * settings.WIDTH_SCALE,
                    30 * settings.HEIGHT_SCALE),
                   (self.main_color, self.second_color, self.main_color, colors['background']),
                   'Граф', self.screen),
        ]
        lines = []
        self.communication_window = SliderWindow((50 * settings.WIDTH_SCALE,
                                                  375 * settings.HEIGHT_SCALE,
                                                  550 * settings.WIDTH_SCALE,
                                                  475 * settings.HEIGHT_SCALE),
                                                 (lines, 15, ''), self.screen,
                                                 colors['dark_purple'])
        self.object_window = SliderWindow((602 * settings.WIDTH_SCALE,
                                           375 * settings.HEIGHT_SCALE,
                                           548 * settings.WIDTH_SCALE,
                                           475 * settings.HEIGHT_SCALE, colors['dark_purple']),
                                          (lines, 15, ''), self.screen)
        self.data_window = SliderWindow((602 * settings.WIDTH_SCALE,
                                         150 * settings.HEIGHT_SCALE,
                                         548 * settings.WIDTH_SCALE,
                                         150 * settings.HEIGHT_SCALE),
                                        (lines, 5, ''), self.screen,
                                        colors['black'])
        self.windows = [
            self.communication_window,
            self.object_window,
            self.data_window
        ]
        self.object_page = 1
        self.communication_page = 1
        self.communications = []
        self.objects_communication = {}
        self.data = []
        if self.manager:
            current_instance_name = self.manager.get_tab('view').instance_name
            current_path = self.manager.get_tab('view').current_path
            self.instance_name = current_instance_name
            self.instance = self.manager.get_tab('view').instance
            self.path = current_path
            self.object_page = 1
            self.communication_page = 1
            self.communications = []
            self.objects = []
            self.data = []
            self.objects_communication = {}
            for data_property in list(self.instance.get_properties()):
                if data_property in list(self.onto.data_properties()):
                    for pair in list(data_property.get_relations()):
                        value = convert_to_python(pair[1])
                        if pair[0] == self.instance:
                            string = value
                            for cut_string in cut_the_string(string, 95 * settings.WIDTH_SCALE):
                                self.data.append(cut_string.replace(';', '\n\t'))
                            string = data_property.python_name
                            for cut_string in cut_the_string(string, 95 * settings.WIDTH_SCALE):
                                self.data.append(cut_string.replace(';', '\n\t'))
                else:
                    self.communications.append(data_property)
                    self.objects_communication[data_property] = []
            for communication in self.communications:
                for pair in list(communication.get_relations()):
                    value = convert_to_python(pair[1])
                    if pair[0] == self.instance:
                        if value not in self.objects_communication[communication]:
                            self.objects_communication[communication].append(value)
            lines = []
            for i in self.communications:
                result = i.python_name
                value = ''
                for pair in i.get_relations():
                    value = pair[1]
                    if convert_to_python(value) in self.objects_communication[i]:
                        value = f' [{convert_to_python(value.is_a[0])}]'
                        if 'Снятие' in value or 'Установка' in value or 'Обслуживание' in value:
                            value = ' [Ремонтная работа]'
                        if len(self.objects_communication[i]) > 1:
                            if 'ТМ' in value:
                                value = ' [ТМ]'
                            if 'ЕО' in value:
                                value = ' [ЕО]'
                            if 'НН' in value:
                                value = ' [НН]'
                        break
                result += value
                lines.append(result)
            self.communication_window.lines = lines
            self.object_window.lines = []
            self.object_window.slider_y = 0
            self.object_window.slider_x = 0
            lines = []
            for i in range(1, len(self.data), 2):
                string = self.data[i]
                lines.append(f'{string}: {self.data[i - 1]}')
            self.data_window.lines = lines
            link = self.clicked_communication
            if not link is None:
                link.color = colors['dark_purple']
                link.draw()
                result = None
                for object_property in self.onto.properties():
                    if object_property.python_name == link.text.split('[')[0][:-1]:
                        result = object_property
                        break
                self.objects = []
                self.objects = self.objects_communication[result]
                lines = []
                for line in self.objects:
                    lines.append(convert_to_python(line))
                self.object_window.lines = lines
                self.communication_window.word = self.instance_name

    def find_docket(self, name):
        """Метод поиска экземпляра
        :param name: название экземпляра, который нужно найти
        :type name: str
        :return False, если не найден, иначе list из двух элементов [путь, имя]
        """
        all_classes = []
        for i in self.onto.classes():
            if len(list(i.ancestors())) == 2:
                all_classes.append(i)
        current_path = [all_classes]
        for vertex in current_path[0]:
            if str(type(vertex)) == "<class 'owlready2.entity.ThingClass'>":
                result_dfs = self.dfs(vertex, name, current_path)
                if result_dfs:
                    return result_dfs
        return False

    def dfs(self, vertex, name, current_path):
        """Метод рекурсивного поиска экземпляра
        :param vertex: Текущая вершина
        :type vertex: list
        :param name: название экземпляра, который нужно найти
        :type name: str
        :param current_path: Текущий проделанный путь
        :type current_path: list
        :return False, если не найден, иначе list из двух элементов [путь, имя]
        """
        new_list = list(vertex.subclasses())
        for instance in list(vertex.instances()):
            if instance.is_a[0] == vertex:
                new_list.append(instance)
        for next_vertex in new_list:
            new_current_path = current_path.copy()
            if str(type(next_vertex)) == "<class 'owlready2.entity.ThingClass'>":
                new_current_path.append(new_list)
                result_dfs = self.dfs(next_vertex, name, new_current_path)
                if result_dfs:
                    return result_dfs
            else:
                if convert_to_python(next_vertex) == name:
                    current_path.append(new_list)
                    return [current_path, next_vertex]
        return False
