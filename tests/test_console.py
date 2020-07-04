# unit tests for the console module
import pytest
from click.testing import CliRunner

from yatta.console import main


@pytest.fixture
def runner():
    return CliRunner()


def test_main_succeeds(runner):
    result = runner.invoke(main)
    assert result.exit_code == 0
