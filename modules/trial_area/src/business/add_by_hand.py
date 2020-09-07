from PyQt5 import QtWidgets, QtCore, uic
from modules.trial_area.src.config import Settings, BasicDir


class AddByHand(QtWidgets.QDialog, uic.loadUiType(BasicDir().get_basic_dir("gui/add_by_hand.ui"))[0]):
    def __init__(self, last_data, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.setupUi(self)
        styles = open(BasicDir().get_basic_dir("gui/stylesheets/base.qss"))
        self.styleData = styles.read()
        styles.close()
        self.setStyleSheet(self.styleData)

        self.last_data = last_data
        self.pushButton.clicked.connect(self.save)
        self.dmrs = Settings(group='Diameters', key='dmrs').read_setting()
        self.name_species = Settings(group='Selected_species', key='species').read_setting()
        self.rb_dmrs = []
        self.rb_spc = []
        self.output_data = {'num_ind': 1, 'num_fuel': 0, 'num_half_ind': 0, 'device_sign': 'hand'}

        """Диаметры"""
        for i_dmr in range(len(self.dmrs)):
            rb_dmr = QtWidgets.QRadioButton(self.groupBox_2)
            rb_dmr.setText(str(self.dmrs[i_dmr]))
            try:  # выбираю radiobutton по прошлому значению
                if str(self.dmrs[i_dmr]) == str(self.last_data['dmr']):
                    rb_dmr.setChecked(True)
            except KeyError:
                None
            self.rb_dmrs.append(rb_dmr)
            if i_dmr % 3 == 0:
                self.verticalLayout_4.addWidget(rb_dmr)
            if i_dmr % 3 == 1:
                self.verticalLayout_12.addWidget(rb_dmr)
            if i_dmr % 3 == 2:
                self.verticalLayout_15.addWidget(rb_dmr)
        """Породы:"""
        row = 0
        for i_spc in range(len(self.name_species)):
            rb_spc = QtWidgets.QRadioButton(self.groupBox_3)
            rb_spc.setText(str(self.name_species[i_spc]))
            try:  # выбираю radiobutton по прошлому значению
                if str(self.name_species[i_spc]) == str(self.last_data['species']):
                    rb_spc.setChecked(True)
            except KeyError:
                None
            self.rb_spc.append(rb_spc)
            if i_spc % 2 == 0:
                self.verticalLayout_6.addWidget(rb_spc)
            if i_spc % 2 == 1:
                self.verticalLayout_7.addWidget(rb_spc)
                row += 1
        """Смотрю прошлую техническую годность"""
        try:
            if self.last_data['num_ind'] != 0 or self.last_data['num_half_ind'] != 0 or self.last_data['num_fuel'] != 0:
                if self.last_data['num_ind'] > 0:
                    self.radioButton_34.setChecked(True)
                if self.last_data['num_fuel'] > 0:
                    self.radioButton_35.setChecked(True)
                if self.last_data['num_half_ind'] > 0:
                    self.radioButton_36.setChecked(True)
        except KeyError:
            None

    def save(self):
        for dmr in self.rb_dmrs:
            if dmr.isChecked():
                self.output_data['dmr'] = int(dmr.text())
        for spc in self.rb_spc:
            if spc.isChecked():
                self.output_data['species'] = spc.text()
        if self.radioButton_34.isChecked():
            self.output_data['num_ind'] = int(self.label_2.text())
            self.output_data['num_fuel'] = 0
            self.output_data['num_half_ind'] = 0
        if self.radioButton_35.isChecked():
            self.output_data['num_ind'] = 0
            self.output_data['num_fuel'] = int(self.label_2.text())
            self.output_data['num_half_ind'] = 0
        if self.radioButton_36.isChecked():
            self.output_data['num_ind'] = 0
            self.output_data['num_fuel'] = 0
            self.output_data['num_half_ind'] = int(self.label_2.text())
        if len(self.output_data) == 6:
            self.accept()
        else:
            QtWidgets.QMessageBox.critical(self, 'Ошибка', 'Не выбраны все параметры.')


