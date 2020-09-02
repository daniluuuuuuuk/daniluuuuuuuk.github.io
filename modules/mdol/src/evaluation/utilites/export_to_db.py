from PyQt5 import QtCore
import traceback

from ....src.models.ta_fund import *


class Export_data(QtCore.QThread):
    signal_status = QtCore.pyqtSignal(list)

    def __init__(self, **args):
        QtCore.QThread.__init__(self)
        self.attributes = args['attributes']
        self.data = args['data']

    def run(self):
        """Записываю данные в БД"""
        """Записываю таблицу описания МДОЛ"""
        try:
            Ta_fund.create(**self.attributes['ta_fund'])
        except Exception as error:
            self.signal_status.emit(['Ошибка сохранения', error, str(traceback.format_exc())])
            return None

        for row in self.data:
            try:
                Ta_fund_wpulp.create(offset_uuid=self.attributes['system']['offset_uuid'],
                                     code_species=row['code_species'],
                                     code_trf_height=row['code_trf_height'],
                                     wpulp_ind_large=float(row['wpulp_ind_large']),
                                     wpulp_ind_medium=float(row['wpulp_ind_medium']),
                                     wpulp_ind_small=float(row['wpulp_ind_small']),
                                     wpulp_ind=float(row['wpulp_ind']),
                                     wpulp_fuel=float(row['wpulp_fuel']),
                                     wpulp_liquid=float(row['wpulp_liquid']),
                                     wpulp_crw_lq=float(row['wpulp_crw_lq']),
                                     wpulp_brushwood=float(row['wpulp_brushwood']),
                                     wpulp_waste=float(row['wpulp_waste']),
                                     wpulp_total=float(row['wpulp_total']),
                                     trf_vl_ind=float(row['trf_vl_ind']),
                                     trf_vl_fuel=float(row['trf_vl_fuel']),
                                     trf_vl_liquid=float(row['trf_vl_liquid']),
                                     trf_vl_crw_lq=float(row['trf_vl_crw_lq']),
                                     trf_vl_brushwood=float(row['trf_vl_brushwood']),
                                     trf_vl_waste=float(row['trf_vl_waste']),
                                     trf_vl_total=float(row['trf_vl_total']),
                                     )
            except Exception as error:
                self.signal_status.emit(['Ошибка сохранения', error, str(traceback.format_exc())])
                return None
        self.signal_status.emit(['Сохранение ВМОЛ успешно.', '', ''])

