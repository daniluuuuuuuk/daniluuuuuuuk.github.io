try:
    import util
except:
    from .. import util

from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QTableWidgetItem,
    QDialog,
    QHeaderView,
    QTableWidget,
    QStyledItemDelegate,
)


UI_TAX_DESCRIPTION = uic.loadUiType(
    util.resolvePath("ui\\taxationDescription.ui")
)[0]


class AlignDelegate(QStyledItemDelegate):
    """
    Делегат для выравнивания текста
    """

    def initStyleOption(self, option, index):
        super(AlignDelegate, self).initStyleOption(option, index)
        option.displayAlignment = Qt.AlignCenter


class TaxationDescription(QDialog, UI_TAX_DESCRIPTION):
    """
    Окно для отображения таксационных характеристик выдела.

    Args:
        QtWidgets ([type]): [Наследуемся от диалогового окна]
        UI_TAX_DESCRIPTION ([type]): [Загрузка UI файла]
    """

    def __init__(self, tax_data: dict, parent=None):
        """
        Открытие окна
        Args:
            tax_data (dict): [
        {
            "lh_name": "Бресткое",                  # Название лесхоза
            "lch_name": "Орешковичское",            # Название лесничества
            "num_kv": 6,                            # Номер квартала
            "num_vd": 15,                           # Номер выдела (ов)
            "identity": 501020006015,               #
            "bonitet": "1А",                        # Бонитет
            "tl": "КИС",                            # Тип леса
            "tum": "Д2",                            # ТУМ
            "m10": [                                # Характеристики десятого макета ForestBase по ярусам
                {
                    "identity": 501020006015,       #
                    "formula": "10Б",               # Формула состава
                    "dmr": 30,                      # Средний диаметр
                    "proish": None,                 # Происхождение
                    "poln": "0",                    # Полнота
                    "height": 30,                   # Средняя высота
                    "age": 75,                      # Средний возраст
                    "yarus": 1,                     # Ярус
                    "zapas": 220,                   # Запас
                },
                {
                    "identity": 501020006015,
                    "formula": "10Е",
                    "dmr": 14,
                    "proish": None,
                    "poln": "0",
                    "height": 15,
                    "age": 40,
                    "yarus": 2,
                    "zapas": 120,
                },
            ],
        }
            ]
            parent ([type], optional): [Родительское окно]. Defaults to None.
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.config_tables()
        self.fill_data(tax_data)

    def config_tables(self):
        """
        Подготавливаю таблицы
        """
        # Отношение ширины таблиц
        self.splitter.setStretchFactor(0, 2)
        self.splitter.setStretchFactor(1, 4)
        # Выставляю ширину столбцов
        self.tableWidget.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeToContents
        )
        self.tableWidget.verticalHeader().setSectionResizeMode(
            QHeaderView.ResizeToContents
        )
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget_2.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeToContents
        )
        self.tableWidget_2.horizontalHeader().setStretchLastSection(True)

        # Таблицы только для чтения
        self.tableWidget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tableWidget_2.setEditTriggers(QTableWidget.NoEditTriggers)

        # Отключаю возможно выделения ячеек
        self.tableWidget.setFocusPolicy(Qt.NoFocus)
        self.tableWidget_2.setFocusPolicy(Qt.NoFocus)

        # Выравниваю текст у таблиц
        self.tableWidget.setItemDelegate(AlignDelegate(self.tableWidget))
        self.tableWidget_2.setItemDelegate(AlignDelegate(self.tableWidget_2))

    def fill_data(self, tax_data: dict):
        """
        Заполняю таблицу данными

        Args:
            tax_data (dict): [Данные для заполнения]

        Returns:
            bool: [В случае удачного заполнения возвращается True]
        """

        tax_data["m10"] = sorted(
            tax_data["m10"], key=lambda x: x["yarus"], reverse=True
        )  # Сортирую, что бы удобно было заполнять таблицу

        for yar in tax_data["m10"]:
            self.tableWidget_2.insertRow(0)
            self.tableWidget_2.setItem(
                0, 0, QTableWidgetItem(str(yar["yarus"]))
            )
            self.tableWidget_2.setItem(0, 1, QTableWidgetItem(str(yar["dmr"])))
            self.tableWidget_2.setItem(0, 2, QTableWidgetItem(yar["proish"]))
            self.tableWidget_2.setItem(0, 3, QTableWidgetItem(yar["poln"]))
            self.tableWidget_2.setItem(
                0, 4, QTableWidgetItem(str(yar["height"]))
            )
            self.tableWidget_2.setItem(0, 5, QTableWidgetItem(str(yar["age"])))
            self.tableWidget_2.setItem(
                0, 6, QTableWidgetItem(str(yar["zapas"]))
            )
            self.tableWidget_2.setItem(0, 7, QTableWidgetItem(yar["formula"]))

        del tax_data["m10"]
        for row in range(len(tax_data.keys())):
            self.tableWidget.insertRow(row)
            self.tableWidget.setItem(
                row, 0, QTableWidgetItem(list(tax_data.keys())[row])
            )
            self.tableWidget.setItem(
                row, 1, QTableWidgetItem(str(list(tax_data.values())[row]))
            )
            self.tableWidget.item(row, 1).setToolTip(
                str(list(tax_data.values())[row])
            )
