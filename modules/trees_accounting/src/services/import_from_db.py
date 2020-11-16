import time
from PyQt5 import QtCore
from ..models.nri import Species, Organization
from ..models.restatement import Trees
from ..models.public import Area


class Data(QtCore.QThread):
    signal_output_data = QtCore.pyqtSignal(dict)
    signal_att_data = QtCore.pyqtSignal(dict)
    signal_calculate_amount = QtCore.pyqtSignal(bool)

    def __init__(self, **args):
        QtCore.QThread.__init__(self)
        self.uuid = args["uuid"]

    def get_att_area_data(self):
        """Получаю атрибутивные данные для пробной площади"""
        area = Area.select().where(Area.uuid == self.uuid).get()
        gplho, forestry_enterprise, forestry = Organization().convert_org_id(
            id_forestry=area.num_forestry, id_forestry_enterprise=area.num_enterprise
        )

        att_data = {
            "area_uuid": area.uuid,
            "gplho": gplho,
            "enterprise": forestry_enterprise,
            "forestry": forestry,
            "compartment": str(area.compartment),
            "sub_compartment": str(area.sub_compartment),
            "area_square": str(area.area),
            "num_cutting_area": area.num_cutting_area,
        }
        return att_data

    def run(self):
        self.signal_att_data.emit(self.get_att_area_data())
        for record in Trees.select().where(Trees.area_uuid == self.uuid):
            species = (
                Species.select()
                .where(Species.code_species == record.code_species)
                .get()
                .name_species_latin
            )
            output_data = {
                "species": species,
                "dmr": record.dmr,
                "num_ind": record.num_ind,
                "num_fuel": record.num_fuel,
                "num_half_ind": record.num_half_ind,
                "device_sign": "db",
            }
            self.signal_output_data.emit(output_data)
            time.sleep(0.001)
        self.signal_calculate_amount.emit(1)  # отправляю сигнал на подсчёт суммы
