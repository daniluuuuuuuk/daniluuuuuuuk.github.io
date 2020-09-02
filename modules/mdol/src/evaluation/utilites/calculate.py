from PyQt5 import QtCore
from decimal import Decimal, ROUND_HALF_UP
import datetime
import traceback

from ....src.models.nri import *
from ....src.models.ta_fund import *


class Export_data(QtCore.QThread):
    signal_status_bar = QtCore.pyqtSignal(int)
    signal_data_by_spc = QtCore.pyqtSignal(list)
    signal_data_total = QtCore.pyqtSignal(dict)
    signal_whip = QtCore.pyqtSignal(float)

    def __init__(self, **args):
        QtCore.QThread.__init__(self)
        self.uuid = args['uuid']
        self.attributes = args['attributes']
        self.rest_data = {}
        self.data_all_spc = []
        self.default_row = {
            'code_species': 0,  # Код породы
            'name_species': 0,  # Название породы
            'code_species_proxying': 0,  # Название породы
            'code_trf_height': 0,  # Разряд высот
            'code_author': 0,  # Таблицы по которым расчитывается объём
            'wpulp_ind_large': 0,  # Запас деловой крупной древесины
            'wpulp_ind_medium': 0,  # Запас деловой средней древесины
            'wpulp_ind_small': 0,  # Запас деловой мелкой древесины
            'wpulp_ind': 0,  # Запас деловой древесины
            'wpulp_fuel': 0,  # Запас дровяной
            'wpulp_liquid': 0,  # Итого ликвида
            'wpulp_crw_lq': 0,  # Запас ликвида из кроны
            'wpulp_brushwood': 0,  # Запас хвороста
            'wpulp_waste': 0,  # Запас отходов
            'wpulp_total': 0,  # Всего
            'trf_vl_ind': 0,  # Стоимость деловой
            'trf_vl_fuel': 0,  # Стоимость дров
            'trf_vl_liquid': 0,  # Стоимость итого ликвида
            'trf_vl_crw_lq': 0,  # Стоимость ликвида из кроны
            'trf_vl_brushwood': 0,  # Стоимость хвороста
            'trf_vl_waste': 0,  # Стоимость отходов
            'trf_vl_total': 0,  # Всего
        }

        self.get_data_from_db()

    def get_data_from_db(self):
        """
        Получаю данные о деревьях (перечётку) с БД
        """
        for record in Ta_fund_enum.select().where(Ta_fund_enum.offset_uuid == self.uuid):
            species = Species.select().where(Species.code_species == record.code_species).get().code_species
            if record.num_ind > 0 or record.num_fuel > 0:
                if species not in list(self.rest_data.keys()):
                    self.rest_data[species] = []
                self.rest_data[species].append(
                    {
                        'dmr': record.dmr,
                        'wpulp_ind': record.num_ind,
                        'wpulp_fuel': record.num_fuel
                    }
                )

    def calc_wpulp(self):
        for spc in self.rest_data:
            self.signal_status_bar.emit(int(100 / len(self.rest_data)))
            one_spc_data = self.default_row.copy()
            one_spc_data['code_species'] = int(str(spc))
            one_spc_data['code_trf_height'] = self.attributes['system']['species_trf_height'][spc]
            for rec in self.rest_data[spc]:
                rec['wpulp_ind'] = float(rec['wpulp_ind'])
                rec['wpulp_fuel'] = float(rec['wpulp_fuel'])

                check_wpulp = self.check_wpulp(code_species=one_spc_data['code_species'],
                                               code_trf_height=one_spc_data['code_trf_height'],
                                               dmr=rec['dmr'],
                                               code_author=self.attributes['ta_fund']['code_author'])
                rec['dmr'] = check_wpulp[0]
                one_spc_data['code_species_proxying'] = int(str(check_wpulp[1]))
                one_spc_data['code_author'] = int(str(check_wpulp[2]))
                one_spc_data['name_species'] = Species.get(Species.code_species == int(str(spc))).name_species

                """Считаю объёмы"""
                for wpulp in Def_wpulp.select().where(Def_wpulp.code_species == one_spc_data['code_species_proxying'],
                                                      Def_wpulp.code_trf_height == one_spc_data['code_trf_height'],
                                                      Def_wpulp.dmr == rec['dmr'],
                                                      Def_wpulp.code_author == one_spc_data['code_author']):
                    size = float(wpulp.wpulp)
                    if str(wpulp.code_kind_timber) == '2':  # если wpulp для деловой мелкой
                        one_spc_data['wpulp_ind_large'] += (Decimal(str(rec['wpulp_ind'])) * Decimal(str(size))).quantize(Decimal("1.00"), ROUND_HALF_UP)
                        one_spc_data['wpulp_fuel'] += (Decimal(str(rec['wpulp_fuel'])) * Decimal(str(size))).quantize(Decimal("1.00"), ROUND_HALF_UP)  # снимаю дрова
                    if str(wpulp.code_kind_timber) == '3':  # если wpulp для деловой средней
                        one_spc_data['wpulp_ind_medium'] += (Decimal(str(rec['wpulp_ind'])) * Decimal(str(size))).quantize(Decimal("1.00"), ROUND_HALF_UP)
                        one_spc_data['wpulp_fuel'] += (Decimal(str(rec['wpulp_fuel'])) * Decimal(str(size))).quantize(Decimal("1.00"), ROUND_HALF_UP)  # снимаю дрова
                    if str(wpulp.code_kind_timber) == '4':  # если wpulp для деловой крупной
                        one_spc_data['wpulp_ind_small'] += (Decimal(str(rec['wpulp_ind'])) * Decimal(str(size))).quantize(Decimal("1.00"), ROUND_HALF_UP)
                        one_spc_data['wpulp_fuel'] += (Decimal(str(rec['wpulp_fuel'])) * Decimal(str(size))).quantize(Decimal("1.00"), ROUND_HALF_UP)  # снимаю дрова
                    if str(wpulp.code_kind_timber) == '5':  # если wpulp для дровяной
                        one_spc_data['wpulp_fuel'] += (Decimal(str(rec['wpulp_ind'])) * Decimal(str(size))).quantize(Decimal("1.00"), ROUND_HALF_UP)
                        one_spc_data['wpulp_fuel'] += (Decimal(str(rec['wpulp_fuel'])) * Decimal(str(size))).quantize(Decimal("1.00"), ROUND_HALF_UP)
                    if str(wpulp.code_kind_timber) == '6':  # отходы (только с деловой)
                        one_spc_data['wpulp_fuel'] += (Decimal(str(rec['wpulp_fuel'])) * Decimal(str(size))).quantize(Decimal("1.00"), ROUND_HALF_UP)
                        one_spc_data['wpulp_waste'] += (Decimal(str(rec['wpulp_ind'])) * Decimal(str(size))).quantize(Decimal("1.00"), ROUND_HALF_UP)
                    if str(wpulp.code_kind_timber) == '7':  # Отходы
                        #  Считается по другому: Сначала складываем колличество деловых и дровяных, потом умножаем на объём древесной массы, округляем до сотых и суммируем к прошлым диаметрам
                        one_spc_data['wpulp_crw_lq'] += (Decimal(str(size)) * (Decimal(rec['wpulp_ind'] + rec['wpulp_fuel']))).quantize(Decimal("1.00"), ROUND_HALF_UP)
                    if str(wpulp.code_kind_timber) == '9':  # хворост
                        #  Считается по другому: Сначала складываем колличество деловых и дровяных, потом умножаем на объём древесной массы, округляем до сотых и суммируем к прошлым диаметрам
                        one_spc_data['wpulp_brushwood'] += (Decimal(str(size)) * (Decimal(rec['wpulp_ind'] + rec['wpulp_fuel']))).quantize(Decimal("1.00"), ROUND_HALF_UP)

            """Считаю стоимость"""
            # Считаю Деловую крупную
            # Вибрайю самую свежую дату где имеються данные
            dates = [datetime.date(2030, 12, 31)]
            for trf_vl in Def_trf_vl.select().where(Def_trf_vl.code_kind_timber == 5,
                                                    Def_trf_vl.code_kind_use == self.attributes['ta_fund']['code_kind_use_for_trf_vl'],
                                                    Def_trf_vl.code_species == one_spc_data['code_species_proxying'],
                                                    Def_trf_vl.code_rank_trf == self.attributes['ta_fund']['code_rank_trf']):
                dates.append((trf_vl.start_date))
            dates = sorted(dates)
            #  Выбираю последнюю дату такс для породы
            for i in range(len(dates)):
                if dates[i + 1] >= self.attributes['ta_fund']['date_taxes'] >= dates[i]:
                    self.attributes['system']['start_date'] = dates[i]
                    break
            #  Для породы считаю цену
            if self.attributes['ta_fund']['code_meth_real'] != 11:  # Если нет реализации, то не считаем
                for trf_vl in Def_trf_vl.select().where(Def_trf_vl.start_date == self.attributes['system']['start_date'],
                                                        Def_trf_vl.code_kind_use == self.attributes['ta_fund']['code_kind_use_for_trf_vl'],
                                                        Def_trf_vl.code_species == one_spc_data['code_species_proxying'],
                                                        Def_trf_vl.code_rank_trf == self.attributes['ta_fund']['code_rank_trf']):
                    if str(trf_vl.code_kind_timber) == '2':
                        one_spc_data['trf_vl_ind'] += (one_spc_data['wpulp_ind_large'] * Decimal(str(trf_vl.taxes))).quantize(Decimal("1.00"), ROUND_HALF_UP)
                    if str(trf_vl.code_kind_timber) == '3':
                        one_spc_data['trf_vl_ind'] += (one_spc_data['wpulp_ind_medium'] * Decimal(str(trf_vl.taxes))).quantize(Decimal("1.00"), ROUND_HALF_UP)
                    if str(trf_vl.code_kind_timber) == '4':
                        one_spc_data['trf_vl_ind'] += (one_spc_data['wpulp_ind_small'] * Decimal(str(trf_vl.taxes))).quantize(Decimal("1.00"), ROUND_HALF_UP)
                    if str(trf_vl.code_kind_timber) == '5':
                        one_spc_data['trf_vl_fuel'] += (one_spc_data['wpulp_fuel'] * Decimal(str(trf_vl.taxes))).quantize(Decimal("1.00"), ROUND_HALF_UP)
                    if str(trf_vl.code_kind_timber) == '6':  # Отходы
                        one_spc_data['trf_vl_waste'] += (one_spc_data['wpulp_waste'] * Decimal(str(trf_vl.taxes))).quantize(Decimal("1.00"), ROUND_HALF_UP)
                    if str(trf_vl.code_kind_timber) == '7':
                        one_spc_data['trf_vl_crw_lq'] += (one_spc_data['wpulp_crw_lq'] * Decimal(str(trf_vl.taxes))).quantize(Decimal("1.00"), ROUND_HALF_UP)
                    if str(trf_vl.code_kind_timber) == '9':  # Хворост
                        one_spc_data['trf_vl_brushwood'] += (one_spc_data['wpulp_brushwood'] * Decimal(str(trf_vl.taxes))).quantize(Decimal("1.00"), ROUND_HALF_UP)
            """"""

            """Считаю суммы для Итого по породе"""
            one_spc_data['wpulp_ind'] = (Decimal(str(one_spc_data['wpulp_ind_large'])) + Decimal(str(one_spc_data['wpulp_ind_medium'])) + Decimal(str(one_spc_data['wpulp_ind_small']))).quantize(Decimal("1.00"), ROUND_HALF_UP)
            one_spc_data['wpulp_liquid'] = (Decimal(str(one_spc_data['wpulp_fuel'])) + Decimal(str(one_spc_data['wpulp_ind']))).quantize(Decimal("1.00"), ROUND_HALF_UP)
            one_spc_data['trf_vl_liquid'] = (Decimal(str(one_spc_data['trf_vl_fuel'])) + Decimal(str(one_spc_data['trf_vl_ind']))).quantize(Decimal("1.00"), ROUND_HALF_UP)

            if self.attributes['ta_fund']['sign_liquid_crown']:
                one_spc_data['wpulp_total'] += one_spc_data['wpulp_crw_lq']
                one_spc_data['trf_vl_total'] += one_spc_data['trf_vl_crw_lq']
            if self.attributes['ta_fund']['sign_brushwood']:
                one_spc_data['wpulp_total'] += one_spc_data['wpulp_brushwood']
                one_spc_data['trf_vl_total'] += one_spc_data['trf_vl_brushwood']
            if self.attributes['ta_fund']['sign_waste']:
                one_spc_data['wpulp_total'] += one_spc_data['wpulp_waste']
                one_spc_data['trf_vl_total'] += one_spc_data['trf_vl_waste']

            one_spc_data['wpulp_total'] += one_spc_data['wpulp_liquid']
            one_spc_data['trf_vl_total'] += one_spc_data['trf_vl_liquid']

            self.data_all_spc.append(one_spc_data)

        self.data_all_spc = sorted(self.data_all_spc, key=lambda x: x['name_species'])
        self.signal_data_by_spc.emit(self.data_all_spc)
        return self.data_all_spc
        # self.calculate_total(self.data_all_spc)  # отправляю данные на подчёт Итого

    def run(self):
        try:
            self.calc_wpulp()
        except Exception as error:
            print('Ошибка записи в БД. Данные не сохранены.', str(error), str(traceback.format_exc()))

    def check_wpulp(self, code_species, code_trf_height, dmr, code_author):
        """Проверяю существует ли объём для текущих данных"""
        try:
            Def_wpulp.select().where(Def_wpulp.code_species == code_species,
                                     Def_wpulp.code_author == code_author).get()
            code_author = self.attributes['ta_fund']['code_author']

        except:
            code_species = Species_proxying.select().where(Species_proxying.code_author_original == code_author,
                                                           Species_proxying.code_species_original == code_species
                                                           ).get().code_species_target
            code_author = Species_proxying.select().where(Species_proxying.code_author_original == code_author,
                                                          Species_proxying.code_species_original == code_species
                                                          ).get().code_author_target
        """Если для указанного диаметра меньше минимального объёма в def_wpulp, то берём минимальный диаметр,
        Если больше максимального - то берём максимальный"""
        tmp = []
        for u in Def_wpulp.select().where(Def_wpulp.code_species == code_species, Def_wpulp.code_trf_height == code_trf_height, Def_wpulp.code_author == code_author):
            if u.dmr not in tmp:
                tmp.append(u.dmr)
        tmp.sort(reverse=True)

        if dmr not in tmp:
            if dmr < tmp[-1]:
                return tmp[-1], code_species, code_author
            if dmr > tmp[0]:
                return tmp[0], code_species, code_author
        else:
            return dmr, code_species, code_author

    # def calculate_total(self, data_all_spc):
    #     self.total = self.default_row.copy()
    #     self.total.pop('code_species')
    #     self.total.pop('code_species_proxying')
    #     self.total.pop('code_author')
    #     self.total.pop('code_trf_height')
    #     k = list(self.total.keys())
    #     for u in k:
    #         for i in data_all_spc:
    #             self.total[u] += i[u]
    #     self.signal_data_total.emit(self.total)
    #     if self.attributes['calculate_whip']:
    #         self.calculate_whip(self.total)

    def calculate_whip(self, total):
        """Расчёт среднего объёма хлыста"""
        whip = (total['wpulp_liquid'] + total['wpulp_waste']) / self.attributes['amount_trees']
        self.signal_whip.emit(whip)
