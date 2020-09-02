from PyQt5 import QtCore
import datetime
import traceback

from ....src.models.nri import *
from ....src.models.ta_fund import *


class ExportData(QtCore.QThread):
    signal_status = QtCore.pyqtSignal(list)

    def __init__(self, **args):
        QtCore.QThread.__init__(self)
        self.all_data = args['data']
        self.dest_filename = args['filename']

    def make_data(self):
        file = open(self.dest_filename[0], 'w', encoding='windows-1251')
        curr_time = datetime.datetime.today().strftime("%d.%m.%Y %H:%M:%S")
        self.all_data['ta_fund']['date_filled'] = self.all_data['ta_fund']['date_filled'].strftime("%d.%m.%Y")
        self.all_data['ta_fund']['date_taxes'] = self.all_data['ta_fund']['date_taxes'].strftime("%d.%m.%Y")
        self.all_data['system']['code_enterprise'] = Organization.get(
            Organization.name_organization == self.all_data['system']['enterprise']).code_organization
        self.all_data['system']['code_forestry'] = Organization.get(
            Organization.name_organization == self.all_data['system']['forestry']).code_organization
        """Заменяю пустоту"""
        if not self.all_data['ta_fund']['year_for_inv']:
            self.all_data['ta_fund']['year_for_inv'] = ''
        if not self.all_data['ta_fund']['density']:
            self.all_data['ta_fund']['density'] = ''
        if not self.all_data['ta_fund']['age']:
            self.all_data['ta_fund']['age'] = ''
        if not self.all_data['ta_fund']['height_avg']:
            self.all_data['ta_fund']['height_avg'] = ''
        if not self.all_data['ta_fund']['diameter_avg']:
            self.all_data['ta_fund']['diameter_avg'] = ''
        if not self.all_data['ta_fund']['code_rgn_meth']:
            self.all_data['ta_fund']['code_rgn_meth'] = ''

        about = [f"[PRORGAMM NAME]=АРМ \"Лесопользование 3\"",
                 f"[SHORT PROGRAMM NAME]=АРМ ЛП3",
                 f"[DATE PROGRAMM]=19.09.2019",
                 f"[VERSION PROGRAMM]=3.2.1.5",
                 f"[SETUP ID ORGANIZATION]={self.all_data['system']['code_enterprise']}",
                 f"[SETUP NAME ORGANIZATION]={self.all_data['system']['enterprise']}",
                 f"[COMMENTARY]=Ведомость МДО",
                 f"[DATE ARCHIVE]={curr_time}",
                 f"[TYPE ARCHIVE]=0",
                 f"[COUNT TABLES]=3",
                 f"[CHECK SUMMA]=1470",
                 f"[TABLE NAME]=TA_FUND",
                 f"[COUNT FIELDS]=51",
                 f"[COUNT RECORDS]=1",
                 f"[BEGIN FIELDS]",
                 f"ID_FT NUMBER",
                 f"DATE_FILL DATE",
                 f"CODE_ORG NUMBER",
                 f"CODE_KIND_USE NUMBER",
                 f"CODE_GR_FOREST NUMBER",
                 f"YEAR_PL_WCT NUMBER",
                 f"YEAR_ALLOT NUMBER",
                 f"YEAR_FOR_INV NUMBER",
                 f"NUM_COMP VARCHAR2",
                 f"NUM_ALLOT NUMBER",
                 f"NUM_SUBCOMP VARCHAR2",
                 f"SQR_SUBC_SUM NUMBER",
                 f"SQR_ALLOT NUMBER",
                 f"CODE_SECT NUMBER",
                 f"CODE_WCT_METH NUMBER",
                 f"CODE_ACC_METH NUMBER",
                 f"FORMULA VARCHAR2",
                 f"DENSITY NUMBER",
                 f"AGE NUMBER",
                 f"CODE_BONIT NUMBER",
                 f"HEIGHT_AVG NUMBER",
                 f"DIAMETER_AVG NUMBER",
                 f"VOL_TRUNK_AVG NUMBER",
                 f"CODE_TYPE_FOR NUMBER",
                 f"CODE_STATUS NUMBER",
                 f"CODE_RGN_METH NUMBER",
                 f"CODE_RANK_TRF NUMBER",
                 f"CODE_METH_REAL NUMBER",
                 f"NUM_ACT_RAD NUMBER",
                 f"DATE_ACT_RAD DATE",
                 f"SOIL_POL_RAD NUMBER",
                 f"SPEC_ACTIVITY_IND VARCHAR2",
                 f"SPEC_ACTIVITY_FUEL VARCHAR2",
                 f"SIGN_DIFF_ACCESS NUMBER",
                 f"CODE_CAT_PROTECTION NUMBER",
                 f"CODE_PROT_AREA NUMBER",
                 f"CODE_AUTHOR NUMBER",
                 f"CODE_PLAN_ASSORT NUMBER",
                 f"DATE_OVERRATE DATE",
                 f"CODE_KIND_USE_OVERRATE NUMBER",
                 f"SIGN_FORMULA_OVERRATE NUMBER",
                 f"COMMENTARY VARCHAR2",
                 f"WTICKET_NUM NUMBER",
                 f"WTICKET_DATE DATE",
                 f"SIGN_ONMAIN NUMBER",
                 f"DATE_ONMAIN DATE",
                 f"SIGN_STATE_FOREST_FUND NUMBER",
                 f"CODE_ECON NUMBER",
                 f"SQR_PORTAGE NUMBER",
                 f"IS_UPDATED NUMBER",
                 f"DATE_INSPECT VARCHAR2",
                 f"[END FIELDS]",
                 f"[BEGIN DATA]",
                 f"4",  # LP : TA_FUND.ID_FT  (Идентификатор лесосеки)
                 f"{self.all_data['ta_fund']['date_filled']}",  # LP : TA_FUND.DATE_FILL  (Дата заполнения)
                 f"{self.all_data['system']['code_forestry']}",  # LP : TA_FUND.CODE_ORG  (Идентификатор организации)
                 f"{self.all_data['ta_fund']['code_kind_use']}",
                 # LP : TA_FUND.CODE_KIND_USE  (Идентификатор вида пользования)
                 f"{self.all_data['ta_fund']['code_gr_forest']}",
                 # LP : TA_FUND.CODE_GR_FOREST  (Идентификатор группы лесов)
                 f"{self.all_data['ta_fund']['year_forest_fund']}",  # LP : TA_FUND.YEAR_PL_WCT  (Год рубки плановый)
                 f"{self.all_data['ta_fund']['year_cutting_area']}",  # LP : TA_FUND.YEAR_ALLOT  (Год отвода )
                 f"{self.all_data['ta_fund']['year_for_inv']}",
                 # LP : TA_FUND.YEAR_FOR_INV  (Год лесоустройства (актуализации))
                 f"{self.all_data['system']['num_compartment']}",  # LP : TA_FUND.NUM_COMP  (Номер квартала)
                 f"{self.all_data['system']['num_cutting_area']}",  # LP : TA_FUND.NUM_ALLOT  (Номер делянки (лесосеки))
                 f"{self.all_data['system']['num_sub_compartment']}",  # LP : TA_FUND.NUM_SUBCOMP  (Номера выделов)
                 f"0",  # LP : TA_FUND.SQR_SUBC_SUM  (Площадь выделов экспл., суммарная, га)
                 f"{self.all_data['system']['area']}",  # LP : TA_FUND.SQR_ALLOT  (Площадь эксплуатационная, га)
                 f"{self.all_data['ta_fund']['code_section']}",  # LP : TA_FUND.CODE_SECT  (Идентификатор хозсекции)
                 f"{self.all_data['ta_fund']['code_wct_meth']}",
                 # LP : TA_FUND.CODE_WCT_METH  (Идентификатор способа рубок)
                 f"{self.all_data['ta_fund']['code_acc_meth']}",
                 # LP : TA_FUND.CODE_ACC_METH  (Идентификатор способа учета)
                 f"{self.all_data['ta_fund']['formula']}",  # LP : TA_FUND.FORMULA  (Формула состава)
                 f"{self.all_data['ta_fund']['density']}",  # LP : TA_FUND.DENSITY  (Полнота)
                 f"{self.all_data['ta_fund']['age']}",  # LP : TA_FUND.AGE  (Возраст)
                 f"{self.all_data['ta_fund']['code_bonit']}",  # LP : TA_FUND.CODE_BONIT  (Идентификатор бонитета)
                 f"{self.all_data['ta_fund']['height_avg']}",  # LP : TA_FUND.HEIGHT_AVG  (Высота средняя)
                 f"{self.all_data['ta_fund']['diameter_avg']}",  # LP : TA_FUND.DIAMETER_AVG  (Диаметр средний)
                 f"",  # LP : TA_FUND.VOL_TRUNK_AVG  (Объем хлыста средний)
                 f"{self.all_data['ta_fund']['code_type_for']}",
                 # LP : TA_FUND.CODE_TYPE_FOR  (Идентификатор типа леса)
                 f"{self.all_data['ta_fund']['code_status']}",
                 # LP : TA_FUND.CODE_STATUS  (Идентификатор состояния насаждения)
                 f"{self.all_data['ta_fund']['code_rgn_meth']}",
                 # LP : TA_FUND.CODE_RGN_METH  (Идентификатор метода восстановления)
                 f"{self.all_data['ta_fund']['code_rank_trf']}",  # LP : TA_FUND.CODE_RANK_TRF  (Идентификатор разряда такс)
                 f"{self.all_data['ta_fund']['code_meth_real']}",
                 # LP : TA_FUND.CODE_METH_REAL  (Идентификатор метода реализации)
                 f"",  # LP : TA_FUND.NUM_ACT_RAD  (Номер Акта радиационной оценки)
                 f"",  # LP : TA_FUND.DATE_ACT_RAD  (Дата Акта радиационной оценки)
                 f"",  # LP : TA_FUND.SOIL_POL_RAD  (Плотность радиоактивного загрязнения, Ku-км2)
                 f"",  # LP : TA_FUND.SPEC_ACTIVITY_IND  (Удельная активность деловой древесины, Бк-кг)
                 f"",  # LP : TA_FUND.SPEC_ACTIVITY_FUEL  (Удельная активность дровяной древесины, Бк-кг)
                 f"",  # LP : TA_FUND.SIGN_DIFF_ACCESS  (Признак доступности (0 - доступная, 1 - труднодоступная))
                 f"",  # LP : TA_FUND.CODE_CAT_PROTECTION  (Идентификатор категории защитности лесов)
                 f"",  # LP : TA_FUND.CODE_PROT_AREA  (Идентификатор особо защитного участка леса)
                 f"{self.all_data['ta_fund']['code_author']}",
                 # LP : TA_FUND.CODE_AUTHOR  (Идентификатор автора (расчет материальной оценки))
                 f"",  # LP : TA_FUND.CODE_PLAN_ASSORT  (Идентификатор сортиментного плана (расчет материальной оценки))
                 f"{self.all_data['ta_fund']['date_taxes']}",
                 # LP : TA_FUND.DATE_OVERRATE  (Дата оценки запасов (расчет денежной оценки))
                 f"{self.all_data['ta_fund']['code_kind_use_for_trf_vl']}",
                 # LP : TA_FUND.CODE_KIND_USE_OVERRATE  (Идентификатор вида пользования (расчет денежной оценки))
                 f"",
                 # LP : TA_FUND.SIGN_FORMULA_OVERRATE  (Способ расчета формулы (0 - в порядке убывания запасов по породам, 1 - в порядке убывания запасов по хозяйственным группам пород))
                 f"{self.all_data['ta_fund']['description']}",  # LP : TA_FUND.COMMENTARY  (Комментарий)
                 f"",  # LP : TA_FUND.WTICKET_NUM  (Номер лесорубочного билета)
                 f"",  # LP : TA_FUND.WTICKET_DATE  (Дата лесорубочного билета)
                 f"",  # LP : TA_FUND.SIGN_ONMAIN  (Признак включения в РГП)
                 f"",  # LP : TA_FUND.DATE_ONMAIN  (Дата измененя признака включения в РГП)
                 f"",
                 # LP : TA_FUND.SIGN_STATE_FOREST_FUND  (Признак включения в государственный лесной фонд (0-не включено, 1 - включено))
                 f"{self.all_data['ta_fund']['code_econ']}",  # LP : TA_FUND.CODE_ECON  (Идентификатор группы пород)
                 f"",  # LP : TA_FUND.SQR_PORTAGE  ()
                 f"",  # LP : TA_FUND.IS_UPDATED  ()
                 f"",  # LP : TA_FUND.DATE_INSPECT  ()
                 f"[END DATA]"]
        for row in about:
            file.write(row + '\n')

        ta_fund_enum_about = [f"[TABLE NAME]=TA_FUND_ENUM",
                              f"[COUNT FIELDS]=8",
                              f"[COUNT RECORDS]={self.all_data['system']['count_records_enum']}",
                              f"[BEGIN FIELDS]",
                              f"ID_FT NUMBER",
                              f"SIGN_KIND_SQR NUMBER",
                              f"NUM_SPLOT NUMBER",
                              f"CODE_SPECIES NUMBER",
                              f"DMR NUMBER",
                              f"NUM_IND NUMBER",
                              f"NUM_HALFIND NUMBER",
                              f"NUM_FUEL NUMBER",
                              f"[END FIELDS]"]
        for row in ta_fund_enum_about:
            file.write(row + '\n')
        #  Записываю данные перечётки:
        for i in Ta_fund_enum.select().where(Ta_fund_enum.offset_uuid == self.all_data['ta_fund_enum']['offset_uuid']):
            file.write('[BEGIN DATA]\n')  # Начало данных
            file.write('4\n')  # идентификатор лесосеки (в ПО не учитывается)
            file.write('1\n')  # номер площади перечета (в ПО не учитывается)
            file.write('0\n')  # номер пробной площади (в ПО не учитывается)
            file.write(str(i.code_species) + '\n')  # код породы
            file.write(str(i.dmr) + '\n')  # диаметр
            file.write(str(i.num_ind) + '\n')  # число дровянных
            file.write(str(i.num_biodiversity) + '\n')  # число боразнообразия
            file.write(str(i.num_fuel) + '\n')  # число деловых
            file.write('[END DATA]\n')  # конец данных

        ta_fund_splot_wpulp_about = [f"[TABLE NAME]=TA_FUND_SPLOT_WPULP",
                                     f"[COUNT FIELDS]=25",
                                     f"[COUNT RECORDS]={str(len(self.all_data['system']['species_trf_height']))}",
                                     f"[BEGIN FIELDS]",
                                     f"ID_FT NUMBER",
                                     f"SIGN_KIND_SQR NUMBER",
                                     f"NUM_SPLOT NUMBER",
                                     f"CODE_SPECIES NUMBER",
                                     f"CODE_TRF_HEIGHT NUMBER",
                                     f"WPULP_IND_LG NUMBER",
                                     f"WPULP_IND_MD NUMBER",
                                     f"WPULP_IND_SM NUMBER",
                                     f"WPULP_IND_ALL NUMBER",
                                     f"WPULP_CRW_LQ NUMBER",
                                     f"WPULP_FUEL NUMBER",
                                     f"WPULP_BAVIN NUMBER",
                                     f"WPULP_WASTE NUMBER",
                                     f"SIGN_CRW_LQ NUMBER",
                                     f"SIGN_BAVIN NUMBER",
                                     f"SIGN_WASTE NUMBER",
                                     f"TRF_VL_IND NUMBER",
                                     f"TRF_VL_FUEL NUMBER",
                                     f"TRF_VL_CRW_LQ NUMBER",
                                     f"TRF_VL_BAVIN NUMBER",
                                     f"TRF_VL_WASTE NUMBER",
                                     f"NUM_ROUND_TRF NUMBER",
                                     f"TRF_VL_LG NUMBER",
                                     f"TRF_VL_MD NUMBER",
                                     f"TRF_VL_SM NUMBER",
                                     f"[END FIELDS]"]
        for row in ta_fund_splot_wpulp_about:
            file.write(row + '\n')

        for i in self.all_data['system']['species_trf_height']:
            file.write('[BEGIN DATA]\n')  # Начало данных
            file.write('4\n')  # LP : TA_FUND_SPLOT_WPULP.ID_FT  ()
            file.write('1\n')  # LP : TA_FUND_SPLOT_WPULP.SIGN_KIND_SQR  ()
            file.write('0\n')  # LP : TA_FUND_SPLOT_WPULP.NUM_SPLOT  ()
            file.write(f"{i}\n")  # LP : TA_FUND_SPLOT_WPULP.CODE_SPECIES  ()
            file.write(
                f"{self.all_data['system']['species_trf_height'][i]}\n")  # LP : TA_FUND_SPLOT_WPULP.CODE_TRF_HEIGHT  ()
            file.write('\n')  # LP : TA_FUND_SPLOT_WPULP.WPULP_IND_LG  ()
            file.write('\n')  # LP : TA_FUND_SPLOT_WPULP.WPULP_IND_MD  ()
            file.write('\n')  # LP : TA_FUND_SPLOT_WPULP.WPULP_IND_SM  ()
            file.write('\n')  # LP : TA_FUND_SPLOT_WPULP.WPULP_IND_ALL  ()
            file.write('\n')  # LP : TA_FUND_SPLOT_WPULP.WPULP_CRW_LQ  ()
            file.write('\n')  # LP : TA_FUND_SPLOT_WPULP.WPULP_FUEL  ()
            file.write('\n')  # LP : TA_FUND_SPLOT_WPULP.WPULP_BAVIN  ()
            file.write('\n')  # LP : TA_FUND_SPLOT_WPULP.WPULP_WASTE  ()
            file.write('0\n')  # LP : TA_FUND_SPLOT_WPULP.SIGN_CRW_LQ  ()
            file.write('0\n')  # LP : TA_FUND_SPLOT_WPULP.SIGN_BAVIN  ()
            file.write('0\n')  # LP : TA_FUND_SPLOT_WPULP.SIGN_WASTE  ()
            file.write('\n')  # LP : TA_FUND_SPLOT_WPULP.TRF_VL_IND  ()
            file.write('\n')  # LP : TA_FUND_SPLOT_WPULP.TRF_VL_FUEL  ()
            file.write('\n')  # LP : TA_FUND_SPLOT_WPULP.TRF_VL_CRW_LQ  ()
            file.write('\n')  # LP : TA_FUND_SPLOT_WPULP.TRF_VL_BAVIN  ()
            file.write('\n')  # LP : TA_FUND_SPLOT_WPULP.TRF_VL_WASTE  ()
            file.write('\n')  # LP : TA_FUND_SPLOT_WPULP.NUM_ROUND_TRF  ()
            file.write('\n')  # LP : TA_FUND_SPLOT_WPULP.TRF_VL_LG  ()
            file.write('\n')  # LP : TA_FUND_SPLOT_WPULP.TRF_VL_MD  ()
            file.write('\n')  # LP : TA_FUND_SPLOT_WPULP.TRF_VL_SM  ()
            file.write('[END DATA]\n')

        ta_fund_wpulp = [f"[TABLE NAME]=TA_FUND_WPULP",
                         f"[COUNT FIELDS]=23",
                         f"[COUNT RECORDS]={str(len(self.all_data['system']['species_trf_height']))}",
                         f"[BEGIN FIELDS]",
                         f"ID_FT NUMBER",
                         f"CODE_SPECIES NUMBER",
                         f"CODE_TRF_HEIGHT NUMBER",
                         f"WPULP_IND_LG NUMBER",
                         f"WPULP_IND_MD NUMBER",
                         f"WPULP_IND_SM NUMBER",
                         f"WPULP_IND_ALL NUMBER",
                         f"WPULP_CRW_LQ NUMBER",
                         f"WPULP_FUEL NUMBER",
                         f"WPULP_BAVIN NUMBER",
                         f"WPULP_WASTE NUMBER",
                         f"SIGN_CRW_LQ NUMBER",
                         f"SIGN_BAVIN NUMBER",
                         f"SIGN_WASTE NUMBER",
                         f"TRF_VL_IND NUMBER",
                         f"TRF_VL_FUEL NUMBER",
                         f"TRF_VL_CRW_LQ NUMBER",
                         f"TRF_VL_BAVIN NUMBER",
                         f"TRF_VL_WASTE NUMBER",
                         f"NUM_ROUND_TRF NUMBER",
                         f"TRF_VL_LG NUMBER",
                         f"TRF_VL_MD NUMBER",
                         f"TRF_VL_SM NUMBER",
                         f"[END FIELDS]"]
        for row in ta_fund_wpulp:
            file.write(row + '\n')

        for i in Ta_fund_wpulp.select().where(
                Ta_fund_wpulp.offset_uuid == self.all_data['ta_fund_wpulp']['offset_uuid']):
            file.write('[BEGIN DATA]\n')  # Начало данных
            file.write('4\n')  # LP : TA_FUND_WPULP.ID_FT  ()
            file.write(str(i.code_species) + '\n')  # LP : TA_FUND_WPULP.CODE_SPECIES  ()
            file.write(str(i.code_trf_height) + '\n')  # LP : TA_FUND_WPULP.CODE_TRF_HEIGHT  ()
            file.write(str(i.wpulp_ind_large) + '\n')  # LP : TA_FUND_WPULP.WPULP_IND_LG  ()
            file.write(str(i.wpulp_ind_medium) + '\n')  # LP : TA_FUND_WPULP.WPULP_IND_MD  ()
            file.write(str(i.wpulp_ind_small) + '\n')  # LP : TA_FUND_WPULP.WPULP_IND_SM  ()
            file.write(str(i.wpulp_ind) + '\n')  # LP : TA_FUND_WPULP.WPULP_IND_ALL  ()
            file.write(str(i.wpulp_crw_lq) + '\n')  # LP : TA_FUND_WPULP.WPULP_CRW_LQ  ()
            file.write(str(i.wpulp_fuel) + '\n')  # LP : TA_FUND_WPULP.WPULP_FUEL  ()
            file.write(str(i.wpulp_brushwood) + '\n')  # LP : TA_FUND_WPULP.WPULP_BAVIN  ()
            file.write(str(i.wpulp_waste) + '\n')  # LP : TA_FUND_WPULP.WPULP_WASTE  ()
            file.write('0\n')  # LP : TA_FUND_WPULP.SIGN_CRW_LQ  ()
            file.write('0\n')  # LP : TA_FUND_WPULP.SIGN_BAVIN  ()
            file.write('0\n')  # LP : TA_FUND_WPULP.SIGN_WASTE  ()
            file.write(str(i.trf_vl_ind) + '\n')  # LP : TA_FUND_WPULP.TRF_VL_IND  ()
            file.write(str(i.trf_vl_fuel) + '\n')  # LP : TA_FUND_WPULP.TRF_VL_FUEL  ()
            file.write(str(i.trf_vl_crw_lq) + '\n')  # LP : TA_FUND_WPULP.TRF_VL_CRW_LQ  ()
            file.write(str(i.trf_vl_brushwood) + '\n')  # LP : TA_FUND_WPULP.TRF_VL_BAVIN  ()
            file.write(str(i.trf_vl_waste) + '\n')  # LP : TA_FUND_WPULP.TRF_VL_WASTE  ()
            file.write('\n')  # LP : TA_FUND_WPULP.NUM_ROUND_TRF  ()
            file.write('\n')  # LP : TA_FUND_WPULP.TRF_VL_LG  ()
            file.write('\n')  # LP : TA_FUND_WPULP.TRF_VL_MD  ()
            file.write('\n')  # LP : TA_FUND_WPULP.TRF_VL_SM  ()
            file.write('[END DATA]\n')  # конец данных

        file.close()
        self.signal_status.emit(['Экспорт произведен успешно.', '', ''])

    def run(self):
        try:
            self.make_data()
        except Exception as error:
            self.signal_status.emit(['Ошибка сохранения', error, str(traceback.format_exc())])
