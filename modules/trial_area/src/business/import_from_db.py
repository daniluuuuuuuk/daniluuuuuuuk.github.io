import time
from PyQt5 import QtCore
from ..models.nri import Species, Organization
from ..models.restatement import Trees
from ..models.public import Area


class Data(QtCore.QThread):
    signal_output_data = QtCore.pyqtSignal(dict)
    signal_att_data = QtCore.pyqtSignal(dict)
    siganl_calculate_amount = QtCore.pyqtSignal(bool)

    def __init__(self, **args):
        QtCore.QThread.__init__(self)
        self.uuid = args['uuid']

    def get_att_area_data(self):
        """Получаю аттрибутивные данные для пробной площади"""
        area = Area.select().where(Area.uuid == self.uuid).get()
        gplho, forestry_enterprise, forestry = self.pars_org_id(id_forestry=area.num_forestry, id_forestry_enterprise=area.num_enterprise)

        att_data = {
            "area_uuid": area.uuid,
            "gplho": gplho,
            "enterprise": forestry_enterprise,
            "forestry": forestry,
            "compartment": str(area.compartment),
            "sub_compartment": str(area.sub_compartment),
            "area_square": str(area.area)
        }
        return att_data

    def pars_org_id(self, id_forestry: int, id_forestry_enterprise: int):
        """Преобразую код лесхоза и код лесничества в названия организаций"""
        if id_forestry < 10:
            id_forestry = '0'+str(id_forestry)
        else:
            id_forestry = str(id_forestry)

        if id_forestry_enterprise < 100:
            if id_forestry_enterprise < 10:
                id_forestry_enterprise = '0'+str(id_forestry_enterprise)
            id_forestry_enterprise = '0' + str(id_forestry_enterprise)
        else:
            id_forestry_enterprise = str(id_forestry_enterprise)

        org_ending = id_forestry_enterprise+id_forestry
        id_organizations = Organization.select(Organization.code_organization).where(Organization.type_organization.is_null())

        for id in id_organizations:
            if str(id.code_organization)[5:] == org_ending:
                forestry_row = Organization.select().where(Organization.code_organization == id.code_organization).get()
                forestry_name = forestry_row.name_organization
                forestry_enterprise_row = Organization.select().where(Organization.id_organization == forestry_row.parent_id_organization).get()
                forestry_enterprise_name = forestry_enterprise_row.name_organization
                gplho_name = Organization.select().where(Organization.id_organization == forestry_enterprise_row.parent_id_organization).get().name_organization

                return gplho_name, forestry_enterprise_name, forestry_name
        return 'МЛХ', 'МЛХ', 'МЛХ'  # Совпадений не найдено

    def run(self):
        self.signal_att_data.emit(self.get_att_area_data())
        for record in Trees.select().where(Trees.area_uuid == self.uuid):
            species = Species.select().where(Species.code_species == record.code_species).get().name_species_latin
            output_data = {
                'species': species,
                'dmr': record.dmr,
                'num_ind': record.num_ind,
                'num_fuel': record.num_fuel,
                'num_half_ind': record.num_half_ind,
                'device_sign': 'db'
            }
            self.signal_output_data.emit(output_data)
            time.sleep(.001)
        self.siganl_calculate_amount.emit(1)  # отправляю сигнал на подсчёт суммы

