import sys, os
sys.path.insert(0, str(os.path.join(os.path.dirname(os.path.realpath(__file__)), ''))+'/lib/site-packages')

def classFactory(iface):
  from .QgsLes import QgsLes
  # from .ControllerGui import PluginGui
  # from .InitializeTables import initTables
  return QgsLes(iface)

## any other initialisation needed