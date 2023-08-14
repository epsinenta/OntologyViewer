""" Модули для визуализации и создания случайных данных """
import pygame
from pygame import Surface
import matplotlib.pyplot
import networkx
import pymorphy2

import settings

def next_page(current_page: int, strings: list, count: int):
    """ Функция листания страниц вперед
    :param current_page: номер текущей страницы
    :type current_page: int
    :param strings:  Все строки
    :type strings: list
    :param count:  Количество строк на одной странице
    :return: int - новый номер страницы
    """
    current_page += 1
    if len(strings) % count != 0:
        current_page %= (len(strings) // count + 2)
    else:
        current_page %= (len(strings) // count + 1)
    if not current_page:
        current_page = 1
    return current_page

def last_page(current_page: int, strings: list, count: int):
    """ Функция листания страниц назад
    :param current_page: номер текущей страницы
    :type current_page: int
    :param strings:  Все строки
    :type strings: list
    :param count:  Количество строк на одной странице
    :return: int - новый номер страницы
    """
    current_page -= 1
    if not current_page:
        if len(strings) % count == 0:
            current_page = (len(strings) // count)
        else:
            current_page = (len(strings) // count) + 1
    return current_page

def draw_menu_bar(screen: Surface, main_color: tuple, menu_buttons: list):
    """ Метод отрисовки панели передвижения
    :param screen: Экран на котором рисуется панель
    :type screen: Surface
    :param main_color: Основной цвет модели
    :type main_color: tuple
    :param menu_buttons: Кнопки панели
    :type menu_buttons: list
    """
    pygame.draw.rect(screen, main_color, (0, 0, 1200 * settings.WIDTH_SCALE,
                                          32 * settings.HEIGHT_SCALE), 0)
    for button in menu_buttons:
        button.draw()

def convert_to_python(value):
    """ Функия перевода имени из онтологической модели в
     удобное для прочтения
     :param value: Изначальное название
     :type value: str
     :return Новое значение
     """
    value = str(value)
    onto_name = settings.ONTO_NAME.split('/')[1].split('.')[0]
    if onto_name not in value:
        return value
    index = value.find('.')
    if index != -1:
        return value[index + 1:]
    return value

def cut_the_string(string, length):
    """Функия разделения строки"""
    string = string.replace('_', ' ')
    string = string.replace('№', '#')
    result_strings = ['']
    if len(string) > length:
        string_list = string.split()
        for new_string in string_list:
            if len(result_strings[-1]) + len(new_string) < length:
                result_strings[-1] += new_string + ' '
            else:
                result_strings.append(new_string + ' ')
    else:
        result_strings = [string]
    return result_strings

def morph_convert(line, word):
    """Функция для склонения глаголов по примеру существительного"""
    result_string = ''
    morph = pymorphy2.MorphAnalyzer()
    gender = ''
    number = ''
    for string in word.replace('_', ' ').split(' '):
        parse = morph.parse(string)[0]
        if 'NOUN' in parse.tag:
            gender = parse.tag.gender
            number = parse.tag.number
            break
        if 'NUMB' in parse.tag and not gender and not number:
            gender = 'femn'
            number = 'sing'
    for string in line.split():
        parse = morph.parse(string)[0]
        if 'VERB' in parse.tag or 'PRTS' in parse.tag:
            time = parse.tag.tense
            person = parse.tag.person
            new = parse
            if not person:
                new = new.inflect({gender, time})
            result_string += new.word + ' '
        else:
            result_string += string + ' '
    if not result_string:
        result_string = line
    return result_string

def model_request(main_object, object_property, sub_object, onto, with_verb=False):
    """Функция поиска результатов на запрос по модели """
    request_result = []
    history = []
    main_object = main_object.replace(' ', '_')
    object_property = object_property.replace(' ', '_')
    sub_object = sub_object.replace(' ', '_')
    if main_object != '':
        if onto[main_object] is not None:
            for prop in onto[main_object].get_properties():
                if prop not in onto.data_properties():
                    if object_property != '':
                        if prop.python_name == object_property:
                            for pair in list(prop.get_relations()):
                                value = convert_to_python(pair[1])
                                if pair[0] == onto[main_object]:
                                    if sub_object == '':
                                        string = f'{main_object} ' \
                                                 f'{prop.python_name} ' \
                                                 f'{value}'
                                        if string not in history:
                                            history.append(string)
                                            request_result.append(
                                                [string.replace('_', ' ').replace('№', '#'),
                                                 main_object, value])
                                    else:
                                        if value == sub_object:
                                            string = f'{main_object} ' \
                                                     f'{prop.python_name} ' \
                                                     f'{value}'
                                            if string not in history:
                                                history.append(string)
                                                request_result.append(
                                                    [string.replace('_', ' ').replace('№', '#'),
                                                     main_object, value])
                    else:
                        for pair in list(prop.get_relations()):
                            value = convert_to_python(pair[1])
                            if pair[0] == onto[main_object]:
                                if sub_object == '':
                                    string = f'{main_object} ' \
                                             f'{prop.python_name} ' \
                                             f'{value}'
                                    if string not in history:
                                        history.append(string)
                                        if with_verb:
                                            request_result.append(
                                                [string.replace('_', ' ').replace('№', '#'),
                                                 main_object, value, prop.python_name])
                                        else:
                                            request_result.append(
                                                [string.replace('_', ' ').replace('№', '#'),
                                                 main_object, value])
                                else:
                                    if value == sub_object:
                                        string = f'{main_object} ' \
                                                 f'{prop.python_name} ' \
                                                 f'{value}'
                                        if string not in history:
                                            history.append(string)
                                            request_result.append(
                                                [string.replace('_', ' ').replace('№', '#'),
                                                 main_object, value])
    else:
        for prop in onto.object_properties():
            if object_property != '':
                if prop.python_name == object_property:
                    for pair in list(prop.get_relations()):
                        value = convert_to_python(pair[1])
                        main_object = convert_to_python(pair[0])
                        if sub_object == '':
                            string = f'{main_object} ' \
                                     f'{prop.python_name} ' \
                                     f'{value}'
                            if string not in history:
                                history.append(string)
                                request_result.append(
                                    [string.replace('_', ' ').replace('№', '#'),
                                     main_object, value])
                        else:
                            if value == sub_object:
                                string = f'{main_object} ' \
                                         f'{prop.python_name} ' \
                                         f'{value}'
                                if string not in history:
                                    history.append(string)
                                    request_result.append(
                                        [string.replace('_', ' ').replace('№', '#'),
                                         main_object, value])
            else:
                properties = list(prop.get_relations())
                for pair in properties:
                    main_object = convert_to_python(pair[0])
                    value = convert_to_python(pair[1])
                    if sub_object == '':
                        string = f'{main_object} ' \
                                 f'{prop.python_name} ' \
                                 f'{value}'
                        if string not in history:
                            history.append(string)
                            request_result.append(
                                [string.replace('_', ' ').replace('№', '#'),
                                main_object, value])
                    else:
                        if value == sub_object:
                            string = f'{main_object} ' \
                                     f'{prop.python_name} ' \
                                     f'{value}'
                            if string not in history:
                                history.append(string)
                                request_result.append(
                                    [string.replace('_', ' ').replace('№', '#'),
                                     main_object, value])
    return request_result

def is_over(widget, pos: tuple):
    """ Проверка координат на нахождение внутри области кнопки
    :param widget: Объект, наведение на которого нужно проверить
    :param pos: Координаты курсора на экране
    :type pos: tuple
    :return: True, если Абсцисса и Ордината находится в области кнопки, иначе False.
    """
    if widget.x_coordinate < pos[0] < widget.x_coordinate + widget.width:
        if widget.y_coordinate < pos[1] < widget.y_coordinate + widget.height:
            return True
    return False

def run_graph(instance_name, onto):
    """
    Функция отрисовки графа
    :param instance_name: Имя экземпляра
    :type instance_name: str
    :param onto: Онтология
    """
    request_result = model_request(instance_name, '', '', onto, True)
    triplets = {}
    for string in request_result:
        triplets[(string[1].replace('_', ' '), string[2].replace('_', ' '))] = \
            morph_convert(string[3].replace('_', ' '), string[1])
    uber_dict = {
        'purple': triplets
    }
    graph = None
    graph = networkx.Graph()
    for color, dict_graph in uber_dict.items():
        for edge, point in dict_graph.items():
            graph.add_edge(*edge, weight=point)
        pos = networkx.shell_layout(graph)
        edge_labels = {(u, v): d['weight'] for u, v, d in graph.edges(data=True)}
        networkx.draw_networkx_nodes(graph, pos, node_size=0, node_color=color)
        networkx.draw_networkx_edges(graph, pos)
        networkx.draw_networkx_labels(graph, pos)
        networkx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels, font_color='b')
        matplotlib.pyplot.title(f'Экземпляр: {instance_name.replace("_", " ")}')
        matplotlib.pyplot.axis('off')
        matplotlib.pyplot.show()
