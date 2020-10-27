import click


@click.group()
def cli():
    pass


@click.command()
def getXml():
    click.echo("extract .xml from .nlogo file")


cli.add_command(getXml)

if __name__ == "__main__":
    cli()
