from PyQt5 import QtWidgets,QtCore, uic

from modules.trial_area.src.config import Settings, BasicDir

from modules.trial_area.src.models.nri import Species


class Select_species(QtWidgets.QDialog, uic.loadUiType(BasicDir().get_basic_dir("gui/select_species.ui"))[0]):
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.setupUi(self)
        styles = open(BasicDir().get_basic_dir("gui/stylesheets/base.qss"), 'r')
        self.styleData = styles.read()
        styles.close()
        self.setStyleSheet(self.styleData)
        """Читаю сохраненные в прошлый раз породы и отображаю их"""
        self.selected_species = Settings(group='Selected_species', key='species').read_setting()

        """Список логических дисков (для записи пород в вилку)"""
        self.comboBox.addItems(['C', 'D', 'E', 'F'])

        """Получаю и отображаю список пород из БД"""
        name_species = []
        for i in Species.select():
            name_species.append(i.name_species)
        name_species.sort()

        self.pushButton_2.clicked.connect(self.data_to_caliper)
        self.pushButton.clicked.connect(self.save_species)
        self.pushButton_4.clicked.connect(lambda: True if len(self.listView.selectedIndexes()) > 0 ==
                                          self.add_to_right_list(self.listView.selectedIndexes()[0].data()) else None)
        self.pushButton_5.clicked.connect(lambda: True if len(self.listView_2.selectedIndexes()) > 0 ==
                                          self.delete_from_right_list(self.listView_2.selectedIndexes()[0].data()) else None)

        self.listView.setModel(QtCore.QStringListModel(name_species))  # Заношу данные в левый список
        self.listView.setEditTriggers(QtWidgets.QListView.NoEditTriggers)  # Отключаю изменения пород
        self.listView_2.setModel(QtCore.QStringListModel(self.selected_species))
        self.listView_2.setEditTriggers(QtWidgets.QListView.NoEditTriggers)  # Отключаю изменения пород

        self.listView.doubleClicked.connect(lambda: self.add_to_right_list(self.listView.selectedIndexes()[0].data()))

    def add_to_right_list(self, item):
        self.selected_species.append(Species.select().where(Species.name_species == item).get().name_species_latin)
        self.listView_2.setModel(QtCore.QStringListModel(self.selected_species))

    def delete_from_right_list(self, item):
        self.selected_species.remove(item)
        self.listView_2.setModel(QtCore.QStringListModel(self.selected_species))

    def data_to_caliper(self):
        selected_logical_disk = self.comboBox.currentText()
        try:
            f = open(f'{selected_logical_disk}:\DATA\MDII\SPCNAME.TXT', 'w')
            for index in self.selected_species:
                f.write(index + '\n')

            QtWidgets.QMessageBox.information(None, 'Успешно', 'Породы успешно загружены в вилку.')

        except:
            QtWidgets.QMessageBox.critical(None, 'Ошибка', 'Ошибка записи, данные не записаны в устройство.')

    def save_species(self):
        self.selected_species = Settings(group='Selected_species', key='species').add_setting(self.selected_species)
        self.close()

