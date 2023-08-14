""" Модули для работы с данными и визуализации их"""
import datetime
import sys
import webbrowser
import os
import pygame
import pyperclip
import owlready2
from pygame import Surface
import settings# pylint: disable=E0401
from utils import next_page, last_page, draw_menu_bar, is_over, convert_to_python# pylint: disable=E0401
from Classes.docket import Docket# pylint: disable=E0401
from settings import colors, MAIN_FONT# pylint: disable=E0401
from Classes.button import Button# pylint: disable=E0401, C0412
from Classes.input import Input# pylint: disable=E0401

class View:
    """ Класс страницы просмотра экземпляров """

    def __init__(self, screen: Surface, onto):
        """Инициализация страницы запросов
        :param screen: Поверхность, на которой будет происходить отрисовка
        :type screen: Surface
        """
        self.screen = screen
        self.main_color = colors['dark_yellow']
        self.second_color = colors['light_yellow']
        self.background_color = colors['background']
        self.menu_buttons = []
        self.find_input = None
        self.next_button = None
        self.last_button = None
        self.back_button = None
        self.buttons = []
        self.page = 1
        self.final_list = []
        self.current_path = []
        self.current_dockets = []
        self.inputs = []
        self.instance_name = ''
        self.manager = None
        self.onto = owlready2.get_ontology(f'{onto}').load()
        self.shift_pressed = False
        self.ctrl_pressed = False
        self.backspace_pressed = False
        self.instance = None
        self.build()
        self.last_click = datetime.datetime.now().microsecond
        all_classes = []
        for i in self.onto.classes():
            if len(list(i.ancestors())) == 2:
                all_classes.append(i)
        self.current_path = []
        self.current_path.append(all_classes)
        self.create_dockets()

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
        pygame.font.init()
        font = pygame.font.SysFont(MAIN_FONT,
                                   int(30 * settings.HEIGHT_SCALE * settings.WIDTH_SCALE))
        self.back_button.draw()
        text = ''
        for inp in self.inputs:
            text = inp.text
            inp.draw()
        self.final_list = []
        for docket in self.current_path[-1]:
            name = docket.name
            if text.lower() in name.replace('_', ' ').lower():
                self.final_list.append(docket)

        max_pages = len(self.final_list) // 16
        if len(self.final_list) % 16 != 0:
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
        x_coordinate = 50 * settings.WIDTH_SCALE
        y_coordinate = 225 * settings.HEIGHT_SCALE
        path_text = 'Path:'
        for sub_path in self.current_path[1:]:
            path_text += '/'
            name = ''
            try:
                name = str(sub_path[0].is_a)[1:-1].split('.')[1:]
            except IndexError:
                pass
            for part in name:
                path_text += part
        if len(path_text) > 100 * settings.WIDTH_SCALE:
            path_text = 'Классификатор: /'
            sub_path = self.current_path[1]
            name = str(sub_path[0].is_a)[1:-1].split('.')[1:]
            for part in name:
                path_text += part
            path_text += '/.../'
            sub_path = self.current_path[-1]
            name = str(sub_path[0].is_a)[1:-1].split('.')[1:]
            for part in name:
                path_text += part
        render_line = font.render(path_text, True, colors['black'])
        if max_pages != 0:
            self.screen.blit(
                render_line,
                (
                    50 * settings.WIDTH_SCALE, 165 * settings.HEIGHT_SCALE
                )
            )
        for i in range(((self.page - 1) * 16), min(len(self.final_list), self.page * 16)):
            docket = self.final_list[i]
            if str(type(docket)) == "<class 'owlready2.entity.ThingClass'>":
                name = docket.name
                docket = Docket((x_coordinate,
                                y_coordinate, 236 * settings.WIDTH_SCALE,
                                100 * settings.HEIGHT_SCALE), (colors["dark_yellow"],
                                                               name.replace('_', ' '),
                                'Классификатор',
                                                               colors['light_yellow']),
                                self.screen)
            else:
                name = docket.name
                docket = Docket((x_coordinate,
                                y_coordinate, 236 * settings.WIDTH_SCALE,
                                100 * settings.HEIGHT_SCALE), (colors['very_dark_purple'],
                                                               name.replace('_', ' '),
                                'Экземпляр',
                                                               colors['dark_purple']),
                                self.screen)
            if text.lower() in name.lower():
                x_coordinate += 286 * settings.WIDTH_SCALE
                if x_coordinate >= 1100 * settings.WIDTH_SCALE:
                    x_coordinate = 50 * settings.WIDTH_SCALE
                    y_coordinate += 150 * settings.HEIGHT_SCALE
                docket.draw()
        draw_menu_bar(self.screen, self.main_color, self.menu_buttons)
        pygame.display.flip()

    def update(self):
        """ Метод обработки событий """
        if self.backspace_pressed:
            for inp in self.inputs:
                if inp.other_params[1]:
                    inp.text = inp.text[:-1]
                    pygame.time.wait(200)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: # pylint: disable=E1101
                sys.exit()
            if event.type == pygame.VIDEORESIZE:# pylint: disable=E1101
                old_surface_saved = self.screen
                self.screen = pygame.display.set_mode((event.w, event.h),
                                                      pygame.RESIZABLE)# pylint: disable=E1101
                self.screen.blit(old_surface_saved, (0, 0))
                settings.WIDTH_SCALE = event.w / settings.size[0]
                settings.HEIGHT_SCALE = event.h / settings.size[1]
                self.build()
            if event.type == pygame.MOUSEBUTTONDOWN:# pylint: disable=E1101
                for button in self.menu_buttons:
                    if is_over(button, pygame.mouse.get_pos()):
                        if button.text == 'Запрос':
                            return 'request'
                        if button.text == 'Главная':
                            return 'main'
                        if button.text == 'Выход':
                            return 'exit'

            if event.type == pygame.KEYDOWN:# pylint: disable=E1101
                self.final_list = []
                for docket in self.current_path[-1]:
                    name = docket.name
                    if self.find_input.text.lower() in name.replace('_', ' ').lower():
                        self.final_list.append(docket)
                x_coordinate = 50 * settings.WIDTH_SCALE
                y_coordinate = 225 * settings.HEIGHT_SCALE
                self.current_dockets = []
                for i in range(((self.page - 1) * 16), min(len(self.final_list), self.page * 16)):
                    docket = self.final_list[i]
                    if str(type(docket)) == "<class 'owlready2.entity.ThingClass'>":
                        name = docket.name
                        docket = Docket((x_coordinate,
                                        y_coordinate, 236 * settings.WIDTH_SCALE,
                                        100 * settings.HEIGHT_SCALE), (colors["dark_yellow"],
                                                                       name.replace('_', ' '),
                                        'Классификатор',
                                                                       colors['light_yellow']),
                                        self.screen)
                    else:
                        name = docket.name
                        docket = Docket((x_coordinate,
                                        y_coordinate, 236 * settings.WIDTH_SCALE,
                                        100 * settings.HEIGHT_SCALE), (colors['very_dark_purple'],
                                                                       name.replace('_', ' '),
                                        'Экземпляр',
                                                                       colors['dark_purple']),
                                        self.screen)
                    if self.find_input.text.lower() in name.lower():
                        x_coordinate += 286 * settings.WIDTH_SCALE
                        if x_coordinate >= 1100 * settings.WIDTH_SCALE:
                            x_coordinate = 50 * settings.WIDTH_SCALE
                            y_coordinate += 150 * settings.HEIGHT_SCALE
                        self.current_dockets.append(docket)
                if event.key == pygame.K_ESCAPE: # pylint: disable=E1101
                    if self.find_input.other_params[1]:
                        self.find_input.other_params[1] = False
                    else:
                        if len(self.current_path) > 1:
                            self.current_path = self.current_path[:-1]
                            self.page = 1
                            self.find_input.text = ''
                if event.key == pygame.K_TAB: # pylint: disable=E1101
                    if self.find_input.other_params[1]:
                        self.find_input.other_params[1] = False
                    else:
                        self.find_input.other_params[1] = True
                if event.key in [pygame.K_d, pygame.K_RIGHT]:# pylint: disable=E1101
                    if not self.find_input.other_params[1]:
                        self.page = next_page(self.page, self.final_list, 16)
                if event.key in [pygame.K_a, pygame.K_LEFT]: # pylint: disable=E1101
                    if not self.find_input.other_params[1]:
                        self.page = last_page(self.page, self.final_list, 16)
                for inp in self.inputs:
                    if inp.other_params[1]:
                        if event.key == pygame.K_BACKSPACE:# pylint: disable=E1101
                            self.backspace_pressed = True
                        elif pygame.key.name(event.key) == 'left shift':
                            self.shift_pressed = True
                        elif pygame.key.name(event.key) == 'left ctrl':
                            self.ctrl_pressed = True
                        elif event.key == pygame.K_RETURN:# pylint: disable=E1101
                            inp.other_params[1] = False
                            self.page = 1
                        else:
                            if self.ctrl_pressed:
                                if event.key in [pygame.K_v]:
                                    inp.text += pyperclip.paste()
                            else:
                                if event.unicode != '\t':
                                    inp.text += event.unicode
            if event.type == pygame.KEYUP: # pylint: disable=E1101
                if pygame.key.name(event.key) == 'left shift':
                    self.shift_pressed = False
                if event.key == pygame.K_BACKSPACE:# pylint: disable=E1101
                    self.backspace_pressed = False
                if pygame.key.name(event.key) == 'left ctrl':
                    self.ctrl_pressed = False
            if event.type == pygame.MOUSEBUTTONDOWN:# pylint: disable=E1101
                new_click = datetime.datetime.now().microsecond
                if abs(new_click - self.last_click) > 10000:
                    self.last_click = new_click
                    self.final_list = []
                    for docket in self.current_path[-1]:
                        name = docket.name
                        if self.find_input.text.replace('_', ' ').lower() in\
                                name.replace('_', ' ').lower():
                            self.final_list.append(docket)
                    x_coordinate = 50 * settings.WIDTH_SCALE
                    y_coordinate = 225 * settings.HEIGHT_SCALE
                    self.current_dockets = []
                    for i in range(((self.page - 1) * 16), min(len(self.final_list),
                                                               self.page * 16)):
                        docket = self.final_list[i]
                        if str(type(docket)) == "<class 'owlready2.entity.ThingClass'>":
                            name = docket.name
                            docket = Docket((x_coordinate,
                                            y_coordinate, 236 * settings.WIDTH_SCALE,
                                            100 * settings.HEIGHT_SCALE), (colors["dark_yellow"],
                                                                           name.replace('_', ' '),
                                            'Классификатор',
                                                                           colors['light_yellow']),
                                            self.screen)
                        else:
                            name = docket.name
                            docket = Docket((x_coordinate,
                                            y_coordinate, 236 * settings.WIDTH_SCALE,
                                            100 * settings.HEIGHT_SCALE),
                                            (colors['very_dark_purple'],
                                            name.replace('_', ' '),
                                            'Экземпляр',
                                            colors['dark_purple']),
                                            self.screen)
                        if self.find_input.text.lower() in name.lower():
                            x_coordinate += 286 * settings.WIDTH_SCALE
                            if x_coordinate >= 1100 * settings.WIDTH_SCALE:
                                x_coordinate = 50 * settings.WIDTH_SCALE
                                y_coordinate += 150 * settings.HEIGHT_SCALE
                            self.current_dockets.append(docket)
                    i = (self.page - 1) * 16
                    for button in self.current_dockets:
                        if is_over(button, pygame.mouse.get_pos()):
                            if i < len(self.final_list):
                                if str(type(self.final_list[i])) ==\
                                        "<class 'owlready2.entity.ThingClass'>":
                                    new_list = list(self.final_list[i].subclasses())
                                    for instance in list(self.final_list[i].instances()):
                                        if instance.is_a[0] == self.final_list[i]:
                                            new_list.append(instance)
                                    self.current_path.append(new_list)
                                    self.page = 1
                                    self.find_input.text = ''
                                    pygame.time.wait(10)
                                    return 'view'
                                self.instance_name = self.final_list[i].name
                                name = convert_to_python(self.instance_name)
                                for file_format in os.listdir(f'{os.getcwd()}\\Docs'):
                                    if file_format.lower() in name.lower():
                                        webbrowser.open(
                                            f'{os.getcwd()}\\Docs\\{file_format}\\{name}', new=2)
                                self.instance = self.final_list[i]
                                self.manager.get_tab('instance').clicked_communication = None
                                with open('last_instances.txt', 'a') as file: # pylint: disable=W1514
                                    with open('last_instances.txt', 'r') as string:  # pylint: disable=W1514
                                        strings = string.readlines()
                                        if strings:
                                            name = strings[-1]
                                            if name[:-1] != self.instance_name:
                                                file.write(f'{self.instance_name}\n')
                                        else:
                                            file.write(f'{self.instance_name}\n')
                                return 'instance'
                        i += 1
                    if is_over(self.back_button, pygame.mouse.get_pos()):
                        if len(self.current_path) > 1:
                            self.current_path = self.current_path[:-1]
                            self.page = 1
                            self.find_input.text = ''
                    if is_over(self.next_button, pygame.mouse.get_pos()):
                        self.page = next_page(self.page, self.final_list, 16)
                    if is_over(self.last_button, pygame.mouse.get_pos()):
                        self.page = last_page(self.page, self.final_list, 16)
                    self.find_input.other_params[1] = is_over(self.find_input,
                                                              pygame.mouse.get_pos())
        return 'view'

    def create_dockets(self):
        """ Метод создания табличек для отлеживания нажатий """
        x_coordinate = 50 * settings.WIDTH_SCALE
        y_coordinate = 225 * settings.HEIGHT_SCALE
        for i in range(((self.page - 1) * 16), min(len(self.current_path[-1]), self.page * 16)):
            docket = self.current_path[-1][i]
            if str(type(docket)) == "<class 'owlready2.entity.ThingClass'>":
                name = docket.name
                docket = Docket((x_coordinate,
                                y_coordinate, 236 * settings.WIDTH_SCALE,
                                100 * settings.HEIGHT_SCALE),
                                (colors["dark_yellow"],
                                name.replace('_', ' '),
                                'Классификатор',
                                colors['light_yellow']),
                                self.screen)
            else:
                name = docket.name
                docket = Docket((x_coordinate,
                                y_coordinate, 236 * settings.WIDTH_SCALE,
                                100 * settings.HEIGHT_SCALE),
                                (colors['very_dark_purple'],
                                name.replace('_', ' '),
                                'Экземпляр',
                                colors['dark_purple']),
                                self.screen)
            if self.find_input.text.lower() in name.lower():
                x_coordinate += 286 * settings.WIDTH_SCALE
                if x_coordinate >= 1100 * settings.WIDTH_SCALE:
                    x_coordinate = 50 * settings.WIDTH_SCALE
                    y_coordinate += 150 * settings.HEIGHT_SCALE
                self.current_dockets.append(docket)

    def update_model(self, onto):
        """Метод обновления страницы под новую модель"""
        self.onto = owlready2.get_ontology(f'{onto}').load()
        self.build()

    def build(self):
        """ Метод инициализации всего необходимого для загрузки страницы """
        self.find_input = Input((622 * settings.WIDTH_SCALE, 60 * settings.HEIGHT_SCALE,
                                 (236 + 908 - 622) * settings.WIDTH_SCALE,
                                 70 * settings.HEIGHT_SCALE),
                                self.main_color, self.screen, 'Поиск')
        self.inputs = [self.find_input]
        self.back_button = Button((50 * settings.WIDTH_SCALE, 60 * settings.HEIGHT_SCALE,
                                   522 * settings.WIDTH_SCALE, 70 * settings.HEIGHT_SCALE),
                                  (self.background_color, colors['very_light_grey'],
                                  self.main_color, colors['black']),
                                  'Вернуться назад', self.screen)
        self.next_button = Button(((356 + 286) * settings.WIDTH_SCALE, 830 * settings.HEIGHT_SCALE,
                                   200 * settings.WIDTH_SCALE, 50 * settings.HEIGHT_SCALE),
                                  (self.background_color, colors['very_light_grey'],
                                  self.main_color, colors['black']),
                                  'Следущая', self.screen)
        self.last_button = Button((356 * settings.WIDTH_SCALE, 830 * settings.HEIGHT_SCALE,
                                   200 * settings.HEIGHT_SCALE, 50 * settings.HEIGHT_SCALE),
                                  (self.background_color, colors['very_light_grey'],
                                  self.main_color, colors['black']),
                                  'Предыдущая', self.screen)
        self.buttons = [
            self.back_button
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
                   (self.background_color, self.background_color, self.background_color,
                   colors['black']), 'Просмотр', self.screen),
            Button((240 * settings.WIDTH_SCALE,
                   0, 120 * settings.WIDTH_SCALE,
                   30 * settings.HEIGHT_SCALE),
                   (self.main_color, self.second_color, self.main_color, colors['background']),
                   'Запрос', self.screen)
        ]
