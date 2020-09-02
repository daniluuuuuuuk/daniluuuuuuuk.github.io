import time
from PyQt5 import QtCore
from ....src.models.nri import Species
from ....src.models.ta_fund import *


class Data(QtCore.QThread):
    signal_output_data = QtCore.pyqtSignal(dict)
    siganl_calculate_amount = QtCore.pyqtSignal(bool)

    def __init__(self, **args):
        QtCore.QThread.__init__(self)
        self.uuid = args['uuid']

    def run(self):
        for record in Ta_fund_enum.select().where(Ta_fund_enum.offset_uuid == self.uuid):
            species = Species.select().where(Species.code_species == record.code_species).get().name_species_latin
            output_data = {
                'species': species,
                'dmr': record.dmr,
                'num_ind': record.num_ind,
                'num_fuel': record.num_fuel,
                'num_biodiversity': record.num_biodiversity,
                'device_sign': 'db'
            }
            self.signal_output_data.emit(output_data)
            time.sleep(.001)
        self.siganl_calculate_amount.emit(1)  # отправляю сигнал на подсчёт суммы

