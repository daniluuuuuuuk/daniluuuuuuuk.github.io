import time
from PyQt5 import QtCore
from modules.trial_area.src.models.nri import Species, Organization
from modules.trial_area.src.models.restatement import Trees, Areas


class Data(QtCore.QThread):
    signal_output_data = QtCore.pyqtSignal(dict)
    signal_att_data = QtCore.pyqtSignal(dict)
    siganl_calculate_amount = QtCore.pyqtSignal(bool)

    def __init__(self, **args):
        QtCore.QThread.__init__(self)
        self.uuid = args['uuid']

    def get_att_area_data(self):
        """Получаю аттрибутивные данные для пробной площади"""
        area = Areas.select(Areas, Organization).join(Organization, on=(Areas.forestry == Organization.id_organization)).where(Areas.area_uuid==self.uuid).get()

        att_data = {
            "area_uuid": area.area_uuid,
            "gplho": area.gplho.name_organization,
            "enterprise": area.enterprise.name_organization,
            "forestry": area.forestry.name_organization,
            "compartment": str(area.compartment),
            "sub_compartment": str(area.sub_compartment),
            "area_square": str(area.area_square)

        }
        return att_data

    def run(self):
        self.signal_att_data.emit(self.get_att_area_data())
        for record in Trees.select().where(Trees.area_uuid == self.uuid):
            species = Species.select().where(Species.code_species == record.code_species).get().name_species_latin
            output_data = {
                'species': species,
                'dmr': record.dmr,
                'num_ind': record.num_ind,
                'num_fuel': record.num_fuel,
                'num_half_ind': record.num_half_ind,
                'device_sign': 'db'
            }
            self.signal_output_data.emit(output_data)
            time.sleep(.001)
        self.siganl_calculate_amount.emit(1)  # отправляю сигнал на подсчёт суммы

