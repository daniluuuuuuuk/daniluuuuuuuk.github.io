from .database import Database

from peewee import AutoField, TextField, IntegerField, ForeignKeyField, DoubleField, DateField


class BaseModel(Database):
    class Meta:
        schema = 'dictionary'


class Kind_use(BaseModel):
    code_kind_use = AutoField(null=False, primary_key=True)
    name_kind_use = TextField(null=False)


class Econ(BaseModel):
    code_econ = AutoField(null=False, primary_key=True)
    name_econ = TextField(null=False)


class Rank_trf(BaseModel):
    code_rank_trf = AutoField(null=False, primary_key=True)
    name_rank_trf = TextField(null=False)


class Acc_meth_wt(BaseModel):
    code_acc_meth_wt = AutoField(null=False, primary_key=True)
    name_acc_meth_wt = TextField(null=False)
    name_acc_meth_wt_short = TextField(null=False)


class Author(BaseModel):
    code_author = AutoField(null=False, primary_key=True)
    name_author = TextField(null=False)


class Bonit(BaseModel):
    code_bonit = AutoField(null=False, primary_key=True)
    name_bonit = TextField(null=False)


class Condition_reduction(BaseModel):
    code_condition_reduction = AutoField(null=False, primary_key=True)
    name_condition_reduction = TextField(null=False)


class Gr_forest(BaseModel):
    code_gr_forest = AutoField(null=False, primary_key=True)
    name_gr_forest = TextField(null=False)
    name_gr_forest_short = TextField(null=False)


class Kind_timber(BaseModel):
    code_kind_timber = AutoField(null=False, primary_key=True)
    name_kind_timber = TextField(null=False)


class Meth_real(BaseModel):
    code_meth_real = AutoField(null=False, primary_key=True)
    name_meth_real = TextField(null=False)
    name_meth_real_short = TextField(null=True)


class Organization(BaseModel):
    id_organization = AutoField(null=False, primary_key=True)
    parent_id_organization = IntegerField(null=False)
    code_organization = IntegerField(null=False, unique=True)
    type_organization = TextField(null=True)
    name_organization = TextField(null=False)


class Rgn_meth(BaseModel):
    code_rgn_meth = AutoField(null=False, primary_key=True)
    name_rgn_meth = TextField(null=False)


class Status(BaseModel):
    code_status = AutoField(null=False, primary_key=True)
    name_status = TextField(null=False)
    name_status_wood = TextField(null=False)


class Trf_height(BaseModel):
    code_trf_height = AutoField(null=False, primary_key=True)
    name_trf_height = TextField(null=False)


class Type_for(BaseModel):
    code_type_for = AutoField(null=False, primary_key=True)
    name_type_for = TextField(null=False)
    name_type_for_short = TextField(null=False)


class Type_stem(BaseModel):
    code_type_stem = AutoField(null=False, primary_key=True)
    name_type_stem = TextField(null=False)

############################################################################


class Acc_meth(BaseModel):
    code_acc_meth = AutoField(null=False, primary_key=True)
    name_acc_meth = TextField(null=False)
    code_acc_meth_wt = ForeignKeyField(Acc_meth_wt, column_name='code_acc_meth_wt')


class Species(BaseModel):
    code_species = AutoField(null=False, primary_key=True)
    name_species = TextField(null=False)
    name_species_short = TextField(null=False, unique=True)
    name_species_latin = TextField(null=False, unique=True)
    code_econ = ForeignKeyField(Econ, column_name='code_econ')


class Wct_meth(BaseModel):
    code_wct_meth = AutoField(null=False, primary_key=True)
    name_wct_meth = TextField(null=False)
    code_kind_use = ForeignKeyField(Kind_use, column_name='code_kind_use')


class Section(BaseModel):
    code_section = AutoField(null=False, primary_key=True)
    name_section = TextField(null=False)
    code_econ = ForeignKeyField(Econ, column_name='code_econ')

    class Meta:
        primary_key = False


class Species_proxying(BaseModel):
    code_species_original = ForeignKeyField(Species, column_name='code_species_original', null=False)
    code_author_original = ForeignKeyField(Author, column_name='code_author_original', null=False)
    code_species_target = ForeignKeyField(Species, column_name='code_species_target', null=False)
    code_author_target = ForeignKeyField(Author, column_name='code_author_target', null=False)

    class Meta:
        primary_key = False


class Def_wpulp(BaseModel):
    code_wpulp = AutoField(null=False, primary_key=True)
    code_species = ForeignKeyField(Species, column_name='code_species', null=False)
    code_trf_height = ForeignKeyField(Trf_height, column_name='code_trf_height', null=False)
    dmr = IntegerField(null=False)
    code_author = ForeignKeyField(Author, column_name='code_author', null=False)
    code_type_stem = ForeignKeyField(Type_stem, column_name='code_type_stem', null=False)
    code_kind_timber = ForeignKeyField(Kind_timber, column_name='code_kind_timber', null=False)
    wpulp = DoubleField(null=False)


class Def_trf_vl(BaseModel):
    start_date = DateField(null=False)
    code_kind_use = ForeignKeyField(Kind_use, column_name='code_kind_use', null=False)
    code_species = ForeignKeyField(Species, column_name='code_species', null=False)
    code_rank_trf = ForeignKeyField(Rank_trf, column_name='code_rank_trf', null=False)
    code_kind_timber = ForeignKeyField(Kind_timber, column_name='code_kind_timber', null=False)
    taxes = DoubleField(null=False)

    class Meta:
        primary_key = False
