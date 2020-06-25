import os

from appdirs import user_cache_dir
import click

APPNAME = "yatta"
CACHE_DIR = user_cache_dir(APPNAME)


@click.group()
def config():
    pass


# TODO: Make this idempotent
# TODO: Add disclaimer about things being added to bashrc/zshrc
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
        os.system(
            f'echo "\n# source yatta completions\nsource {comp_file}" >> {shell_config}'
        )
    elif shell == "zsh":
        shell_config = os.path.join(home, ".zshrc")
        os.system(f"_YATTA_COMPLETE=source_zsh yatta > {comp_file}")
        os.system(
            f'echo "\n# source yatta completions\nsource {comp_file}" >> {shell_config}'
        )
    else:
        os.system(f"_YATTA_COMPLETE=source_zsh yatta > {comp_file}")
        comp_dir = os.path.join(home, ".config/fish/completions/")
        os.system(f"cp {comp_file} {comp_dir}")
