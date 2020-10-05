from PyQt5 import QtCore
import json
from ..models.nri import Species


class Data(QtCore.QThread):
    signal_new_uuid = QtCore.pyqtSignal(str)
    signal_output_record = QtCore.pyqtSignal(dict)
    siganl_calculate_amount = QtCore.pyqtSignal(bool)
    siganl_error = QtCore.pyqtSignal(bool)

    def __init__(self, **args):
        QtCore.QThread.__init__(self)
        self.import_file = args['import_file']

    def run(self):
        try:
            with open(self.import_file, "r") as read_file:
                import_data = json.load(read_file)
            self.signal_new_uuid.emit(import_data['uuid_area'])
            for spc in import_data['business']:
                name_species_latin = Species.select().where(Species.name_species == spc).get().name_species_latin
                for record in import_data['business'][spc]:
                    self.signal_output_record.emit({'species': name_species_latin,
                                                    'dmr': int(record['dmr']),
                                                    'num_ind': int(record['num_ind']),
                                                    'num_fuel': int(record['num_fuel']),
                                                    'num_half_ind': int(record['num_half_ind']),
                                                    'device_sign': 'json'})

            self.siganl_calculate_amount.emit(1)  # отправляю сигнал на подсчёт суммы
        except:
            self.siganl_error.emit(1)
