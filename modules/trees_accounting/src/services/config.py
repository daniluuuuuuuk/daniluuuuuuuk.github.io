from PyQt5.QtCore import QSettings
from typing import Union
import os
import platform


class BasicDir:
    """
    Получение полных путей к файлам
    """

    @staticmethod
    def get_module_dir(relative_path):
        """Получение полного пути к папке текущего модуля"""
        # C:\Users\user\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\GisLes\modules\trees_accounting\src\
        if platform.system() == "Windows":
            os_path_separator = "\\"
        else:
            os_path_separator = "/"
        current_full_path = os.path.dirname(os.path.realpath(__file__))
        module_folders_array = current_full_path.split(os_path_separator)[
            :-1
        ]  # up 3 level
        module_path = os_path_separator.join(module_folders_array)
        full_file_path = module_path + os_path_separator + relative_path
        return full_file_path

    @staticmethod
    def get_plugin_dir(relative_path):
        """Получение полного пути к папке всего плагина"""
        # C:\Users\user\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\GisLes
        if platform.system() == "Windows":
            os_path_separator = "\\"
        else:
            os_path_separator = "/"
        current_full_path = os.path.dirname(os.path.realpath(__file__))
        plugin_folders_array = current_full_path.split(os_path_separator)[
            :-4
        ]  # up 3 level
        plugin_path = os_path_separator.join(plugin_folders_array)
        full_file_path = plugin_path + os_path_separator + relative_path

        return full_file_path


class Config:

    default_ini = BasicDir.get_plugin_dir("config.ini")

    def __init__(self, ini_path=default_ini):
        self.settings = QSettings(ini_path, QSettings.IniFormat)

    def add_setting(self, group: str, key: str, value: str) -> bool:

        if type(value) is not list:
            self.settings.beginGroup(group)
            self.settings.setValue(key, value)
            self.settings.endGroup()
            self.settings.sync()
        else:
            self.settings.beginWriteArray(group)
            self.settings.setValue(key, value)
            self.settings.setArrayIndex(len(value) - 1)
            self.settings.endArray()

        return True

    def read_setting(self, group: str, key: str) -> Union[str, None]:
        return self.settings.value(group + "/" + key)
