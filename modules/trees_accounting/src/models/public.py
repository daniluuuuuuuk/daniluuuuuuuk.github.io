from datetime import date

from peewee import TextField, IntegerField, CharField, DecimalField

from .database import Database


class BaseModel(Database):
    class Meta:
        schema = "public"


class Area(BaseModel):
    geom = TextField(column_name="geom", null=False)
    uuid = CharField(column_name="uid")
    num_forestry = IntegerField(column_name="num_lch", help_text="Номер лесничества")
    compartment = CharField(column_name="num_kv", help_text="Номер квартала")
    sub_compartment = CharField(column_name="num_vd", help_text="Номер выдела")
    area = DecimalField(column_name="area", help_text="Экспл. площадь")
    num_enterprise = IntegerField(column_name="leshos", help_text="Номер лесхоза")
    num_cutting_area = CharField(column_name="num", help_text="Номер лесосеки")
    use_type = CharField(column_name="usetype", help_text="Тип пользования")
    cutting_type = CharField(column_name="cuttingtyp", help_text="Тип рубки")
    num_plot = CharField(column_name="plot", help_text="Делянка")
    person_name = CharField(column_name="fio", help_text="ФИО работника")
    date_trial = CharField(
        column_name="date",
        help_text="Дата отвода",
        default=date.today().strftime("%d.%m.%Y"),
    )
    description = CharField(column_name="info", help_text="Доп. информация")
    num_vds = CharField(column_name="num_vds")
    leshos_text = CharField(column_name="leshos_text")
    lesnich_text = CharField(column_name="lesnich_text")

    class Meta:
        primary_key = False
        table_name = "area"
