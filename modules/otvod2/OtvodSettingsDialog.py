from qgis.PyQt.QtWidgets import QDialog
from .gui.otvodSettings import Ui_Dialog as uiOtvodSettingDialog


class OtvodSettingsWindow(QDialog):
    def __init__(self, *args, **kwargs):
        super(OtvodSettingsWindow, self).__init__()
        self.ui = uiOtvodSettingDialog()
        self.ui.setupUi(self)
        self.tabletypes = {'Координаты': 0,
                           'Азимуты': 1,
                           'Румбы': 2}
        self.coordtypes = {'Десятичный': 0,
                           'Градусы/Минуты/Секунды': 1}
        self.ui.tabletype_comboBox.addItems(
            [key for key, value in self.tabletypes.items()])
        self.ui.coordtype_comboBox.addItems(
            [key for key, value in self.coordtypes.items()])
