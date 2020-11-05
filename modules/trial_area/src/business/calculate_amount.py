from PyQt5 import QtCore


class Amount(QtCore.QThread):
    signal_output_data = QtCore.pyqtSignal(dict)

    def __init__(self, table):
        QtCore.QThread.__init__(self)
        self.table = table

    def amount(self):
        """
        Рассчёт конечной суммы, а так же запуск подсчёта дополнительных сумм.
        """
        total = self.total_by_species_dmr()
        total_by_species_dmr = total[0]
        total_by_dmr = total[1]

        output_data = {}
        #  Учитываю данные для подсчёта с метода total_by_species
        for column in range(1, self.table.columnCount()):
            if column % 4 == 1:
                for _ in total_by_species_dmr:
                    if _["column"] == column:
                        try:
                            output_data[column] += _["total"]
                        except KeyError:
                            output_data[column] = _["total"]

            else:
                output_data[column] = 0
                for row in range(2, self.table.rowCount() - 1):
                    if self.table.item(row, column):
                        output_data[column] = output_data[column] + int(
                            self.table.item(row, column).text()
                        )
        return {
            "amount": output_data,
            "total_by_species_dmr": total_by_species_dmr,
            "total_by_dmr": total_by_dmr,
        }

    def total_by_species_dmr(self):
        """
        Рассчитывается сумма деловых+дровяных для каждого диаметра и для каждой породы
        """
        output_data = []
        output_data_by_dmr = {}
        for row in range(2, self.table.rowCount() - 1):
            for column in range(1, self.table.columnCount()):
                if column % 4 == 2:  # (Столбец деловой)
                    try:
                        ind = int(self.table.item(row, column).text())
                    except AttributeError:
                        ind = 0
                    try:
                        fuel = int(self.table.item(row, column + 1).text())
                    except AttributeError:
                        fuel = 0
                    liquid = ind + fuel
                    output_data.append(
                        {"row": row, "column": column - 1, "total": liquid}
                    )
                    if liquid > 0:
                        try:
                            output_data_by_dmr[row] += liquid
                        except KeyError:
                            output_data_by_dmr[row] = liquid

        return output_data, output_data_by_dmr

    def total_by_dmr(self):
        """
        Рассчитывается сумма ДЕЛ + ДРОВ по всем породам для каждого диаметра
        """
        None

    def run(self):
        self.signal_output_data.emit(self.amount())
