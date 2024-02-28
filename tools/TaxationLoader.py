"""Классы для загрузки таксационных показателей из базы данных.
Основные таблицы таксационного описания: subcompartments_taxation,
subcompartments_taxation_m10
"""

from .. import PostgisDB
from qgis.core import *
from PyQt5 import QtCore
from . import config
from psycopg2 import ProgrammingError

MESSAGE_CATEGORY = "Taxation Loader Task"


class Worker(QtCore.QObject):
    def __init__(self, feature):
        QtCore.QObject.__init__(self)
        self.killed = False
        self.feature = feature
        self.identity = int(self.generateIdentity(feature))
        self.forestcode = int(feature["forestcode"])
        self.lhCode = str(int(float(feature["code_lh"])))
        self.loader = Loader("Load Taxation Info")

    def getLhCode(self):
        cf = config.Configurer("enterprise")
        settings = cf.readConfigs()
        return str(int(float(settings.get("code_lh"))))

    def generateIdentity(self, feature):
        self.num_lhz = int(feature["num_lhz"])
        self.num_lch = int(feature["num_lch"])
        self.num_kv = int(feature["num_kv"])
        self.num_vd = int(feature["num_vd"])
        return (
            (1000000000 * self.num_lhz)
            + (10000000 * self.num_lch)
            + (1000 * self.num_kv)
            + self.num_vd
        )

    def run(self):
        ret = None
        try:
            self.loader.run(
                self.identity, self.num_lhz, self.num_lch, self.lhCode, self.forestcode
            )
            self.loader.waitForFinished()
            ret = {
                "Лесхоз": self.loader.lh_name,
                "Лесничество": self.loader.lch_name,
                "Квартал": self.num_kv,
                "Выдел": self.num_vd,
                "Площадь": float(self.loader.area),
                **self.loader.taxDetails,
            }
            ret["m10"] = self.loader.taxDetailsM10
            ret["undergrowth_data"] = self.loader.undergrowth_data
            ret["underwood_data"] = self.loader.underwood_data
            # ret["additional_data"] = {**self.loader.forest_cultures, **self.loader.tapping, **self.loader.red_book_plants_animals, **self.loader.selection_features, **self.loader.completed_economic_events}
            # ret["additional_data"] = self.loader.forest_cultures + self.loader.tapping + self.loader.red_book_plants_animals + self.loader.selection_features + self.loader.completed_economic_events
            ret["additional_data"] = self.loader.united_add_data_list
            ret["forest_cultures"] = self.loader.forest_cultures
            ret["tapping"] = self.loader.tapping
            ret["red_book_plants_animals"] = self.loader.red_book_plants_animals
            ret["selection_features"] = self.loader.selection_features
            ret["completed_economic_events"] = self.loader.completed_economic_events
        except Exception as e:
            raise e
        self.finished.emit(ret)

    def kill(self):
        self.killed = True

    finished = QtCore.pyqtSignal(object)


class Loader(QgsTask):
    def __init__(self, description):
        super().__init__(description, QgsTask.CanCancel)

        self.taxDetailsM10 = None
        self.undergrowth_data = None
        self.underwood_data = None
        self.forest_cultures = None
        self.tapping = None
        self.red_book_plants_animals = None
        self.selection_features = None
        self.completed_economic_events = None
        self.united_add_data_list = None
        self.lh_name = None
        self.lch_name = None
        self.lhCode = None
        self.area = None

        self.total = 0
        self.iterations = 0
        self.exception = None

    def run(self, identity, lh, lch, lh_type, forestcode):
        QgsMessageLog.logMessage(
            '\nStarted task "{}"'.format(self.description()),
            MESSAGE_CATEGORY,
            Qgis.Info,
        )
        self.loadTaxation(identity, lh, lch, lh_type, forestcode)
        return True

    def loadTaxation(self, identity, lh, lch, lhCode, forestcode):
        if lch < 10:
            num_lch = "0" + str(lch)
        else:
            num_lch = str(lch)

        postgisConnection = PostgisDB.PostGisDB()

        self.lh_name = postgisConnection.getQueryResult(
            """select name_organization 
                from "dictionary".organization
                where code_organization = '{}'""".format(
                lhCode
            )
        )[0][0]

        self.lch_name = postgisConnection.getQueryResult(
            """select name_organization from (select id_organization from "dictionary".organization
                where code_organization = '{}') typed
                join "dictionary".organization org on org.parent_id_organization = typed.id_organization
                where substring(code_organization::varchar(255) from 9 for 2) = '{}'""".format(
                lhCode, num_lch
            )
        )[0][0]
        # try:
            # sql_main_tax_description = """select 
            #     st.bon as "Бонитет",
            #     st.tl as "Тип леса",
            #     st.tum as "ТУМ",
            #     st.ptg as "ПТГ",
            #     ds.name as "Проект. порода",
            #     ds_2."name" as "Главная порода",
            #     concat_ws(', ', x1.name_xmer, x2.name_xmer, x3.name_xmer) AS "Хоз. мероприятия"
            # from public.subcompartment_taxation st 
            #     left join "dictionary".dict_species ds on st.por_m2 = ds.class_code_por
            #     left join "dictionary".dict_species ds_2 on st.por_m3 = ds_2.class_code_por
            #     left join "dictionary".xmer x1 on st.xmer1 = x1.code_xmer 
            #     left join "dictionary".xmer x2 on st.xmer2 = x2.code_xmer 
            #     left join "dictionary".xmer x3 on st.xmer3 = x3.code_xmer
            #         where st.identity = '{}'""".format(
            #     int(identity)
            # )
        sql_main_tax_description = """select 
                forest_categories.description as "Категория лесов",
                sc.protection_areas as "ОРЛ",
                land_types.description as "Вид земель",
                ds.name as "Порода",
                sc.bonitet as "Бонитет",
                sc.forest_type as "Тип леса",
                sc.forest_growing_cond_type as "ТУМ",
                sc.soil_typological_groups as "ПТГ",
                concat_ws(', ', x1.name_xmer, sc.cutting_percent) AS "Хоз. мероприятие",
                x2.name_xmer as "Хоз. мероприятие 2",
                concat_ws('. ', first_forest_categories.description, second_forest_categories.description, third_forest_categories.description) AS "Другие категории",
                economic_impact.availability_sign as "Доступность"
            from public.subcompartment_characteristics sc 
                left join "dictionary".forest_categories forest_categories on sc.protection_category = forest_categories.code
                left join "dictionary".land_types land_types on sc.land_type = land_types.code
                left join "dictionary".dict_species ds on sc.dominant_species = ds.class_code_por
                left join "dictionary".xmer x1 on sc.first_economic_event = x1.code_xmer
                left join "dictionary".xmer x2 on sc.second_economic_event = x2.code_xmer
                left join public.economic_impact_accessibility economic_impact on sc.id = economic_impact.subcompartment_characteristics_id
                left join public.other_forests_subcategories other_forests_subcategories on sc.id = other_forests_subcategories.subcompartment_characteristics_id
                left join "dictionary".forest_categories first_forest_categories on other_forests_subcategories.first_forest_subcategory = first_forest_categories.code
                left join "dictionary".forest_categories second_forest_categories on other_forests_subcategories.second_forest_subcategory = second_forest_categories.code
                left join "dictionary".forest_categories third_forest_categories on other_forests_subcategories.third_forest_subcategory = third_forest_categories.code
                    where sc.id = '{}'""".format(
                int(forestcode)
            )
        self.taxDetails = postgisConnection.getQueryResult(
            sql_main_tax_description, as_dict=True
        )[0]

        # except ProgrammingError:
        #     sql_main_tax_description = """select 
        #         st.bon as "бонитет",
        #         st.tl as "Тип леса",
        #         st.tum as "ТУМ"
        #     from public.subcompartment_taxation st 
        #         where st.identity = '{}'""".format(
        #         int(identity)
        #     )
        #     self.taxDetails = postgisConnection.getQueryResult(
        #         sql_main_tax_description, as_dict=True
        #     )[0]
        # finally:
        #     self.taxDetail = {}

        for k, v in list(self.taxDetails.items()):  # Чистка от NULL
            if v is None or v == "":
                del self.taxDetails[k]

        try:
            self.area = postgisConnection.getQueryResult(
                """select areadoc from "public".subcompartments where identity = '{}'""".format(
                    int(identity)
                )
            )[0][0]
        except IndexError:
            None

        self.taxDetailsM10 = postgisConnection.getQueryResult(
            """select
                    taxation_characteristics.order_number,
                    taxation_characteristics.layer,
                    taxation_characteristics.structure_coeff,
                    dict_species.name,
                    taxation_characteristics.age, 
                    taxation_characteristics.height, 
                    taxation_characteristics.diameter, 
                    taxation_characteristics.fullness, 
                    taxation_characteristics.layer_stock 
                from "public".taxation_characteristics taxation_characteristics
                left join "dictionary".dict_species dict_species on taxation_characteristics.wood_species = dict_species.class_code_por
                where subcompartment_characteristics_id = '{}'""".format(
                int(forestcode)
            )
        )
        # self.taxDetailsM10 = postgisConnection.getQueryResult(
        #     """select identity, formula, dmr, proish, poln, height, age, yarus, zapas from "public".subcompartment_taxation_m10 where identity = '{}'""".format(
        #         int(identity)
        #     )
        # )
        if len(self.taxDetailsM10) > 0:
            for i in range(len(self.taxDetailsM10)):
                self.taxDetailsM10[i] = [
                    "" if v is None else v for v in self.taxDetailsM10[i]
                ]
                self.taxDetailsM10[i] = {
                    "order_number": self.taxDetailsM10[i][0],
                    "layer": self.taxDetailsM10[i][1],
                    "structure_coeff": self.taxDetailsM10[i][2],
                    "wood_species": self.taxDetailsM10[i][3],
                    "age": self.taxDetailsM10[i][4],
                    "height": str(self.taxDetailsM10[i][5]),
                    "diameter": str(self.taxDetailsM10[i][6]),
                    "fullness": self.taxDetailsM10[i][7],
                    "layer_stock": self.taxDetailsM10[i][8],
                }

        # postgisConnection.__del__()
        
        self.undergrowth_data = postgisConnection.getQueryResult(
            """select
                    concat_ws('', undergrowth.first_coefficient, first_dict_species.shifr_por, undergrowth.second_coefficient, second_dict_species.shifr_por, undergrowth.third_coefficient, third_dict_species.shifr_por),
                    undergrowth.age,
                    undergrowth.height,
                    undergrowth.amount,
                    undergrowth.undergrowth_grade
                from "public".undergrowth undergrowth
                left join "dictionary".dict_species first_dict_species on undergrowth.first_species = first_dict_species.class_code_por
                left join "dictionary".dict_species second_dict_species on undergrowth.second_species = second_dict_species.class_code_por
                left join "dictionary".dict_species third_dict_species on undergrowth.third_species = third_dict_species.class_code_por
                where subcompartment_characteristics_id = '{}'""".format(
                int(forestcode)
            )
        )

        if len(self.undergrowth_data) > 0:
            for i in range(len(self.undergrowth_data)):
                self.undergrowth_data[i] = [
                    "" if v is None else v for v in self.undergrowth_data[i]
                ]
                self.undergrowth_data[i] = {
                    "structure": str(self.undergrowth_data[i][0]),
                    "age": self.undergrowth_data[i][1],
                    "height": str(self.undergrowth_data[i][2]),
                    "amount": str(self.undergrowth_data[i][3]),
                    "undergrowth_grade": self.undergrowth_data[i][4]
                }

                
        self.underwood_data = postgisConnection.getQueryResult(
            """select
                    underwood.density_degree,
                    concat_ws(', ', first_dict_species.shifr_por, second_dict_species.shifr_por, third_dict_species.shifr_por)
                from "public".underwood underwood
                left join "dictionary".dict_species first_dict_species on underwood.first_species = first_dict_species.class_code_por
                left join "dictionary".dict_species second_dict_species on underwood.second_species = second_dict_species.class_code_por
                left join "dictionary".dict_species third_dict_species on underwood.third_species = third_dict_species.class_code_por
                where subcompartment_characteristics_id = '{}'""".format(
                int(forestcode)
            )
        )

        if len(self.underwood_data) > 0:
            for i in range(len(self.underwood_data)):
                self.underwood_data[i] = [
                    "" if v is None else v for v in self.underwood_data[i]
                ]
                self.underwood_data[i] = {
                    "density_degree": str(self.underwood_data[i][0]),
                    "species_list": str(self.underwood_data[i][1])
                }

        # self.additional_info = postgisConnection.getQueryResult(
        #     """select
        #             forest_cultures.creation_year,
        #             forest_cultures.row_spacing,
        #             forest_cultures.spacing_in_row,
        #             forest_cultures.amount,
        #             forest_cultures.condition,
        #             tapping.start_year,
        #             tapping.actual_end_year,
        #             tapping.condition,
        #             red_book_plants_animals.first_feature,
        #             red_book_plants_animals.second_feature,
        #             red_book_plants_animals.third_feature,
        #             red_book_plants_animals.fourth_feature,
        #             red_book_plants_animals.fifth_feature,
        #             red_book_plants_animals.sixth_feature,
        #             red_book_plants_animals.seventh_feature,
        #             red_book_plants_animals.eighth_feature
        #         from "public".forest_cultures forest_cultures
        #         left join public.tapping tapping on forest_cultures.subcompartment_characteristics_id = tapping.subcompartment_characteristics_id
        #         left join public.red_book_plants_animals red_book_plants_animals on forest_cultures.subcompartment_characteristics_id = red_book_plants_animals.subcompartment_characteristics_id
        #         where forest_cultures.subcompartment_characteristics_id = '{}'""".format(
        #         int(forestcode)
        #     )
        # )

        self.forest_cultures = postgisConnection.getQueryResult(
            """select
                    forest_cultures.creation_year,
                    forest_cultures.row_spacing,
                    forest_cultures.spacing_in_row,
                    forest_cultures.amount,
                    forest_cultures.condition
                from "public".forest_cultures forest_cultures
                where forest_cultures.subcompartment_characteristics_id = '{}'""".format(
                int(forestcode)
            )
        )

        self.tapping = postgisConnection.getQueryResult(
            """select
                    tapping.start_year,
                    tapping.actual_end_year,
                    tapping.condition
                from "public".tapping tapping
                where tapping.subcompartment_characteristics_id = '{}'""".format(
                int(forestcode)
            )
        )

        self.red_book_plants_animals = postgisConnection.getQueryResult(
            """select
                    eighth_red_book_species.description,
                    seventh_red_book_species.description,
                    sixth_red_book_species.description,
                    fifth_red_book_species.description,
                    fourth_red_book_species.description,
                    third_red_book_species.description,
                    second_red_book_species.description,
                    first_red_book_species.description
                from "public".red_book_plants_animals red_book_plants_animals
                left join "dictionary".red_book_species eighth_red_book_species on red_book_plants_animals.eighth_feature = eighth_red_book_species.code
                left join "dictionary".red_book_species seventh_red_book_species on red_book_plants_animals.seventh_feature = seventh_red_book_species.code
                left join "dictionary".red_book_species sixth_red_book_species on red_book_plants_animals.sixth_feature = sixth_red_book_species.code
                left join "dictionary".red_book_species fifth_red_book_species on red_book_plants_animals.fifth_feature = fifth_red_book_species.code
                left join "dictionary".red_book_species fourth_red_book_species on red_book_plants_animals.fourth_feature = fourth_red_book_species.code
                left join "dictionary".red_book_species third_red_book_species on red_book_plants_animals.third_feature = third_red_book_species.code
                left join "dictionary".red_book_species second_red_book_species on red_book_plants_animals.second_feature = second_red_book_species.code
                left join "dictionary".red_book_species first_red_book_species on red_book_plants_animals.first_feature = first_red_book_species.code
                where red_book_plants_animals.subcompartment_characteristics_id = '{}'""".format(
                int(forestcode)
            )
        )

        self.selection_features = postgisConnection.getQueryResult(
            """select
                    eighth_sf_dict.description,
                    seventh_sf_dict.description,
                    sixth_sf_dict.description,
                    fifth_sf_dict.description,
                    fourth_sf_dict.description,
                    third_sf_dict.description,
                    second_sf_dict.description,
                    first_sf_dict.description
                from "public".selection_features sf
                left join "dictionary".selection_features eighth_sf_dict on sf.eighth_feature = eighth_sf_dict.code
                left join "dictionary".selection_features seventh_sf_dict on sf.seventh_feature = seventh_sf_dict.code
                left join "dictionary".selection_features sixth_sf_dict on sf.sixth_feature = sixth_sf_dict.code
                left join "dictionary".selection_features fifth_sf_dict on sf.fifth_feature = fifth_sf_dict.code
                left join "dictionary".selection_features fourth_sf_dict on sf.fourth_feature = fourth_sf_dict.code
                left join "dictionary".selection_features third_sf_dict on sf.third_feature = third_sf_dict.code
                left join "dictionary".selection_features second_sf_dict on sf.second_feature = second_sf_dict.code
                left join "dictionary".selection_features first_sf_dict on sf.first_feature = first_sf_dict.code
                where sf.subcompartment_characteristics_id = '{}'""".format(
                int(forestcode)
            )
        )

        self.completed_economic_events = postgisConnection.getQueryResult(
            """select
                    xmer.name_xmer,
                    ce.year
                from "public".completed_economic_events ce
                left join "dictionary".xmer xmer on ce.event = xmer.code_xmer
                where ce.subcompartment_characteristics_id = '{}'""".format(
                int(forestcode)
            )
        )


        # if len(self.additional_info) > 0:
        #     for i in range(len(self.additional_info)):
        #         self.additional_info[i] = [
        #             "" if v is None else v for v in self.additional_info[i]
        #         ]
        #         self.additional_info[i] = {
        #             "creation_year": str(self.additional_info[i][0]),
        #             "row_spacing": str(self.additional_info[i][1]),
        #             "spacing_in_row": str(self.additional_info[i][2]),
        #             "amount": str(self.additional_info[i][3]),
        #             "cultures_condition": str(self.additional_info[i][4]),
        #             "start_year": str(self.additional_info[i][5]),
        #             "actual_end_year": str(self.additional_info[i][6]),
        #             "tapping_condition": str(self.additional_info[i][7]),
        #             "red_book_first_feature": str(self.additional_info[i][8]),
        #             "red_book_second_feature": str(self.additional_info[i][9]),
        #             "red_book_third_feature": str(self.additional_info[i][10]),
        #             "red_book_fourth_feature": str(self.additional_info[i][11]),
        #             "red_book_fifth_feature": str(self.additional_info[i][12]),
        #             "red_book_sixth_feature": str(self.additional_info[i][13]),
        #             "red_book_seventh_feature": str(self.additional_info[i][14]),
        #             "red_book_eighth_feature": str(self.additional_info[i][15])
        #         }
        
        if len(self.forest_cultures) > 0:
            for i in range(len(self.forest_cultures)):
                self.forest_cultures[i] = [
                    "" if v is None else v for v in self.forest_cultures[i]
                ]
                self.forest_cultures[i] = {
                    "creation_year": str(self.forest_cultures[i][0]),
                    "row_spacing": str(self.forest_cultures[i][1]),
                    "spacing_in_row": str(self.forest_cultures[i][2]),
                    "amount": str(self.forest_cultures[i][3]),
                    "forest_cultures_condition": str(self.forest_cultures[i][4]),
                }
        
        if len(self.tapping) > 0:
            for i in range(len(self.tapping)):
                self.tapping[i] = [
                    "" if v is None else v for v in self.tapping[i]
                ]
                self.tapping[i] = {
                    "start_year": str(self.tapping[i][0]),
                    "actual_end_year": str(self.tapping[i][1]),
                    "tapping_condition": str(self.tapping[i][2]),
                }
        
        if len(self.red_book_plants_animals) > 0:
            for i in range(len(self.red_book_plants_animals)):
                self.red_book_plants_animals[i] = [
                    "" if v is None else v for v in self.red_book_plants_animals[i]
                ]
                self.red_book_plants_animals[i] = {
                    "red_book_first_feature": str(self.red_book_plants_animals[i][0]),
                    "red_book_second_feature": str(self.red_book_plants_animals[i][1]),
                    "red_book_third_feature": str(self.red_book_plants_animals[i][2]),
                    "red_book_fourth_feature": str(self.red_book_plants_animals[i][3]),
                    "red_book_fifth_feature": str(self.red_book_plants_animals[i][4]),
                    "red_book_sixth_feature": str(self.red_book_plants_animals[i][5]),
                    "red_book_seventh_feature": str(self.red_book_plants_animals[i][6]),
                    "red_book_eighth_feature": str(self.red_book_plants_animals[i][7])
                }
        
        if len(self.selection_features) > 0:
            for i in range(len(self.selection_features)):
                self.selection_features[i] = [
                    "" if v is None else v for v in self.selection_features[i]
                ] 
                self.selection_features[i] = {
                    "selection_first_feature": str(self.selection_features[i][0]),
                    "selection_second_feature": str(self.selection_features[i][1]),
                    "selection_third_feature": str(self.selection_features[i][2]),
                    "selection_fourth_feature": str(self.selection_features[i][3]),
                    "selection_fifth_feature": str(self.selection_features[i][4]),
                    "selection_sixth_feature": str(self.selection_features[i][5]),
                    "selection_seventh_feature": str(self.selection_features[i][6]),
                    "selection_eighth_feature": str(self.selection_features[i][7])
                }

        if len(self.completed_economic_events) > 0:
            for i in range(len(self.completed_economic_events)):
                self.completed_economic_events[i] = [
                    "" if v is None else v for v in self.completed_economic_events[i]
                ]
                self.completed_economic_events[i] = {
                    "event": str(self.completed_economic_events[i][0]),
                    "year": str(self.completed_economic_events[i][1])
                }
        combined_add_data_dicts = self.forest_cultures + self.tapping + self.red_book_plants_animals + self.selection_features + self.completed_economic_events
        self.united_add_data_list = [dict(pair for add_data_dict in combined_add_data_dicts for pair in add_data_dict.items())]
    def finished(self, result):
        if result:
            QgsMessageLog.logMessage(
                'Task "{name}" completed\n'.format(name=self.description()),
                MESSAGE_CATEGORY,
                Qgis.Success,
            )
        else:
            if self.exception is None:
                QgsMessageLog.logMessage(
                    'Task "{name}" not successful but without exception '
                    "(probably the task was manually canceled by the "
                    "user)".format(name=self.description()),
                    MESSAGE_CATEGORY,
                    Qgis.Warning,
                )
            else:
                QgsMessageLog.logMessage(
                    'Task "{name}" Exception: {exception}'.format(
                        name=self.description(), exception=self.exception
                    ),
                    MESSAGE_CATEGORY,
                    Qgis.Critical,
                )
                raise self.exception

    def cancel(self):
        QgsMessageLog.logMessage(
            'Task "{name}" was cancelled'.format(name=self.description()),
            MESSAGE_CATEGORY,
            Qgis.Info,
        )
        super().cancel()
