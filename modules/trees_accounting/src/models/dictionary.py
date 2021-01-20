"""
Модели справочников
Схема - dictionary
"""

from .database_connection import Connection

from peewee import (
    AutoField,
    TextField,
    IntegerField,
    ForeignKeyField,
    # DoubleField,
    # DateField,
)


class BaseModel(Connection):
    class Meta:
        schema = "dictionary"


class Econ(BaseModel):
    code_econ = AutoField(null=False, primary_key=True)
    name_econ = TextField(null=False)


class Species(BaseModel):
    code_species = AutoField(null=False, primary_key=True)
    name_species = TextField(null=False)
    name_species_short = TextField(null=False, unique=True)
    name_species_latin = TextField(null=False, unique=True)
    code_econ = ForeignKeyField(Econ, column_name="code_econ")


class Organization(BaseModel):
    id_organization = AutoField(null=False, primary_key=True)
    parent_id_organization = IntegerField(null=False)
    code_organization = IntegerField(null=False, unique=True)
    type_organization = TextField(null=True)
    name_organization = TextField(null=False)

    @classmethod
    def convert_org_id(self, id_forestry: int, id_forestry_enterprise: int) -> dict:
        """
        Преобразовываю код лесхоза и код лесничества
        из картографии в словарь названия организаций и его кода
        """
        if id_forestry < 10:
            id_forestry = "0" + str(id_forestry)
        else:
            id_forestry = str(id_forestry)

        if id_forestry_enterprise < 100:
            if id_forestry_enterprise < 10:
                id_forestry_enterprise = "0" + str(id_forestry_enterprise)
            id_forestry_enterprise = "0" + str(id_forestry_enterprise)
        else:
            id_forestry_enterprise = str(id_forestry_enterprise)

        org_ending = id_forestry_enterprise + id_forestry
        id_organizations = self.select(self.code_organization).where(
            self.type_organization.is_null()
        )

        for id in id_organizations:
            if str(id.code_organization)[5:] == org_ending:
                forestry_row = (
                    self.select()
                    .where(self.code_organization == id.code_organization)
                    .get()
                )
                forestry_code = forestry_row.code_organization
                forestry_name = forestry_row.name_organization

                forestry_enterprise = (
                    self.select()
                    .where(self.id_organization == forestry_row.parent_id_organization)
                    .get()
                )
                forestry_enterprise_code = forestry_enterprise.code_organization
                forestry_enterprise_name = forestry_enterprise.name_organization

                gplho = (
                    self.select()
                    .where(
                        self.id_organization
                        == forestry_enterprise.parent_id_organization
                    )
                    .get()
                )
                gplho_code = gplho.code_organization
                gplho_name = gplho.name_organization

                return {
                    gplho_code: gplho_name,
                    forestry_enterprise_code: forestry_enterprise_name,
                    forestry_code: forestry_name,
                }
        return {
            "1500100000": "МЛХ",
            "1500100000": "МЛХ",
            "1500100000": "МЛХ",
        }  # Совпадений не найдено
