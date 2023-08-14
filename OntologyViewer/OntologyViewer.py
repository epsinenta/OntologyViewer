# pylint: disable=C0103
""" Модули для визуализации данных """
import datetime
import sys
import traceback
from threading import Thread
import pygame
import settings

from Tabs.main import Main
from Tabs.request import Request
from Tabs.view import View
from Tabs.instance import Instance
from Classes.manager import Manager

def run(manager):
    """Функция запуска приложения
    :param manager: менеджер управления приложением
    :type manager: Manager
    """
    manager.set_status('main')
    while manager.status != 'exit':
        if manager.last_status != manager.status:
            manager.get_tab(manager.status).build()
        manager.last_status = manager.status
        manager.set_status(manager.get_tab(manager.status).run(manager))
        if '.owl' in manager.status:
            name = manager.status.split('\\')[-1]
            last_model = manager.onto
            try:
                build(f'Models/{name}', True)
            except FileNotFoundError:
                manager.set_status('main')
                build(last_model)
    sys.exit()

def build(ontology_name, with_clear = False):
    """ Функция инициалиация страниц """
    try:
        screen = pygame.display.set_mode(settings.size, pygame.RESIZABLE)# pylint: disable=E1101
        pygame.display.set_caption('OntologyViewer')
        onto = f"file://{ontology_name}"
        settings.ONTO_NAME = ontology_name
        main = Main(screen, onto)
        request = Request(screen, onto)
        view = View(screen, onto)
        instance = Instance(screen, onto)
        manager = Manager(screen, (main, view, request, instance))
        manager.set_status('main')
        manager.onto = ontology_name
        if with_clear:
            with open('last_model.txt', 'w') as last_model: # pylint: disable=W1514
                last_model.write(ontology_name.split('/')[-1]) # pylint: disable=W1514
            with open('last_instances.txt', 'w') as last_instances: # pylint: disable=W1514
                last_instances.seek(0)
            with open('last_requests.txt', 'w') as last_requests: # pylint: disable=W1514
                last_requests.seek(0)
        run(manager)
    except:
        with open('log.txt', 'a') as file:  # pylint: disable=W1514
            if traceback.format_exc().split('\n')[-2] != 'SystemExit':
                file.write(f'{datetime.datetime.now()}:\n')
                file.write(f'{traceback.format_exc()}\n')


if __name__ == "__main__":
    try:
        with open('last_model.txt', 'r') as file_model: # pylint: disable=W1514
            onto_name = file_model.readline()
            th = Thread(target=build, args=(f'Models/{onto_name}', ))
            th.start()
    except:
        with open('log.txt', 'a') as file:  # pylint: disable=W1514
            file.write(f'{datetime.datetime.now()}:\n')
            file.write(f'{traceback.format_exc()}\n')