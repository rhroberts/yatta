import logging
import os

from tomlkit import document, dumps, parse, table

from yatta.utils import get_app_dirs

DATA_DIR, CONFIG_DIR, CACHE_DIR = get_app_dirs()
CONFIG_FILE = os.path.join(CONFIG_DIR, "settings.toml")

logger = logging.getLogger(__name__)


class Config(object):
    """
    A class to handle app configuration.
    """

    default_dict = {
        "general": {"run_in_background": "false"},
        "formatting": {"figlet_font": "doom", "table_style": "pretty"},
        "plotting": {"columns": 75, "show_legend": "true"},
    }

    def __init__(self):
        self.default = construct_toml(self.default_dict)
        self.user = self._generate_user_config()

    def __str__(self):
        return dumps(self.user)

    def _generate_user_config(self):
        if os.path.exists(CONFIG_FILE):
            # read user settings from file
            try:
                with open(CONFIG_FILE, "r") as f:
                    content = f.read()
                    config = parse(content)
            except Exception as e:
                logger.error(e)
            # check for new default settings
            for category, settings in self.default_dict.items():
                if category not in config.keys():
                    config.add(category, table())
                else:
                    for setting, value in settings.items():
                        if setting not in config[category].keys():
                            config[category][setting] = value
            # remove deprecated settings
            for category, settings in config.items():
                # remove deprecated tables
                if category not in self.default_dict.keys():
                    config.remove(category)
                # remove deprecated settings within tables
                else:
                    for setting in settings.keys():
                        if setting not in self.default_dict[category]:
                            config[category].remove(setting)
        else:
            # construct the default config toml if no config file exists
            config = construct_toml(self.default_dict)
        # write to file
        self._write_to_config(config)
        return config

    def _write_to_config(self, toml_doc):
        with open(CONFIG_FILE, "w") as f:
            f.write(dumps(toml_doc))

    def _check_new_settings(self):
        """
        When new settings are added to `default_dict` in later versions, need to be
        able to add these into the user config file without wiping the file.
        """
        for category, settings in self.default_dict.items():
            if category not in self.user.keys():
                self.user.add(category, table())
                for setting, value in settings.items():
                    self.user[category][setting] = value
        self._write_to_config(self.user)

    def _remove_old_settings(self):
        pass

    def restore_defaults(self):
        self.user = construct_toml(self.default_dict)
        self._write_to_config(self.user)

    def get_user_value(self, table, key):
        return self.user[table][key]

    def set_user_value(self, table, key, value):
        self.user[table][key] = value
        self._write_to_config(self.user)


def construct_toml(config_dict):
    toml_doc = document()
    tables = {}
    for category in config_dict.keys():
        tables[category] = table()
        for setting, value in config_dict[category].items():
            tables[category].add(setting, value)
        toml_doc.add(category, tables[category])
    return toml_doc
