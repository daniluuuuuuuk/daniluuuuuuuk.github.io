from .database import Database

from peewee import AutoField, UUIDField, IntegerField, ForeignKeyField, DecimalField
from peewee import FloatField, CharField, DateField, BooleanField

from .nri import Species, Trf_height, Type_for, Kind_use, Gr_forest, Meth_real, Rank_trf
from .nri import Author, Section, Econ, Wct_meth, Acc_meth, Rgn_meth, Status, Bonit


class BaseModel(Database):
    class Meta:
        # schema = 'ta_fund'
        schema = 'mdo'


class Ta_fund_enum(BaseModel):
    id_enum = AutoField(null=False, primary_key=True)
    offset_uuid = UUIDField(null=False)
    code_species = ForeignKeyField(Species, column_name='code_species', null=False)
    dmr = IntegerField(null=False)
    num_ind = IntegerField()
    num_fuel = IntegerField()
    num_biodiversity = IntegerField()


class Ta_fund_wpulp(BaseModel):
    id_enum = AutoField(null=False, primary_key=True)
    offset_uuid = UUIDField(null=False, help_text='UUID лесосеки')
    code_species = ForeignKeyField(Species, column_name='code_species', null=False, help_text='Код породы')
    code_trf_height = ForeignKeyField(Trf_height, column_name='code_trf_height', null=False, help_text='Код разряда высоты породы')

    wpulp_ind_large = DecimalField(help_text='Запас деловой крупной, куб.м.')
    wpulp_ind_medium = DecimalField(help_text='Запас деловой средней, куб.м.')
    wpulp_ind_small = DecimalField(help_text='Запас деловой мелкой, куб.м.')
    wpulp_ind = DecimalField(help_text='Запас деловой, всего, куб.м.')
    wpulp_fuel = DecimalField(help_text='Запас дров, куб.м.')
    wpulp_liquid = DecimalField(help_text='Запас итого ликвида, куб.м.')
    wpulp_crw_lq = DecimalField(help_text='Запас ликвида из кроны, куб.м.')
    wpulp_brushwood = DecimalField(help_text='Запас хвороста, куб.м.')
    wpulp_waste = DecimalField(help_text='Запас отходов, куб.м.')
    wpulp_total = DecimalField(help_text='Запас всей древесины по породе, куб.м.')

    trf_vl_ind = DecimalField(help_text='Таксовая стоимость деловой, руб.')
    trf_vl_fuel = DecimalField(help_text='Таксовая стоимость дровяной, руб.')
    trf_vl_liquid = DecimalField(help_text='Таксовая стоимость ликвида, руб.')
    trf_vl_crw_lq = DecimalField(help_text='Таксовая стоимость ликвида из кроны, руб.')
    trf_vl_brushwood = DecimalField(help_text='Таксовая стоимость хвороста, руб.')
    trf_vl_waste = DecimalField(help_text='Таксовая стоимость отходов, руб.')
    trf_vl_total = DecimalField(help_text='Таксовая стоимость всего по породе, руб.')


class Ta_fund(BaseModel):
    id_enum = AutoField(null=False, primary_key=True)
    offset_uuid = UUIDField(null=False, help_text='UUID лесосеки')
    code_kind_use = ForeignKeyField(Kind_use, column_name='code_kind_use', null=False, help_text='Идентификатор вида пользования')
    code_gr_forest = ForeignKeyField(Gr_forest, column_name='code_gr_forest', null=False, help_text='Идентификатор группы лесов')
    code_meth_real = ForeignKeyField(Meth_real, column_name='code_meth_real', null=False, help_text='Идентификатор метода реализации')
    code_author = ForeignKeyField(Author, column_name='code_author', null=False, help_text='Идентификатор автора (расчет материальной оценки)')
    code_kind_use_for_trf_vl = IntegerField(null=False, help_text='Таксы рубок (Главного - 1, Промежуточного - 2) пользования')
    code_section = ForeignKeyField(Section, column_name='code_section', null=False, help_text='Идентификатор хозсекции')
    code_econ = ForeignKeyField(Econ, column_name='code_econ', null=False, help_text='Группа пород')
    code_wct_meth = ForeignKeyField(Wct_meth, column_name='code_wct_meth', help_text='Вид рубки')
    code_acc_meth = ForeignKeyField(Acc_meth, column_name='code_acc_meth', help_text='Метод учёта')
    code_rgn_meth = ForeignKeyField(Rgn_meth, column_name='code_rgn_meth', help_text='Способ восстановления', null=True)
    code_status = ForeignKeyField(Status, column_name='code_status', help_text='Состав насаждений')
    code_bonit = ForeignKeyField(Bonit, column_name='code_bonit', help_text='Бонитет')
    code_type_for = ForeignKeyField(Type_for, column_name='code_type_for', help_text='Тип леса')
    formula = CharField(null=False, help_text='Состав')
    rank_trf = ForeignKeyField(Rank_trf, column_name='code_rank_trf', null=False, help_text='Идентификатор разряда такс')
    age = IntegerField(null=True, help_text='Возраст')
    density = FloatField(null=True, help_text='Полнота')
    height_avg = IntegerField(null=True, help_text='Высота средняя')
    diameter_avg = IntegerField(null=True, help_text='Диаметр средний')
    date_taxes = DateField(null=False, help_text='Дата оценки запаса')
    date_filled = DateField(null=False, help_text='Дата заполнения МДОЛ')
    year_forest_fund = IntegerField(null=False, help_text='Год лесного фонда')
    year_cutting_area = IntegerField(null=False, help_text='Год отвода')
    year_for_inv = IntegerField(null=True, help_text='Год лесоустройства')
    sign_liquid_crown = BooleanField(null=False, help_text='Признак включения ликвида из кроны в общий запас')
    sign_brushwood = BooleanField(null=False, help_text='Признак включения хвороста в общий запас')
    sign_waste = BooleanField(null=False, help_text='Признак включения отходов в общий запас')
    person_name = CharField(null=True, help_text='ФИО работника')
    description = CharField(null=True, help_text='Доп. информация')
