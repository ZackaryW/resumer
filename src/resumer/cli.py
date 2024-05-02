import click
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from resumer.profiles import get_profile

@click.command()
@click.option("--copy-temp-folder", "-ct", default=False, is_flag=True)
@click.option("--profile", "-p", help="profile to use")
def cli(copy_temp_folder, profile):
    if not profile:
        click.echo("no profile specified")
        return
    
    try:
        get_profile(profile)(copy_temp_folder)
    except Exception as e:
        click.echo(e)
        click.echo("something went wrong, check the output above")


if __name__ == "__main__":
    cli()