""" Модуль для визуализации данных """
from pygame import Surface

class Manager:
    """ Класс менеджер управления приложением """

    def __init__(self, screen: Surface, tabs: tuple):
        """Инициализация главной вкладки
        :param screen: Поверхность, на которой будет происходить отрисовка
        :type screen: Surface
        :param Tabs: Вкладки приложения
        :type Tabs: tuple
        """
        self.screen = screen
        self.navigation = {
            'main': tabs[0],
            'view': tabs[1],
            'request': tabs[2],
            'instance': tabs[3],
        }
        self.status = 'main'
        self.last_status = 'main'
        self.onto = ''

    def get_tab(self, tab_name):
        """ Метод получения экземпляра страницы по ее названию
        :param tab_name: Имя страницы
        :type tab_name: str
        """
        return  self.navigation[tab_name]

    def set_status(self, new_status):
        """Метод изменения статуса
        :param new_status: Новый статус
        :type new_status: str
        """
        self.status = new_status
