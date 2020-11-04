import winsound

from PyQt5 import QtCore


class Caliper(QtCore.QThread):
    signal_output_data = QtCore.pyqtSignal(dict)

    def __init__(self, **args):
        QtCore.QThread.__init__(self)
        self.connection = args["connection"]

    def run(self):

        a = []
        while True:
            b = self.connection.readline().decode("utf-8").split(",")
            a.append(b)
            if len(a) % 2 == 0:
                a = a[0] + a[1]
                b = []
                for i in a:
                    i = i.replace("\r\n", "")
                    b.append(i)
                c = [b[3], b[8]]
                a = []
                c[1] = self.roundingData(
                    int(c[1])
                )  # Привожу точный диаметр к категории диаметров
                data = {
                    "species": b[3],  # Порода на латинице (то что приходит с вилки)
                    "dmr": c[1],  # Категория диаметров
                    "num_ind": 1,  # Техническая годность приходит по дефолту Деловая
                    "num_fuel": 0,
                    "num_half_ind": 0,
                    "device_sign": "caliper",
                }
                self.signal_output_data.emit(
                    data
                )  # Отправляю эти данные в основной поток для заполнения таблицы
                winsound.MessageBeep()  # Издаю звук о добавлении ствола

    def roundingData(self, i):
        """Привожу диаметры стволов"""
        i = float(i) / 10
        if 0 < i <= 12.9:
            # b = 1
            b = 4
        elif 13.0 <= i <= 31.9:
            # b = 2
            b = 4
        elif 32.0 <= i:
            b = 4
        else:
            b = 1
        i = round(i / b + 10 ** (-9)) * b

        if i <= 6:  # Меньше 6см деревья не учитываем
            return 0

        return i
