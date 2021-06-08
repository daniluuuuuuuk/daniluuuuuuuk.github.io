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
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWidgetResizable(True)

        self.scrollAreaWidgetContents = QWidget()

        self.cutting_areas_container = QVBoxLayout(
            self.scrollAreaWidgetContents
        )
        self.setWidget(self.scrollAreaWidgetContents)

        self.fill_list()

    def get_current_cutting_areas(self) -> list:
        """
        Получение текущих лесосек
        """
        area_table = PostGisDB().getQueryResult(
            """select lesnich_text as "Лесничество", num_kv as "Квартал", num_vds as "Выдел", usetype as "Вид пользования", cuttingtyp as "Вид рубки", uid as "UUID" from area;""",
            as_dict=True,
        )
        return area_table

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
                self.cutting_areas_container.addWidget(
                    QLabel("Лесосеки отсутствуют")
                )

        self.cutting_areas_container.addStretch(1)

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
