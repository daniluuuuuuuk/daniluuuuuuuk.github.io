from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import QThread, pyqtSignal
from .trees_liquid import TreesLiquid
from ..models.public import Area, Trees


class ImportedData(QThread):
    signal_get_trees_data = pyqtSignal(QStandardItemModel)
    signal_get_att_data = pyqtSignal(dict)

    def __init__(self, uuid: str = None):
        QThread.__init__(self)
        self.uuid = uuid
        self.trees_liquid = TreesLiquid()

    def get_att_data(self) -> dict:
        """Получение атрибутивных данных о лесосеке"""
        current_area_att = Area.select().where(Area.uuid == self.uuid).dicts().get()

        del current_area_att["geom"]

        current_area_att["area"] = str(float(current_area_att["area"]))

        self.signal_get_att_data.emit(current_area_att)

    def get_trees_data(self) -> list:
        """Получение колличества деревьев"""
        trees = Trees.select().where(Trees.area_uuid == self.uuid).dicts()

        for row in trees:
            del row["area_uuid"]
            self.trees_liquid.add_record(row)

        self.signal_get_trees_data.emit(self.trees_liquid)
        return None

    def run(self):
        self.get_att_data()
        self.get_trees_data()
