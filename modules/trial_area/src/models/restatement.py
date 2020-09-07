from .database import Database

from peewee import AutoField, UUIDField, IntegerField, ForeignKeyField, FloatField

from .nri import Species, Organization


class BaseModel(Database):
    class Meta:
        schema = "restatement"


class Trees(BaseModel):
    """Хранится записи о деревьях всех перечёток"""
    id_enum = AutoField(null=False, primary_key=True)
    area_uuid = UUIDField(null=False)
    code_species = ForeignKeyField(Species, column_name="code_species", null=False)
    dmr = IntegerField(null=False)
    num_ind = IntegerField()
    num_fuel = IntegerField()
    num_half_ind = IntegerField()


class Areas(BaseModel):
    """Хранятся данные о пробной площади"""
    area_uuid = UUIDField(null=False, primary_key=True)
    gplho = ForeignKeyField(Organization, null=False, column_name='gplho')
    enterprise = ForeignKeyField(Organization, null=False, column_name='enterprise')
    forestry = ForeignKeyField(Organization, null=False, column_name='forestry')
    compartment = IntegerField(null=True)
    sub_compartment = IntegerField(null=True)
    area_square = FloatField()



