import os

from appdirs import user_cache_dir
import click

APPNAME = "yatta"
CACHE_DIR = user_cache_dir(APPNAME)


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
