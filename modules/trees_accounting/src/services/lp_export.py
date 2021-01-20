import json
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtCore import QThread, pyqtSignal
from ..models.dictionary import Organization


class LPExportedData(QThread):
    """
    Поток для сохранения данных в JSON для импорта в АРМ Лесопользование.
    """

    signal_message_result = pyqtSignal(dict)

    def __init__(self, att_data: dict, model: QStandardItemModel, export_file: str):
        QThread.__init__(self)
        self.att_data = att_data
        self.model = model
        self.export_file = export_file

    def configure_json_head(self) -> dict:
        """
        Подгодавливаю "заголовок" JSONа.
        Пример:
        "uuid_area": "b42e8db0-3f59-4ea2-873f-dc1175dc990f",
        "code_enterprise": 1508020300,
        "code_forestry": 1508020301,
        "num_compartment": "11",
        "num_sub_compartment": "23, 3",
        "area": "1.8",
        "num_cutting_area": "",
        "date_offset": "18.01.2021",
        """
        _, code_enterprise, code_forestry = Organization.convert_org_id(
            self.att_data["num_forestry"], self.att_data["num_enterprise"]
        ).keys()

        head = {
            "code_enterprise": code_enterprise,
            "code_forestry": code_forestry,
            "num_compartment": self.att_data["compartment"],
            "num_sub_compartment": self.att_data["sub_compartment"],
            "area": self.att_data["area"],
            "num_cutting_area": self.att_data["num_cutting_area"],
            "date_offset": self.att_data["date_trial"],
        }
        return head

    def configure_json_body(self) -> list:
        """
        Подготавливаю "тело" запроса
        Пример:
        [
        {
        "code_spc": 27,
        "code_trf_height": 1,
        "trees": [
            {
            "dmr": 12,
            "num_ind": 36,
            "num_fuel": 0,
            "num_biodiversity": 0
            },
            {
            "dmr": 16,
            "num_ind": 16,
            "num_fuel": 0,
            "num_biodiversity": 0
             }
        },
        {
        "code_spc": 21,
        "code_trf_height": 1,
        "trees": [
            {
            "dmr": 16,
            "num_ind": 0,
            "num_fuel": 0,
            "num_biodiversity": 15
            },
            {
            "dmr": 40,
            "num_ind": 25,
            "num_fuel": 0,
            "num_biodiversity": 0
            }
        ]
        }
        ]
        """
        body = []
        code_species_in_body = []
        for instance in self.model.as_list():
            if instance["code_species"] not in code_species_in_body:
                code_species_in_body.append(instance["code_species"])
                body.append(
                    {
                        "code_spc": instance["code_species"],
                        "code_trf_height": 1,
                        "trees": [],
                    }
                )
            for rec in body:
                if rec["code_spc"] == instance["code_species"]:
                    rec["trees"].append(
                        {
                            "dmr": instance["dmr"],
                            "num_ind": instance["num_ind"],
                            "num_fuel": instance["num_fuel"],
                        }
                    )
        return body

    def run(self):

        output_lp_dict = self.configure_json_head()
        output_lp_dict["species"] = self.configure_json_body()

        with open(self.export_file, "w") as file:
            json.dump(output_lp_dict, file, indent=1, ensure_ascii=False)

        self.signal_message_result.emit(
            {
                "main_text": f"Данные успешно экспортированы в \n{self.export_file}.",
                "detailed_text": None,
            }
        )
