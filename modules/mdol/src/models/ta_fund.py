from .database import Database

from peewee import AutoField, UUIDField, IntegerField, ForeignKeyField

from .nri import Species


class BaseModel(Database):
    class Meta:
        schema = "restatement"


class Trees(BaseModel):
    id_enum = AutoField(null=False, primary_key=True)
    offset_uuid = UUIDField(null=False)
    code_species = ForeignKeyField(Species, column_name="code_species", null=False)
    dmr = IntegerField(null=False)
    num_ind = IntegerField()
    num_fuel = IntegerField()
    num_half_ind = IntegerField()
