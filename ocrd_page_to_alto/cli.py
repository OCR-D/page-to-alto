import click
from .convert import OcrdPageAltoConverter
from ocrd_utils import initLogging

@click.command()
@click.option('--check-words/--no-check-words', default=True, help='Check whether PAGE-XML contains any Words and fail if not')
@click.option('--check-border/--no-check-border', default=True, help='Check whether PAGE-XML contains Border or PrintSpace')
@click.argument('filename')
def main(check_words, check_border, filename):
    """
    Convert PAGE to ALTO
    """
    initLogging()
    converter = OcrdPageAltoConverter(page_filename=filename, check_words=check_words, check_border=check_border)
    converter.convert()
    print(converter)

if __name__ == '__main__':
    main()
