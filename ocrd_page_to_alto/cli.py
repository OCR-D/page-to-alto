import click
from .convert import OcrdPageAltoConverter

@click.command()
@click.argument('filename')
def main(filename):
    """
    Convert PAGE to ALTO
    """
    converter = OcrdPageAltoConverter(page_filename=filename)
    converter.convert()
    print(converter)

if __name__ == '__main__':
    main()
