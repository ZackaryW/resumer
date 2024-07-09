from functools import cache
import logging
import os
import pprint
import sys
import typing
import click
import toml

from resumer import gen
from resumer.utils import get_batches_model

def getProfile(prof):
    try:
        return getattr(gen.GenPlace, f"profile_{prof}")
    except AttributeError:
        raise click.UsageError(f"unknown profile: {prof}")


@cache
def encryptedStore():
    from keyrings.cryptfile import cryptfile

    def getPass():
        if "RESUMER_PASS" in os.environ:
            return os.environ["RESUMER_PASS"]
        else:
            click.echo("Enter password: ", nl=False)
            return click.prompt(type=str, hide_input=True)

    ring = cryptfile.CryptFileKeyring()
    ring.file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "keyring")
    ring.keyring_key = getPass()
    return ring

def getData(key : str):
    if key.startswith("[") and key.endswith("]"):
        return encryptedStore().get_password("STORE", key[1:-1])
    else:
        logging.debug(f"recieved key {key}, attempting to load as file")
        if key == ".":
            key = "data.toml"
        toml_data = toml.load(key)

        return toml_data


@click.group(invoke_without_command=True)
@click.option("--kp", help="keyring password")
@click.option("--debug", "-d", is_flag=True, help="debug mode")
def cli(kp, debug):
    if kp:
        os.environ["RESUMER_PASS"] = kp

    if debug:
        logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s", stream=sys.stdout)

@cli.command()
@click.argument("key")
def meta(key):
    tomld = encryptedStore().get_password("STORE", key)
    pprint.pprint(tomld)
    
@cli.command(help="generate files based on a profile")
@click.argument("prof")
@click.argument("files", nargs=-1)   
@click.option("--store", "-s", help="save meta to encrypted store")
@click.option("--dfile", "-d", default=False, is_flag=True, help="debug files")
@click.pass_context
def profgen(ctx : click.Context, prof, files, store, dfile):
    if prof == ".":
        prof = "txt_1"

    profile : typing.Callable = getProfile(prof)

    data = [getData(file) for file in files]

    data = get_batches_model(*data)
    dumped = data.dump_dict()
    if store:
        encryptedStore().set_password("STORE", store, toml.dumps(dumped))

    if not data:
        raise click.UsageError("no data provided")

    profile(dumped, **{"dfiles" : dfile})

if __name__ == "__main__":
    cli()