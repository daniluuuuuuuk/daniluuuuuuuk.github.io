import decimal

class CoordinateFormatConverter:
    """Используется для конвертации данных
    в другой формат координат - из десятичных в градусы-минуты-секунды
    и наоборот
    """
    def __init__(self, tableList, tableType, coordType):
        super().__init__()
        self.tableList = tableList
        self.tableType = tableType
        self.coordType = coordType

    def convertToDMS(self):
        tableListConverted = []
        for row in self.tableList:
            convertedRow = self.convertRowToDMS(row)
            tableListConverted.append(convertedRow)
        return tableListConverted

    def convertToDD(self):
        tableListConverted = []        
        for row in self.tableList:
            convertedRow = self.convertRowToDD(row)
            tableListConverted.append(convertedRow)
        return tableListConverted

    def convertRowToDMS(self, row):
        if self.tableType == 0:
            convertedRow = self.convertDDcoord(row)
        elif self.tableType == 1:
            convertedRow = self.convertDDAzimuth(row)
        elif self.tableType == 2:
            convertedRow = self.convertDDRumb(row)
        elif self.tableType == 3 or self.tableType == 4:
            convertedRow = self.convertDDAzimuth(row)
        return convertedRow

    def convertRowToDD(self, row):
        if self.tableType == 0:
            convertedRow = self.convertDMSCoord(row)
        elif self.tableType == 1:
            convertedRow = self.convertDMSAzimuth(row)
        elif self.tableType == 2:
            convertedRow = self.convertDMSRumb(row)
        elif self.tableType == 3 or self.tableType == 4:
            convertedRow = self.convertDMSAzimuth(row)
        return convertedRow

    def decdeg2dms(self, dd, roundUp):
        mnt, sec = divmod(float(dd) * 3600, 60)
        deg, mnt = divmod(float(mnt), 60)
        if roundUp:
            d = decimal.Decimal(deg).quantize(decimal.Decimal('.1'))
            m = decimal.Decimal(mnt).quantize(decimal.Decimal('.1'))
            s = decimal.Decimal(sec).quantize(decimal.Decimal('.1'))
            return d, m, s
        else:
            return deg, mnt, sec

    def dms2dd(self, degrees, minutes, seconds, roundUp):
        dd = float(degrees) + float(minutes)/60 + float(seconds)/(60*60)
        if roundUp:
            return decimal.Decimal(dd).quantize(decimal.Decimal('.1'))
        else:
            return dd

    def convertDDcoord(self, row):
        x = row[1]
        y = row[2]
        convertedX = self.decdeg2dms(x, False)
        convertedY = self.decdeg2dms(y, False)
        convertedRow = [row[0], str(convertedX[0]), str(convertedX[1]), str(convertedX[2]),
                        str(convertedY[0]), str(convertedY[1]), str(convertedY[2]), row[3]]
        return convertedRow

    def convertDMSCoord(self, row):
        x = self.dms2dd(row[1], row[2], row[3], False)
        y = self.dms2dd(row[4], row[5], row[6], False)
        convertedRow = [row[0], str(x), str(y), row[7]]
        return convertedRow

    def convertDDAzimuth(self, row):
        az = self.decdeg2dms(row[1], True)
        convertedRow = [row[0], str(az[0]), str(az[1]), str(az[2]), row[2], row[3]]
        return convertedRow

    def convertDMSAzimuth(self, row):
        az = self.dms2dd(row[1], row[2], row[3], True)
        convertedRow = [row[0], str(az), row[4], row[5]]
        return convertedRow

    def convertDDRumb(self, row):
        rmb = self.decdeg2dms(row[1], True)
        convertedRow = [row[0], str(rmb[0]), str(rmb[1]), str(rmb[2]), row[2], row[3], row[4]]
        return convertedRow

    def convertDMSRumb(self, row):
        rmb = self.dms2dd(row[1], row[2], row[3], True)
        convertedRow = [row[0], str(rmb), row[4], row[5], row[6]]
        return convertedRow