from qgis.PyQt.QtWidgets import (
    QScrollArea,
    QVBoxLayout,
    QWidget,
    QCheckBox,
    QSpacerItem,
    QSizePolicy,
    QLabel,
)
from qgis.PyQt.QtCore import Qt
from ..PostgisDB import PostGisDB
from .LayoutObjectsIterator import LayoutObjectsIterator


class CuttingAreaScrollList(QScrollArea):
    def __init__(self, selected_cutting_areas=[], forestry_number=0, quarter_number=0, stratum_number=0, cutting_area_number=0, parent=None):
        super().__init__(parent)

        self.setWidgetResizable(True)

        self.scrollAreaWidgetContents = QWidget()

        self.cutting_areas_container = QVBoxLayout(
            self.scrollAreaWidgetContents
        )
        self.setWidget(self.scrollAreaWidgetContents)

        self.selected_cutting_areas = selected_cutting_areas

        self.forestry_number = forestry_number
        self.quarter_number = quarter_number
        self.stratum_number = stratum_number
        self.cutting_area_number = cutting_area_number

        self.fill_list()

    def get_current_cutting_areas(self) -> list:
        """
        Получение текущих лесосек
        """
        area_table = PostGisDB().getQueryResult(
            self.form_result_query(self.forestry_number, self.quarter_number, self.stratum_number, self.cutting_area_number),
            as_dict=True,
        )
        return area_table

    @staticmethod
    def form_result_query(forestry_number, quarter_number, stratum_number, cutting_area_number):
        if not forestry_number or forestry_number == '0':
            query = """select lesnich_text as "Лесничество", num_kv as "Квартал", num_vds as "Выдел", num as "Номер лесосеки", usetype as "Вид пользования", cuttingtyp as "Вид рубки", uid as "UUID" from area;"""
        elif forestry_number and not quarter_number:

            query = """select 
                            lesnich_text as "Лесничество",
                            num_kv as "Квартал",
                            num_vds as "Выдел",
                            num as "Номер лесосеки", 
                            usetype as "Вид пользования", 
                            cuttingtyp as "Вид рубки", 
                            uid as "UUID" 
                        from area
                        where num_lch = '{}';""".format(forestry_number)
        elif forestry_number and not stratum_number:
            query = """select 
                            lesnich_text as "Лесничество",
                            num_kv as "Квартал",
                            num_vds as "Выдел",
                            num as "Номер лесосеки", 
                            usetype as "Вид пользования", 
                            cuttingtyp as "Вид рубки", 
                            uid as "UUID" 
                        from area
                        where num_lch = '{}' and num_kv = '{}';""".format(forestry_number, quarter_number)
        elif forestry_number and not cutting_area_number:
            query = """select 
                            lesnich_text as "Лесничество",
                            num_kv as "Квартал",
                            num_vds as "Выдел",
                            num as "Номер лесосеки", 
                            usetype as "Вид пользования", 
                            cuttingtyp as "Вид рубки",
                            uid as "UUID" 
                        from area
                        where num_lch = '{}' and num_kv = '{}' and num_vds = '{}';""".format(forestry_number, quarter_number, stratum_number)
        else:
            query = """select 
                            lesnich_text as "Лесничество",
                            num_kv as "Квартал",
                            num_vds as "Выдел",
                            num as "Номер лесосеки", 
                            usetype as "Вид пользования", 
                            cuttingtyp as "Вид рубки",
                            uid as "UUID" 
                        from area
                        where num_lch = '{}' and num_kv = '{}' and num_vds = '{}' and num = '{}';""".format(forestry_number, quarter_number, stratum_number, cutting_area_number)
        return query

    def set_checked_selected_cutting_areas(self):
        for cutting_area_cb in LayoutObjectsIterator(
            layout=self.cutting_areas_container
        ):
            cutting_area_cb.setChecked(False)

            if getattr(cutting_area_cb, "uuid") in self.selected_cutting_areas:
                cutting_area_cb.setChecked(True)

    def fill_list(self):
        """
        Добавление текущих лесосек в GUI
        """

        for cutting_area in self.get_current_cutting_areas():
            if cutting_area != {}:
                cb = QCheckBox(
                    "; ".join(
                        [
                            "%s: %s" % (key, value)
                            for (key, value) in cutting_area.items()
                        ]
                    )
                )

                cb.setChecked(1)
                setattr(cb, "uuid", cutting_area.get("UUID", False))
                self.cutting_areas_container.addWidget(cb)
            else:
                pass

        self.cutting_areas_container.addStretch(1)
        if self.selected_cutting_areas != []:
            self.set_checked_selected_cutting_areas()

    @property
    def selected_areas_uuid(self) -> list:
        """
        Если нажат чекбокс лесосеки, то UUID
        добавляется в список и возвращается

        Returns:
            list: [Список UUID выбранных лесосек]
        """
        cutting_area_uuid = []

        for cutting_area_cb in LayoutObjectsIterator(
            layout=self.cutting_areas_container
        ):
            if cutting_area_cb.checkState():
                cutting_area_uuid.append(getattr(cutting_area_cb, "uuid"))
        return cutting_area_uuid
