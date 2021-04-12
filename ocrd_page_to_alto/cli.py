import click
from .convert import OcrdPageAltoConverter
from ocrd_utils import initLogging

@click.command()
@click.option('--check-words/--no-check-words', default=True, help='Check whether PAGE-XML contains any Words and fail if not')
@click.option('--check-border/--no-check-border', default=True, help='Check whether PAGE-XML contains Border or PrintSpace')
@click.option('--skip-empty-lines/--no-skip-empty-lines', default=False, help='Whether to omit or keep empty lines in PAGE-XML')
@click.option('--textequiv-index', default=0, help='If multiple textequiv, use the n-th TextEquiv by @index')
@click.option('--textequiv-fallback-strategy', default='last', type=click.Choice(['raise', 'first', 'last']), help="What to do if nth textequiv isn't available. 'raise' will lead to a runtime error, 'first' will use the first TextEquiv, 'last' will use the last TextEquiv on the element")
@click.argument('filename')
def main(check_words, check_border, skip_empty_lines, textequiv_index, textequiv_fallback_strategy, filename):
    """
    Convert PAGE to ALTO
    """
    initLogging()
    converter = OcrdPageAltoConverter(
        page_filename=filename,
        check_words=check_words,
        check_border=check_border,
        skip_empty_lines=skip_empty_lines,
        textequiv_index=textequiv_index,
        textequiv_fallback_strategy=textequiv_fallback_strategy
    )
    converter.convert()
    print(converter)

if __name__ == '__main__':
    main() # pylint: disable=no-value-for-parameter
