# unit tests for the utils module
import os
import pyfiglet
import logging

from yatta import utils as utils

logger = logging.getLogger(__name__)


def test_time_div():
    hour, min, sec = utils.time_div(3600)
    assert hour == 1
    assert min == 0
    assert sec == 0


def test_time_format():
    time_str = utils.time_format(1, 0, 0)
    assert time_str == "01:00:00"


def test_time_print():
    assert utils.time_print(65) == "00:01:05"


def test_time_figlet_print():
    count = 202
    font = pyfiglet.Figlet("doom")
    time_str = font.renderText("00:03:22")
    assert time_str == utils.time_figlet_print(font, count)


def test_get_app_dirs():
    # test that the dirs can be created
    for dir_type in ["data", "cache", "config"]:
        try:
            # create and get test dir
            app_dir = utils.get_app_dirs("_tmp", dir_type)
            # remove the test dir
            os.removedirs(app_dir)
        except Exception as e:
            logger.error(e)
