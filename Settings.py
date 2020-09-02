from qgis.PyQt.QtWidgets import QDialog, QMessageBox, QToolButton
from .gui import settingsDialog, changePortDialog
from .tools import config
from .tools import module_errors as er
from .PostgisDB import PostGisDB
from .BluetoothAdapter import BTAdapter

class SettingsWindow(QDialog):

    def __init__(self, parent=None):
        super(SettingsWindow, self).__init__(parent)
        self.ui = settingsDialog.Ui_settingsDialog()
        self.ui.setupUi(self)

class comPortWindow(QDialog):

    def __init__(self, parent=None):
        super(comPortWindow, self).__init__(parent)
        self.ui = changePortDialog.Ui_Dialog()
        self.ui.setupUi(self)

class SettingsController:

  def __init__(self, *args, **kwargs):
    self.sd = SettingsWindow()
    self.sd.setModal(False)
    self.tableUi = self.sd.ui

    self.populateBDSettings()
    self.populateBTSettings()

    self.tableUi.saveConfigButton.clicked.connect(self.saveBDConfig)
    self.tableUi.testDBConnection_pushButton.clicked.connect(self.getDBConnectionState)

    self.tableUi.changeForkComButton.clicked.connect(self.changeComPort)
    self.tableUi.changeRangeFinderComButton.clicked.connect(self.changeComPort)
    self.tableUi.SaveBTConfigPushButton.clicked.connect(self.saveComPortConfig)

    self.sd.exec()

  def populateBDSettings(self):
    try:
      cf = config.Configurer('dbconnection')
      bdsettings = cf.readConfigs()
      self.tableUi.connectionLineEdit.setText(bdsettings.get('host', 'No data'))
      self.tableUi.portLineEdit.setText(bdsettings.get('port', 'No data'))
      self.tableUi.usernameLineEdit.setText(bdsettings.get('user', 'No data'))
      self.tableUi.passwordLineEdit.setText(bdsettings.get('password', 'No data'))
      self.tableUi.BDNameLineEdit.setText(bdsettings.get('database', 'No data'))
    except Exception as e:
      QMessageBox.information(None, er.MODULE_ERROR, er.CONFIG_FILE_ERROR + str(e))

  def populateBTSettings(self):
    cf = config.Configurer('bluetooth')
    btsettings = cf.readConfigs()
    self.tableUi.forkComPortlineEdit.setText(btsettings.get('fork', 'No data'))
    self.tableUi.rangeFinderLineEdit.setText(btsettings.get('rangefinder', 'No data'))

  def changeComPort(self, *args, **kwargs):
    sender = self.sd.sender()

    sd = comPortWindow()
    ui = sd.ui

    btAdapter = BTAdapter()
    ui.comPortCombobox.addItems([x.device for x in btAdapter.getAvailablePorts()])
    result = sd.exec()
    
    if result == QDialog.Accepted:
      port = ui.comPortCombobox.currentText()
      if (sender == self.tableUi.changeForkComButton):
        self.tableUi.forkComPortlineEdit.setText(port)
      elif (sender == self.tableUi.changeRangeFinderComButton):
        self.tableUi.rangeFinderLineEdit.setText(port)

  def saveComPortConfig(self):
    try:
      settingsDict = {'fork' : self.tableUi.forkComPortlineEdit.text(), 
                    'rangefinder' : self.tableUi.rangeFinderLineEdit.text()}
      cf = config.Configurer('bluetooth', settingsDict)
      cf.writeConfigs()
    except Exception as e:
        QMessageBox.information(None, er.MODULE_ERROR, er.CONFIG_FILE_ERROR + str(e))

  def saveBDConfig(self):
    try:
      settingsDict = {'host' : self.tableUi.connectionLineEdit.text(), 
                    'port' : self.tableUi.portLineEdit.text(),
                    'user' : self.tableUi.usernameLineEdit.text(),
                    'password' : self.tableUi.passwordLineEdit.text(),
                    'database' : self.tableUi.BDNameLineEdit.text()}
      cf = config.Configurer('dbconnection', settingsDict)
      cf.writeConfigs()
    except Exception as e:
        QMessageBox.information(None, er.MODULE_ERROR, er.CONFIG_FILE_ERROR + str(e))

  def getDBConnectionState(self):
    dbconnection = PostGisDB()
    tc = dbconnection.testConnection(host= self.tableUi.connectionLineEdit.text(),
                                    port = self.tableUi.portLineEdit.text(),
                                    user = self.tableUi.usernameLineEdit.text(),
                                    password = self.tableUi.passwordLineEdit.text(),
                                    database = self.tableUi.BDNameLineEdit.text())
    if(tc):
      QMessageBox.information(None, er.MODULE_ERROR, er.CONNECTION_SUCCEEDED)
    else:
      QMessageBox.information(None, er.MODULE_ERROR, er.DATABASE_CONNECTION_ERROR)
