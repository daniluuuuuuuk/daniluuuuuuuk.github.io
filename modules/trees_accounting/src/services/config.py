from PyQt5.QtCore import QSettings
import os


class Settings:
    def __init__(self, **args):
        self.settings = QSettings(
            BasicDir().get_basic_dir(name="trial_area.ini"), QSettings.IniFormat
        )
        self.group = args["group"]
        self.key = args["key"]
        if (
            len(self.settings.allKeys()) < 12
        ):  # ! 12 - текущее значение ключей, если их меньше -делаем дефолтный конфиг
            self.create_default_config()

    def add_setting(self, value):
        self.value = value

        if type(value) is not list:
            self.settings.beginGroup(self.group)
            self.settings.setValue(self.key, self.value)
            self.settings.endGroup()
            self.settings.sync()
        else:
            self.settings.beginWriteArray(self.group)
            self.settings.setValue(self.key, self.value)
            self.settings.setArrayIndex(len(self.value) - 1)
            self.settings.endArray()

    def read_setting(self):
        if self.settings.value(self.group + "/" + self.key) is not None:
            return self.settings.value(self.group + "/" + self.key)
        else:
            pass

    def create_default_config(self):
        self.settings.beginGroup("Default_Settings")
        self.settings.setValue("caliper_port", "COM1")
        self.settings.endGroup()

        self.settings.beginGroup("Database")
        self.settings.setValue("host", "localhost")
        self.settings.setValue("user", "postgres")
        self.settings.setValue("password", "loo98Yt5")
        self.settings.setValue("database", "trial_area")
        self.settings.setValue("port", "5432")
        self.settings.endGroup()

        self.settings.beginWriteArray("Selected_species")
        self.settings.setValue("species", ["el", "sosna", "dub"])
        self.settings.setArrayIndex(3)
        self.settings.endArray()

        self.settings.beginWriteArray("Caliper")
        self.settings.setValue("existing_ports", ["COM1", "COM2"])
        self.settings.setArrayIndex(1)
        self.settings.endArray()

        self.settings.beginWriteArray("Diameters")
        self.settings.setValue(
            "dmrs",
            [
                8,
                12,
                16,
                20,
                24,
                28,
                32,
                36,
                40,
                44,
                48,
                52,
                56,
                60,
                64,
                68,
                72,
                76,
                80,
                84,
                88,
                92,
                96,
                100,
                104,
                108,
                112,
                116,
                120,
                124,
                128,
                132,
                136,
            ],
        )
        self.settings.setArrayIndex(1)
        self.settings.endArray()

        self.settings.sync()


class BasicDir:
    def get_basic_dir(self, name):
        """
        Определяет каталог модуля
        пример: C:\\OSGeo4W64\\apps\\qgis\\python\\plugins\\QgsLes\\modules\\trial_area\\
        """
        basepath = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        return os.path.join(basepath, name)
