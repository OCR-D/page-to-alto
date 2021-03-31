import click
from .convert import OcrdPageAltoConverter
from ocrd_utils import initLogging

@click.command()
@click.argument('filename')
def main(filename):
    """
    Convert PAGE to ALTO
    """
    initLogging()
    converter = OcrdPageAltoConverter(page_filename=filename)
    converter.convert()
    print(converter)

if __name__ == '__main__':
    main()
