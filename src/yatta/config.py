import os
from copy import deepcopy
from tomlkit import parse, dumps, document, table, nl, comment
import logging

from yatta.utils import get_app_dirs

DATA_DIR, CONFIG_DIR, CACHE_DIR = get_app_dirs()
CONFIG_FILE = os.path.join(CONFIG_DIR, "settings.toml")

logger = logging.getLogger(__name__)


class Config(object):
    """
    A class to handle app configuration.
    """

    default_config = {
        "general": {"run_in_background": "false"},
        "formatting": {"figlet_font": "doom", "table_style": "fancy_grid"},
    }

    def __init__(self):
        self.defaults = self._construct_toml(self.default_config)
        self.user = self._generate_user_config()

    def __str__(self):
        return dumps(self.user)

    def _generate_user_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    content = f.read()
                    config = parse(content)
            except Exception as e:
                logger.error(e)
        else:
            # construct the default config toml if no config file exists
            config = self._construct_toml(self.defaults)
            # write to file
            with open(CONFIG_FILE, "w") as f:
                f.write(dumps(config))
        return config

    def _construct_toml(self, config_dict):
        toml_doc = document()
        toml_doc.add("title", "yatta configuration file.")
        tables = {}
        for category in config_dict.keys():
            tables[category] = table()
            for setting, value in config_dict[category].items():
                tables[category].add(setting, value)
            toml_doc.add(nl())
        return toml_doc

    def _restore_defaults(self):
        self.user = self._construct_toml(self.default_config)

    def get_user_value(self, table, key):
        return self.user[table][key]

    def set_user_value(self, table, key, value):
        self.user[table][key] = value
