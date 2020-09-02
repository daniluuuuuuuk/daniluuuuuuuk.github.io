from PyQt5 import QtCore
from ....src.models.ta_fund import *
from ....src.models.nri import *


class DBData(QtCore.QThread):
    signal_status = QtCore.pyqtSignal(dict)

    def __init__(self, table, uuid):
        QtCore.QThread.__init__(self)
        self.table = table
        self.uuid = uuid

    def run(self):
        if self.table.columnCount() == 1:
            self.signal_status.emit({'head': 'Ошибка', 'body': 'Отсутсвуют данные сохранения.'})
            return None
        for column in range(1, self.table.columnCount()):
            if column % 3 == 1:
                output_data = {'species': Species.select().where(
                    Species.name_species == self.table.item(0, column).text()).get().code_species}

                for row in range(2, self.table.rowCount()-1):  # Сумму не трогаю (self.table.rowCount()-1)
                    """Собираю данные с ячеек (если ячейки пусты - ставлю 0"""
                    if self.table.item(row, column):
                        output_data['num_ind'] = int(self.table.item(row, column).text())
                    else:
                        output_data['num_ind'] = 0
                    if self.table.item(row, column+1):
                        output_data['num_fuel'] = int(self.table.item(row, column+1).text())
                    else:
                        output_data['num_fuel'] = 0
                    if self.table.item(row, column+2):
                        output_data['num_biodiversity'] = int(self.table.item(row, column+2).text())
                    else:
                        output_data['num_biodiversity'] = 0
                    if output_data['num_ind'] == 0 and output_data['num_fuel'] == 0 and output_data['num_biodiversity'] == 0:
                        None
                    else:
                        output_data['dmr'] = int(row*4)
                        try:
                            Ta_fund_enum.create(offset_uuid=self.uuid,
                                                code_species=output_data['species'],
                                                dmr=output_data['dmr'],
                                                num_ind=output_data['num_ind'],
                                                num_fuel=output_data['num_fuel'],
                                                num_biodiversity=output_data['num_biodiversity'])
                        except:
                            self.signal_status.emit({'head': 'Ошибка',
                                                     'body': 'Ошибка записи в БД.\nДанные не сохранены'})
                            return None

        self.signal_status.emit({'head': 'Успешно', 'body': 'Данные успешно сохранены.'})
