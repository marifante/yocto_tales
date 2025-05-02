import yaml
import logging
from typing import Union, Dict


logger = logging.getLogger(__name__)


class ConfigParser:
    def __init__(self, config_path: str):
        """ Constructore of the class.

        :param config_path: the path of the configuration yaml.
        """
        self._config_path = config_path

        with open(self._config_path, "r") as file:
            self._yaml_data = yaml.safe_load(file)

        self._validate_required_fields()
        self._complete_bitbake_field()

        logger.info(f"Configuration file {config_path} was read sucessfully")
        logger.info(self._yaml_data)

    def _validate_required_fields(self):
        """ Validate if the yaml file has the required fields. """
        required_fields = {
            "name": str,
            "layers": list,
            "bitbake": dict
        }

        for field_name, field_type in required_fields.items():
            if field_name not in self._yaml_data:
                raise ValueError(f"The field {field_name} was not found in the config file {self._config_path}")

            if not isinstance(self._yaml_data[field_name], field_type):
                raise ValueError(f"Field {field_name} has type {type(self._yaml_data[field_name])} but was supposed to have type {field_type}")

    def _complete_bitbake_field(self):
        """ Complete bitbake field with more details. """
        self._yaml_data['bitbake']['command'] = f"bitbake {self._yaml_data['bitbake']['image']}"

        self._yaml_data['bitbake']['setup_script'] = ""
        for cmd in self._yaml_data['bitbake']['setup']:
            self._yaml_data['bitbake']['setup_script'] += f"cd {cmd.get('cd', '.')} && {cmd['call']}\n"

    @property
    def name(self) -> str:
        """ Get the name of the configuration from the yaml file. """
        return self._yaml_data['name']

    @property
    def setup(self) -> Union[Dict, None]:
        """ Get the setup dictionary from the yaml file.

        Since this parameter is option in the yaml, can return None if
        it is not present.
        """
        return self._yaml_data.get('setup', None)

    @property
    def layers(self) -> dict:
        """ Get layers list from configuration yaml file. """
        return self._yaml_data['layers']

    @property
    def bitbake(self) -> dict:
        """ Get bitbake dictionary from configuration yaml file. """
        return self._yaml_data['bitbake']
