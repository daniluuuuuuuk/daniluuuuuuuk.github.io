import sys, os
sys.path.insert(0, str(os.path.join(os.path.dirname(os.path.realpath(__file__)), ''))+'/lib/site-packages')

"""Точка входа модуля
"""
def classFactory(iface):
  from .QgsLes import QgsLes, DatabaseConnectionVerifier
  vfr = DatabaseConnectionVerifier(iface)
  runnable = vfr.verifyConfig()
  return QgsLes(iface, runnable)