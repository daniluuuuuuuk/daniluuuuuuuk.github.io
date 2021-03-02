"""
Модели перечёта
Схема - dictionary
"""

from datetime import date

from peewee import (
    TextField,
    IntegerField,
    CharField,
    DecimalField,
    AutoField,
    UUIDField,
    ForeignKeyField,
)

from .database_connection import Connection
from .dictionary import Species, TrfHeight, KindSeeds


class BaseModel(Connection):
    class Meta:
        schema = "public"


class Area(BaseModel):
    geom = TextField(column_name="geom", null=False)
    uuid = CharField(column_name="uid")
    num_forestry = IntegerField(column_name="num_lch", help_text="Номер лесничества")
    compartment = CharField(column_name="num_kv", help_text="Номер квартала")
    sub_compartment = CharField(column_name="num_vds", help_text="Номер выдела")
    area = DecimalField(column_name="area", help_text="Экспл. площадь")
    num_enterprise = IntegerField(column_name="leshos", help_text="Номер лесхоза")
    num_cutting_area = CharField(column_name="num", help_text="Номер лесосеки")
    use_type = CharField(column_name="usetype", help_text="Тип пользования")
    cutting_type = CharField(column_name="cuttingtyp", help_text="Тип рубки")
    person_name = CharField(column_name="fio", help_text="ФИО работника")
    date_trial = CharField(
        column_name="date",
        help_text="Дата отвода",
        default=date.today().strftime("%d.%m.%Y"),
    )
    description = CharField(column_name="info", help_text="Доп. информация")
    leshos_text = CharField(column_name="leshos_text")
    lesnich_text = CharField(column_name="lesnich_text")

    def __str__(self):
        return self.uuid

    class Meta:
        primary_key = False
        table_name = "area"


class Trees(BaseModel):
    """Хранится записи о деревьях всех перечёток"""

    id_enum = AutoField(null=False, primary_key=True)
    area_uuid = UUIDField(null=False)
    code_species = ForeignKeyField(Species, column_name="code_species", null=False)
    dmr = IntegerField(null=False)
    num_ind = IntegerField()
    num_fuel = IntegerField()


class TreesNotCuttingModel(BaseModel):
    area_uuid = UUIDField(null=False)
    code_species = ForeignKeyField(Species, column_name="code_species", null=False)
    seed_type_code = ForeignKeyField(
        KindSeeds, column_name="seed_type_code", null=False
    )
    seed_dmr = IntegerField(null=False)
    seed_count = IntegerField(null=False)
    seed_number = TextField(null=True)

    class Meta:
        table_name = "trees_not_cutting"


class TreesTrfHeight(BaseModel):
    area_uuid = CharField(column_name="area_uuid")
    code_species = ForeignKeyField(Species, column_name="code_species")
    code_trf_height = ForeignKeyField(TrfHeight, column_name="code_trf_height")

    def __str__(self):
        return f"{self.area_uuid}__{self.code_species}"

    class Meta:
        table_name = "trees_trf_height"
