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
        # self.splitter.setStretchFactor(0, 2)
        # self.splitter.setStretchFactor(1, 4)
        # Выставляю ширину столбцов
        self.tableWidget.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeToContents
        )
        self.tableWidget.verticalHeader().setSectionResizeMode(
            QHeaderView.ResizeToContents
        )
        self.tableWidget_2.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeToContents
        )
        self.tableWidget_2.verticalHeader().setSectionResizeMode(
            QHeaderView.ResizeToContents
        )
        self.tableWidget_3.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeToContents
        )
        self.tableWidget_3.verticalHeader().setSectionResizeMode(
            QHeaderView.ResizeToContents
        )
        self.tableWidget_4.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeToContents
        )
        self.tableWidget_4.verticalHeader().setSectionResizeMode(
            QHeaderView.ResizeToContents
        )
        self.tableWidget_5.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeToContents
        )
        self.tableWidget_5.verticalHeader().setSectionResizeMode(
            QHeaderView.ResizeToContents
        )
        self.tableWidget_6.verticalHeader().setSectionResizeMode(
            QHeaderView.ResizeToContents
        )
        self.tableWidget_6.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeToContents
        )
        self.tableWidget_8.verticalHeader().setSectionResizeMode(
            QHeaderView.ResizeToContents
        )
        self.tableWidget_8.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeToContents
        )
        self.tableWidget_9.verticalHeader().setSectionResizeMode(
            QHeaderView.ResizeToContents
        )
        self.tableWidget_9.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeToContents
        )
        self.tableWidget_3.horizontalHeader().setStretchLastSection(True)
        self.tableWidget_7.verticalHeader().setSectionResizeMode(
            QHeaderView.ResizeToContents
        )
        self.tableWidget_7.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeToContents
        )
        # self.tableWidget_4.horizontalHeader().setSectionResizeMode(
        #     QHeaderView.ResizeToContents
        # )
        # self.tableWidget_4.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tableWidget.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tableWidget.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.tableWidget.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.tableWidget.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self.tableWidget_2.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tableWidget_2.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tableWidget_2.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.tableWidget_4.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tableWidget_4.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tableWidget_4.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.tableWidget_4.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.tableWidget_4.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self.tableWidget_4.horizontalHeader().setSectionResizeMode(5, QHeaderView.Stretch)
        self.tableWidget_4.horizontalHeader().setSectionResizeMode(6, QHeaderView.Stretch)
        self.tableWidget_4.horizontalHeader().setSectionResizeMode(7, QHeaderView.Stretch)
        self.tableWidget_5.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tableWidget_5.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tableWidget_6.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tableWidget_7.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tableWidget_8.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tableWidget_9.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)

        # Таблицы только для чтения
        self.tableWidget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tableWidget_2.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tableWidget_3.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tableWidget_4.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tableWidget_5.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tableWidget_6.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tableWidget_7.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tableWidget_8.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tableWidget_9.setEditTriggers(QTableWidget.NoEditTriggers)

        # Отключаю возможно выделения ячеек
        self.tableWidget.setFocusPolicy(Qt.NoFocus)
        self.tableWidget_2.setFocusPolicy(Qt.NoFocus)
        self.tableWidget_3.setFocusPolicy(Qt.NoFocus)
        self.tableWidget_4.setFocusPolicy(Qt.NoFocus)
        self.tableWidget_4.setFocusPolicy(Qt.NoFocus)
        self.tableWidget_5.setFocusPolicy(Qt.NoFocus)
        self.tableWidget_6.setFocusPolicy(Qt.NoFocus)
        self.tableWidget_7.setFocusPolicy(Qt.NoFocus)
        self.tableWidget_8.setFocusPolicy(Qt.NoFocus)
        self.tableWidget_9.setFocusPolicy(Qt.NoFocus)

        # Выравниваю текст у таблиц
        self.tableWidget.setItemDelegate(AlignDelegate(self.tableWidget))
        self.tableWidget_2.setItemDelegate(AlignDelegate(self.tableWidget_2))
        self.tableWidget_3.setItemDelegate(AlignDelegate(self.tableWidget_3))
        self.tableWidget_4.setItemDelegate(AlignDelegate(self.tableWidget_4))
        self.tableWidget_5.setItemDelegate(AlignDelegate(self.tableWidget_5))
        self.tableWidget_6.setItemDelegate(AlignDelegate(self.tableWidget_6))
        self.tableWidget_7.setItemDelegate(AlignDelegate(self.tableWidget_7))
        self.tableWidget_8.setItemDelegate(AlignDelegate(self.tableWidget_8))
        self.tableWidget_9.setItemDelegate(AlignDelegate(self.tableWidget_9))

    def fill_data(self, tax_data: dict):
        """
        Заполняю таблицу данными

        Args:
            tax_data (dict): [Данные для заполнения]

        Returns:
            bool: [В случае удачного заполнения возвращается True]
        """
    
        tax_data["m10"] = sorted(
            tax_data["m10"], key=lambda x: x["order_number"] if x["order_number"] else 0, reverse=True
        )  # Сортирую, что бы удобно было заполнять таблицу
        print(tax_data["m10"])
        for yar in tax_data["m10"]:
            self.tableWidget_4.insertRow(0)
            self.tableWidget_4.setItem(
                0, 0, QTableWidgetItem(str(yar["layer"]))
            )
            self.tableWidget_4.setItem(0, 1, QTableWidgetItem(str(yar["structure_coeff"])))
            self.tableWidget_4.setItem(0, 2, QTableWidgetItem(str(yar["wood_species"])))
            self.tableWidget_4.setItem(0, 3, QTableWidgetItem(str(yar["age"])))
            self.tableWidget_4.setItem(
                0, 4, QTableWidgetItem(str(yar["height"]))
            )
            self.tableWidget_4.setItem(0, 5, QTableWidgetItem(str(yar["diameter"])))
            self.tableWidget_4.setItem(
                0, 6, QTableWidgetItem(str(yar["fullness"]))
            )
            self.tableWidget_4.setItem(0, 7, QTableWidgetItem(str(yar["layer_stock"])))

        for undergrowth in tax_data["undergrowth_data"]:
            self.tableWidget.insertRow(0)
            self.tableWidget.setItem(
                0, 0, QTableWidgetItem(str(undergrowth["structure"]))
            )
            self.tableWidget.setItem(0, 1, QTableWidgetItem(str(undergrowth["age"])))
            self.tableWidget.setItem(0, 2, QTableWidgetItem(str(undergrowth["height"])))
            self.tableWidget.setItem(0, 3, QTableWidgetItem(str(undergrowth["amount"])))
            self.tableWidget.setItem(
                0, 4, QTableWidgetItem(str(undergrowth["undergrowth_grade"]))
            )

        for underwood in tax_data["underwood_data"]:
            self.tableWidget_5.insertRow(0)
            self.tableWidget_5.setItem(
                0, 0, QTableWidgetItem(str(underwood["density_degree"]))
            )
            self.tableWidget_5.setItem(0, 1, QTableWidgetItem(str(underwood["species_list"])))

        # for additional_info in tax_data["additional_info"]:
        #     self.tableWidget_2.insertColumn(0)
        #     self.tableWidget_2.insertColumn(1)
        #     self.tableWidget_2.insertColumn(2)
        #     self.tableWidget_2.insertColumn(3)
        #     self.tableWidget_2.setItem(
        #         0, 0, QTableWidgetItem(str(additional_info["creation_year"]))
        #     )
        #     if additional_info["row_spacing"]:
        #         row_spacing = str(additional_info["row_spacing"])
        #         spacing_in_row = str(additional_info["spacing_in_row"])
        #         amount = str(additional_info["amount"])
        #         full_spacing_row = f"{row_spacing} x {spacing_in_row}, {amount}"
        #         self.tableWidget_2.setItem(
        #             0, 1, QTableWidgetItem(full_spacing_row)
        #         )
        #     self.tableWidget_2.setItem(
        #         0, 2, QTableWidgetItem(str(additional_info["cultures_condition"]))
        #     )
        #     if additional_info["start_year"]:
        #         start_year = str(additional_info["start_year"])
        #         full_years_row = f"Год начала: {start_year}; "
        #         self.tableWidget_2.setItem(
        #             1, 1, QTableWidgetItem(full_years_row)
        #         )
        #     if additional_info["actual_end_year"]:
        #         actual_end_year = str(additional_info["actual_end_year"])
        #         full_years_row = f"Год окончания: {actual_end_year}"
        #         self.tableWidget_2.setItem(
        #             1, 1, QTableWidgetItem(full_years_row)
                # )
            # self.tableWidget_2.setItem(1, 2, QTableWidgetItem(str(tapping["row_spacing"])))
        
        
        for forest_culture in tax_data["forest_cultures"]:
            self.tableWidget_7.insertRow(0)
            self.tableWidget_7.setItem(
                0, 0, QTableWidgetItem(str(forest_culture["creation_year"]))
            )
            if forest_culture["row_spacing"]:
                row_spacing = str(forest_culture["row_spacing"])
                spacing_in_row = str(forest_culture["spacing_in_row"])
                full_spacing_row = f"{row_spacing} x {spacing_in_row}"
                self.tableWidget_7.setItem(
                    0, 1, QTableWidgetItem(full_spacing_row)
                )
            self.tableWidget_7.setItem(
                0, 2, QTableWidgetItem(str(forest_culture["amount"]))
            )
            self.tableWidget_7.setItem(
                0, 3, QTableWidgetItem(str(forest_culture["forest_cultures_condition"]))
            )

        
        
        for tapping in tax_data["tapping"]:
            
            self.tableWidget_2.insertRow(0)
            self.tableWidget_2.setItem(
                0, 0, QTableWidgetItem(str(tapping["start_year"]))
            )
            self.tableWidget_2.setItem(0, 1, QTableWidgetItem(str(tapping["actual_end_year"])))
            self.tableWidget_2.setItem(0, 2, QTableWidgetItem(str(tapping["tapping_condition"])))
            
            
        for red_book_spices in tax_data["red_book_plants_animals"]:
            # species_list = []
            for species in red_book_spices:
                if red_book_spices[species]:
                    self.tableWidget_8.insertRow(0)
                    self.tableWidget_8.setItem(0, 0, QTableWidgetItem(str(red_book_spices[species])))

        
        for feature_dict in tax_data["selection_features"]:
            # species_list = []
            for feature in feature_dict:
                if feature_dict[feature]:
                    self.tableWidget_9.insertRow(0)
                    self.tableWidget_9.setItem(0, 0, QTableWidgetItem(str(feature_dict[feature])))


        for event in tax_data["completed_economic_events"]:
            self.tableWidget_6.insertRow(0)
            self.tableWidget_6.setItem(0, 0, QTableWidgetItem(str(event["event"])))
            self.tableWidget_6.setItem(0, 1, QTableWidgetItem(str(event["year"])))


        del tax_data["m10"]
        del tax_data["undergrowth_data"]
        del tax_data["underwood_data"]
        del tax_data["additional_data"]
        del tax_data["forest_cultures"]
        del tax_data["tapping"]
        del tax_data["red_book_plants_animals"]
        del tax_data["selection_features"]
        del tax_data["completed_economic_events"]

        for row in range(len(tax_data.keys())):
            self.tableWidget_3.insertRow(row)
            self.tableWidget_3.setItem(
                row, 0, QTableWidgetItem(list(tax_data.keys())[row])
            )
            self.tableWidget_3.setItem(
                row, 1, QTableWidgetItem(str(list(tax_data.values())[row]))
            )
            self.tableWidget_3.item(row, 1).setToolTip(
                str(list(tax_data.values())[row])
            )
