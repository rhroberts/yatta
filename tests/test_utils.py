# unit tests for the utils module
import pyfiglet

from yatta import utils as utils


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
