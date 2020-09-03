import time
from PyQt5 import QtCore
from ....src.models.nri import Species, Organization
from ....src.models.public import Area
from ....src.models.restatement import Trees


class Data(QtCore.QThread):
    signal_output_data = QtCore.pyqtSignal(dict)
    siganl_calculate_amount = QtCore.pyqtSignal(bool)

    def __init__(self, **args):
        QtCore.QThread.__init__(self)
        self.uuid = args['uuid']

    # def get_att_area_data(self):
    #     """Получаю аттрибутивные данные для пробной площади"""
    #     area = Area.select(Area.uuid,
    #                        Area.num_enterprise,
    #                        Area.num_forestry,
    #                        Area.num_compartment,
    #                        Area.num_sub_compartment
    #                        ).where(Area.uuid == self.uuid).get()
    #     origin_data = {
    #         "uuid": area.uuid,
    #         "num_enterprise": area.num_enterprise,
    #         "num_forestry": area.num_forestry,
    #         "num_compartment": area.num_compartment,
    #         "num_sub_compartment": area.num_sub_compartment
    #     }
    #     self.att_processing(origin_data)
    #
    # def att_processing(self, origin_data: dict):
    #     """Перевожу коды лесхоза и лесничества в текстовый вид"""
    #     orgs = Organization.select(Organization.id_organization,
    #                                Organization.code_organization,
    #                                Organization.name_organization)
    #     for record in orgs:
    #         print(str(record.code_organization))
    #         print(str(record.code_organization)[3:6])
    #         print(str(origin_data['num_enterprise']))
    #         if str(record.code_organization)[3:6] == str(origin_data['num_enterprise']):
    #             print(record.name_organization)
    #             break
    #     print(origin_data)

    def run(self):
        for record in Trees.select().where(Trees.offset_uuid == self.uuid):
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

