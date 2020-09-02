from PyQt5 import QtCore
from decimal import Decimal, ROUND_HALF_UP

from ....src.models.ta_fund import *
from ....src.models.nri import *
from ....src.models.public import *


class ImportData(QtCore.QThread):
    signal_status = QtCore.pyqtSignal(str)
    signal_general = QtCore.pyqtSignal(dict)
    signal_restatement = QtCore.pyqtSignal(dict)
    signal_wpulp_info = QtCore.pyqtSignal(dict)
    signal_wpulp = QtCore.pyqtSignal(list)

    def __init__(self, **args):
        QtCore.QThread.__init__(self)
        self.uuid = args['uuid']

    def general(self):
        """
        В этом методе получаю:
        Название лесхоза, лесничества
        Номера квартала, выдела, лесосеки
        ФИО, поле дополнительной информации, эксплуатационную площадь
        """
        general_data = {}
        num_forestry = Cutting_area.select().where(Cutting_area.uuid == self.uuid).get().num_forestry
        num_enterprise = Cutting_area.select().where(Cutting_area.uuid == self.uuid).get().num_enterprise
        if num_forestry < 10:
            temp = str(num_enterprise) + '0' + str(num_forestry)
        else:
            temp = str(num_enterprise) + str(num_forestry)

        for i in Organization.select():
            if str(i.code_organization)[-5:] == temp:
                general_data['forestry'] = i.name_organization
            if str(i.code_organization)[-5:] == str(num_enterprise) + '00':
                general_data['enterprise'] = i.name_organization
                code_leshoz = i.code_organization

        for i in Organization.select():
            if str(i.code_organization) == str(num_enterprise)[:-4] + '0000':
                self.general_data['gplho'] = i.name_organization

        general_data['sub_compartment'] = Cutting_area.select().where(
            Cutting_area.uuid == self.uuid).get().num_sub_compartment
        general_data['compartment'] = Cutting_area.select().where(
            Cutting_area.uuid == self.uuid).get().num_compartment
        general_data['cutting_area'] = Cutting_area.select().where(
            Cutting_area.uuid == self.uuid).get().num_cutting_area
        general_data['area'] = Cutting_area.select().where(Cutting_area.uuid == self.uuid).get().area
        general_data['person_name'] = Cutting_area.select().where(Cutting_area.uuid == self.uuid).get().person_name
        general_data['description'] = Cutting_area.select().where(Cutting_area.uuid == self.uuid).get().description

        return general_data

    def restatement(self):
        """
        В этом методе получаю:
        Колличество деловых/дровяных деревьев и деревьев биоразнообразия (quality_data и not_cutting_data)
        с таблицы mdo.Ta_fund_enum
        """
        restatement_data = {}
        quality_data = []
        not_cutting_data = []
        for record in Ta_fund_enum.select().where(Ta_fund_enum.offset_uuid == self.uuid):
            species_latin = Species.select().where(Species.code_species == record.code_species).get().name_species_latin
            quality_data.append({
                'species': species_latin,
                'dmr': record.dmr,
                'num_ind': record.num_ind,
                'num_fuel': record.num_fuel
            })
            if record.num_biodiversity > 0:  # отдельно собираю информацию по биоразнообразию
                species = Species.select().where(
                    Species.code_species == record.code_species).get().name_species
                not_cutting_data.append({
                    'species': species,
                    'dmr': record.dmr,
                    'num_biodiversity': record.num_biodiversity
                })
        restatement_data['quality_data'] = quality_data  # деловые\дровяный
        restatement_data['not_cutting_data'] = not_cutting_data  # биоразнообразие

        return restatement_data

    def wpulp_info(self):
        """
        В этом методе получаю параметры МДОЛ:
        Вид пользования, Категорию леса, Год лес. фонда, Год отвода, Дату начала действия такс, Таксы, Таблицу запаса,
        Разряды высот для пород, дату заполнения, разряд такс, реализацю и т.д.
        """
        wpulp_info = {}
        tmp = {}
        ta_f = Ta_fund.get(Ta_fund.offset_uuid == self.uuid)
        wpulp_info['selected_kind_use'] = Kind_use.get(Kind_use.code_kind_use == ta_f.code_kind_use).name_kind_use
        wpulp_info['selected_gr_forest'] = Gr_forest.get(Gr_forest.code_gr_forest == ta_f.code_gr_forest).name_gr_forest
        wpulp_info['selected_meth_real'] = Meth_real.get(Meth_real.code_meth_real == ta_f.code_meth_real).name_meth_real
        wpulp_info['selected_author'] = Author.get(Author.code_author == ta_f.code_author).name_author
        wpulp_info['selected_kind_use_for_trf_vl'] = int(ta_f.code_kind_use_for_trf_vl)
        wpulp_info['selected_rank_trf'] = Rank_trf.get(Rank_trf.code_rank_trf == ta_f.code_rank_trf).name_rank_trf
        wpulp_info['selected_date_taxes'] = ta_f.date_taxes
        wpulp_info['selected_date_filled'] = ta_f.date_filled
        wpulp_info['year_forest_fund'] = ta_f.year_forest_fund
        wpulp_info['year_cutting_area'] = ta_f.year_cutting_area
        wpulp_info['year_for_inv'] = ta_f.year_for_inv
        wpulp_info['person_name'] = ta_f.person_name
        wpulp_info['description'] = ta_f.description
        wpulp_info['selected_section'] = Section.get(Section.code_section == ta_f.code_section).name_section
        wpulp_info['selected_econ'] = Econ.get(Econ.code_econ == ta_f.code_econ).name_econ
        wpulp_info['selected_wct_meth'] = Wct_meth.get(Wct_meth.code_wct_meth==str(ta_f.code_wct_meth)[:-1]+'0').name_wct_meth
        wpulp_info['selected_wct_meth_group'] = Wct_meth.get(Wct_meth.code_wct_meth==ta_f.code_wct_meth).name_wct_meth
        wpulp_info['selected_acc_meth'] = Acc_meth.get(Acc_meth.code_acc_meth==ta_f.code_acc_meth).name_acc_meth
        wpulp_info['sign_liquid_crown'] = ta_f.sign_liquid_crown
        wpulp_info['sign_brushwood'] = ta_f.sign_brushwood
        wpulp_info['sign_waste'] = ta_f.sign_waste
        if ta_f.code_rgn_meth:  # не обязательный параметр
            wpulp_info['selected_rgn_meth'] = Rgn_meth.get(Rgn_meth.code_rgn_meth==ta_f.code_rgn_meth).name_rgn_meth
        else:
            wpulp_info['selected_rgn_meth'] = ''
        wpulp_info['selected_status'] = Status.get(Status.code_status==ta_f.code_status).name_status
        wpulp_info['selected_bonit'] = Bonit.get(Bonit.code_bonit==ta_f.code_bonit).name_bonit
        wpulp_info['selected_type_for'] = Type_for.get(Type_for.code_type_for==ta_f.code_type_for).name_type_for
        wpulp_info['formula'] = str(ta_f.formula)
        if ta_f.age:
            wpulp_info['age'] = str(ta_f.age)
        else:
            wpulp_info['age'] = ''
        if ta_f.density:
            wpulp_info['density'] = str(ta_f.density)
        else:
            wpulp_info['density'] = ''
        if ta_f.height_avg:
            wpulp_info['height_avg'] = str(ta_f.height_avg)
        else:
            wpulp_info['height_avg'] = ''
        if ta_f.diameter_avg:
            wpulp_info['diameter_avg'] = str(ta_f.diameter_avg)
        else:
            wpulp_info['diameter_avg'] = ''
        if ta_f.year_for_inv:
            wpulp_info['year_for_inv'] = str(ta_f.year_for_inv)
        else:
            wpulp_info['year_for_inv'] = ''

        """Разряды высот попородам"""
        for record in Ta_fund_wpulp.select().where(Ta_fund_wpulp.offset_uuid == self.uuid):
            tmp[Species.get(Species.code_species == record.code_species).name_species] = \
                Trf_height.get(Trf_height.code_trf_height == record.code_trf_height).name_trf_height

        wpulp_info['trf_s'] = tmp
        return wpulp_info

    def wpulp(self):
        """
        В этом методе получаю данные об объёмах и стоимости древесины
        """
        wpulp_data = []

        for record in Ta_fund_wpulp.select().where(Ta_fund_wpulp.offset_uuid == self.uuid):
            tmp = {}
            tmp['code_species'] = int(str(record.code_species))
            tmp['code_trf_height'] = int(str(record.code_trf_height))
            tmp['wpulp_ind_large'] = (Decimal(str(record.wpulp_ind_large))).quantize(Decimal("1.00"), ROUND_HALF_UP)
            tmp['wpulp_ind_medium'] = (Decimal(str(record.wpulp_ind_medium))).quantize(Decimal("1.00"), ROUND_HALF_UP)
            tmp['wpulp_ind_small'] = (Decimal(str(record.wpulp_ind_small))).quantize(Decimal("1.00"), ROUND_HALF_UP)
            tmp['wpulp_ind'] = (Decimal(str(record.wpulp_ind))).quantize(Decimal("1.00"), ROUND_HALF_UP)
            tmp['wpulp_fuel'] = (Decimal(str(record.wpulp_fuel))).quantize(Decimal("1.00"), ROUND_HALF_UP)
            tmp['wpulp_liquid'] = (Decimal(str(record.wpulp_liquid))).quantize(Decimal("1.00"), ROUND_HALF_UP)
            tmp['wpulp_crw_lq'] = (Decimal(str(record.wpulp_crw_lq))).quantize(Decimal("1.00"), ROUND_HALF_UP)
            tmp['wpulp_brushwood'] = (Decimal(str(record.wpulp_brushwood))).quantize(Decimal("1.00"), ROUND_HALF_UP)
            tmp['wpulp_waste'] = (Decimal(str(record.wpulp_waste))).quantize(Decimal("1.00"), ROUND_HALF_UP)
            tmp['wpulp_total'] = (Decimal(str(record.wpulp_total))).quantize(Decimal("1.00"), ROUND_HALF_UP)
            tmp['trf_vl_ind'] = (Decimal(str(record.trf_vl_ind))).quantize(Decimal("1.00"), ROUND_HALF_UP)
            tmp['trf_vl_fuel'] = (Decimal(str(record.trf_vl_fuel))).quantize(Decimal("1.00"), ROUND_HALF_UP)
            tmp['trf_vl_liquid'] = (Decimal(str(record.trf_vl_liquid))).quantize(Decimal("1.00"), ROUND_HALF_UP)
            tmp['trf_vl_crw_lq'] = (Decimal(str(record.trf_vl_crw_lq))).quantize(Decimal("1.00"), ROUND_HALF_UP)
            tmp['trf_vl_brushwood'] = (Decimal(str(record.trf_vl_brushwood))).quantize(Decimal("1.00"), ROUND_HALF_UP)
            tmp['trf_vl_waste'] = (Decimal(str(record.trf_vl_waste))).quantize(Decimal("1.00"), ROUND_HALF_UP)
            tmp['trf_vl_total'] = (Decimal(str(record.trf_vl_total))).quantize(Decimal("1.00"), ROUND_HALF_UP)
            wpulp_data.append(tmp)
        return wpulp_data

    def run(self):
        """Импорт данных из БД"""
        general = self.general()
        restatement = self.restatement()
        try:
            Ta_fund.select().where(Ta_fund.offset_uuid == self.uuid)
            wpulp_info = self.wpulp_info()
            wpulp = self.wpulp()
        except Exception as e:
            wpulp_info = None
            wpulp = None
        self.signal_general.emit(general)
        self.signal_restatement.emit(restatement)
        if wpulp_info:
            self.signal_wpulp_info.emit(wpulp_info)
        if wpulp:
            self.signal_wpulp.emit(wpulp)

        # print(self.general())
        # print(self.restatement())
        # print(self.wpulp_info())
        # print(self.wpulp())

