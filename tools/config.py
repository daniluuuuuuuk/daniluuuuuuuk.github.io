import configparser
import os
from . import module_errors as er
from qgis.PyQt.QtWidgets import QMessageBox

class Configurer:
  """Класс используется для чтения и записи данных в файл конфигурации модуля config.ini
  """
  def __init__(self, section, *args):
    self.config = configparser.ConfigParser()
    self.configFilePath = self.resolve('config.ini')
    self.section = section
    self.options = args

  def resolve(self, name, basepath=None):
    if not basepath:
      basepath = os.path.dirname(os.path.dirname(__file__))
    return os.path.join(basepath, name)

  def readConfigs(self):
    try:
      self.config.read(self.configFilePath)
      configKeys = [key for key in self.config[self.section]]
      keyValue = {}
      for key in configKeys:
        keyValue[key] = (self.config[self.section][key])
      return keyValue
    except Exception as e:
        QMessageBox.information(None, er.MODULE_ERROR, er.CONFIG_FILE_ERROR + str(e))

  def writeConfigs(self):
    try:
      self.config.read(self.configFilePath)
      configToChange = self.config[self.section]
      for key, value in self.options[0].items():
        configToChange[key] = value
      self.config[self.section] = self.options[0]
      with open(self.configFilePath, 'w') as configfile:
        self.config.write(configfile)
    except Exception as e:
      QMessageBox.information(None, er.MODULE_ERROR, er.CONFIG_FILE_ERROR + str(e))