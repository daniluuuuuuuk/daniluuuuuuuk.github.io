from PyQt5 import QtCore
import json


class Data(QtCore.QThread):
    signal_status = QtCore.pyqtSignal(dict)

    def __init__(self, **args):
        QtCore.QThread.__init__(self)
        self.uuid = args['uuid']
        self.table = args['table']
        self.export_file = args['export_file']

    def run(self):
        try:
            output_data = {'uuid_area': self.uuid, 'restatement': {}}
            for column in range(1, self.table.columnCount()):
                if column % 3 == 1:
                    species = self.table.item(0, column).text()
                    output_data['restatement'].update({species: []})
                    for row in range(2, self.table.rowCount()-1):
                        dmr = self.table.item(row, 0).text()
                        """Если ячейка пустая - пишу ноль"""
                        if self.table.item(row, column):
                            num_ind = int(self.table.item(row, column).text())
                        else:
                            num_ind = 0
                        if self.table.item(row, column+1):
                            num_fuel = int(self.table.item(row, column+1).text())
                        else:
                            num_fuel = 0

                        if self.table.item(row, column+2):
                            num_biodiversity = int(self.table.item(row, column+2).text())
                        else:
                            num_biodiversity = 0
                        if num_ind != 0 or num_fuel != 0 or num_biodiversity != 0:
                            output_data['restatement'][species].append({'dmr': dmr,
                                                                        'num_ind': num_ind,
                                                                        'num_fuel': num_fuel,
                                                                        'num_biodiversity': num_biodiversity})

            with open(self.export_file, 'w') as file:
                json.dump(output_data, file, indent=1, ensure_ascii=False)
            self.signal_status.emit({'head': 'Успешно', 'body': 'Данные успешно экспортированы в\n'+self.export_file})
        except:
            self.signal_status.emit({'head': 'Ошибка', 'body': 'Ошибка экспорта.'})

