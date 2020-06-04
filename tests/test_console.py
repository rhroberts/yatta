# unit tests for the console module

from click.testing import CliRunner
import pytest

from yatta.console import main


@pytest.fixture
def runner():
    return CliRunner()


def test_main_succeeds(runner):
    result = runner.invoke(main)
    assert result.exit_code == 0
