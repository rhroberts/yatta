"""
A class to handle app configuration.
"""


class Config(object):

    default_config = {
        "figlet_font": "doom",
        "table_style": "fancy_grid",
        "run_in_background": "false",
    }

    def __init__(self):
        self.defaults = self.default_config
