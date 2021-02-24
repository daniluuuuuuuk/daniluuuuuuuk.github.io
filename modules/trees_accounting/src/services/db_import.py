from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtCore import QThread, pyqtSignal
from ..models.trees_liquid import TreesLiquid
from ..models.trees_not_cutting import TreesNotCutting
from ..models.public import Area, Trees, TreesTrfHeight, TreesNotCuttingModel
from ..models.dictionary import Species, KindSeeds


class ImportedData(QThread):
    signal_get_trees_data = pyqtSignal(QStandardItemModel)
    signal_get_not_cutting_trees_data = pyqtSignal(QStandardItemModel)
    signal_get_att_data = pyqtSignal(dict)

    def __init__(self, uuid: str = None):
        QThread.__init__(self)
        self.uuid = uuid
        self.trees_liquid = TreesLiquid()
        self.trees_not_cutting = TreesNotCutting()

    def get_att_data(self) -> dict:
        """Получение атрибутивных данных о лесосеке"""
        current_area_att = Area.select().where(Area.uuid == self.uuid).dicts().get()

        del current_area_att["geom"]

        current_area_att["area"] = str(float(current_area_att["area"]))

        self.signal_get_att_data.emit(current_area_att)

    def get_trees_data(self) -> None:
        """Получение колличества деревьев"""
        trees = Trees.select().where(Trees.area_uuid == self.uuid).dicts()

        for row in trees:
            del row["area_uuid"]
            self.trees_liquid.add_record(row)

        self.get_trees_trf_data()

        self.signal_get_trees_data.emit(self.trees_liquid)
        return None

    def get_not_cutting_trees_data(self) -> None:
        trees = (
            TreesNotCuttingModel.select()
            .where(TreesNotCuttingModel.area_uuid == self.uuid)
            .dicts()
        )

        for row in trees:
            del row["area_uuid"]
            row["name_species"] = (
                Species.select(Species.name_species)
                .where(Species.code_species == row["code_species"])
                .get()
                .name_species
            )
            row["name_kind_seeds"] = (
                KindSeeds.select(KindSeeds.name_kind_seeds)
                .where(KindSeeds.code_kind_seeds == row["seed_type_code"])
                .get()
                .name_kind_seeds
            )
            row["seed_dmr"] = str(row["seed_dmr"])
            row["seed_count"] = str(row["seed_count"])
            self.trees_not_cutting.add_record(row)
        self.signal_get_not_cutting_trees_data.emit(self.trees_not_cutting)

    def get_trees_trf_data(self) -> None:
        """
        Добавляю в модель данные из БД о разрядах высот
        """
        species_position = self.trees_liquid.species_position()
        for spc in species_position.keys():
            current_trf_height = int(
                str(
                    TreesTrfHeight.select()
                    .where(
                        TreesTrfHeight.area_uuid == self.uuid,
                        TreesTrfHeight.code_species == spc,
                    )
                    .get()
                    .code_trf_height
                )
            )
            self.trees_liquid.set_trf_for_spc(species_position[spc], current_trf_height)

        return None

    def run(self):
        self.get_att_data()
        self.get_trees_data()
        self.get_not_cutting_trees_data()
