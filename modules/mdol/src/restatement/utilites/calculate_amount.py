from PyQt5 import QtCore


class Amount(QtCore.QThread):
    signal_output_data = QtCore.pyqtSignal(dict)

    def __init__(self, table):
        QtCore.QThread.__init__(self)
        self.table = table

    def run(self):
        output_data = {}
        for column in range(1, self.table.columnCount()):
            output_data[column] = 0
            for row in range(2, self.table.rowCount()-1):
                if self.table.item(row, column):
                    output_data[column] = output_data[column]+int(self.table.item(row, column).text())
        self.signal_output_data.emit(output_data)
