import os

import click
import colorama as co
from tomlkit import dumps

from yatta.completion_helpers import get_figlet_fonts, get_table_formats
from yatta.config import Config
from yatta.utils import get_app_dirs

DATA_DIR, CONFIG_DIR, CACHE_DIR = get_app_dirs()


@click.group()
def config():
    """
    Configure yatta.
    """


@config.command()
@click.option(
    "-s", "--shell", required=True, type=click.Choice(["bash", "zsh", "fish"])
)
def completions(shell):
    """
    Generate shell completes for yatta.
    """
    home = os.environ.get("HOME")
    comp_file = os.path.join(CACHE_DIR, "_completions")

    if shell == "bash":
        shell_config = os.path.join(home, ".bashrc")
        os.system(f"_YATTA_COMPLETE=source_bash yatta > {comp_file}")
        print(
            "\nThe tab completion script has been generated! To enable, "
            + f"add the following to {shell_config} and open a new shell:\n"
        )
        print(f"# source yatta completions\nsource {comp_file}")
    elif shell == "zsh":
        shell_config = os.path.join(home, ".zshrc")
        os.system(f"_YATTA_COMPLETE=source_zsh yatta > {comp_file}")
        print(
            "\nThe tab completion script has been generated! To enable, "
            + f"add the following to {shell_config} and open a new shell:\n"
        )
        print(f"# source yatta completions\nsource {comp_file}")
    else:
        os.system(f"_YATTA_COMPLETE=source_zsh yatta > {comp_file}")
        comp_dir = os.path.join(home, ".config/fish/completions/")
        try:
            assert os.path.exists(comp_dir)
            os.system(f"cp {comp_file} {comp_dir}")
            print(
                "The tab completion script has been generated! "
                + "Open a new shell to enable completions."
            )
        except AssertionError:
            print(
                "\nYour fish completion direction is missing, please create it here:\n"
                + f"\n{comp_dir}"
            )


@config.command()
@click.argument("font", type=click.STRING, autocompletion=get_figlet_fonts)
def font(font):
    """
    Select figlet font for displaying stopwatch.
    """
    Config().set_user_value("formatting", "figlet_font", font)


@config.command()
@click.argument("style", type=click.STRING, autocompletion=get_table_formats)
def table_style(style):
    """
    Select tabulate table style.
    """
    Config().set_user_value("formatting", "table_style", style)


@config.command()
@click.argument("columns", type=click.INT)
def plot_columns(columns):
    """
    Set maximum number of columns for plots.
    """
    Config().set_user_value("plotting", "columns", columns)


@config.command()
@click.argument("run_in_background", type=click.BOOL)
def background(run_in_background):
    """
    Always run yatta in the background.
    """
    Config().set_user_value("general", "run_in_background", run_in_background)


@config.command()
@click.argument("show", type=click.BOOL)
def show_legend(show):
    """
    Always display a legend with applicable plots.
    """
    Config().set_user_value("plotting", "show_legend", show_legend)


@config.command()
@click.option("-d", "--defaults", is_flag=True, help="Print the default settings.")
def list(defaults):
    """
    List current user settings.
    """
    co.init(autoreset=True)
    if defaults:
        print(f"\n{co.Fore.BLUE}{dumps(Config().default)}")
    else:
        print(f"\n{co.Fore.GREEN}{Config()}")


@config.command()
@click.confirmation_option(
    prompt="Are you sure you want to reset the application settings?"
)
def restore_defaults():
    """
    Restore settings to default values.
    """
    Config().restore_defaults()
