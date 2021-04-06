import click
from .convert import OcrdPageAltoConverter
from ocrd_utils import initLogging

@click.command()
@click.option('--check-words/--no-check-words', default=True, help='Check whether PAGE-XML contains any Words and fail if not')
@click.option('--check-border/--no-check-border', default=True, help='Check whether PAGE-XML contains Border or PrintSpace')
@click.option('--skip-empty-lines/--no-skip-empty-lines', default=False, help='Whether to omit or keep empty lines in PAGE-XML')
@click.argument('filename')
def main(check_words, check_border, skip_empty_lines, filename):
    """
    Convert PAGE to ALTO
    """
    initLogging()
    converter = OcrdPageAltoConverter(
        page_filename=filename,
        check_words=check_words,
        check_border=check_border,
        skip_empty_lines=skip_empty_lines,
    )
    converter.convert()
    print(converter)

if __name__ == '__main__':
    main()
