import click
from .convert import OcrdPageAltoConverter
from ocrd_utils import initLogging

@click.command()
@click.option('--check-words/--no-check-words', default=True, help='Check whether PAGE-XML contains any Words and fail if not')
@click.option('--check-border/--no-check-border', default=True, help='Check whether PAGE-XML contains Border or PrintSpace')
@click.option('--skip-empty-lines/--no-skip-empty-lines', default=False, help='Whether to omit or keep empty lines in PAGE-XML')
@click.option('--trailing-dash-to-hyp/--no-trailing-dash-to-hyp', default=False, help='Whether to add a <HYP/> element if the last word in a line ends in "-"')
@click.option('--dummy-textline/--no-dummy-textline', default=True, help='Whether to create a TextLine for regions that have TextEquiv/Unicode but no TextLine')
@click.option('--dummy-word/--no-dummy-word', default=True, help='Whether to create a Word for TextLine that have TextEquiv/Unicode but no Word')
@click.option('--textequiv-index', default=0, help='If multiple textequiv, use the n-th TextEquiv by @index')
@click.option('--textequiv-fallback-strategy', default='last', type=click.Choice(['raise', 'first', 'last']), help="What to do if nth textequiv isn't available. 'raise' will lead to a runtime error, 'first' will use the first TextEquiv, 'last' will use the last TextEquiv on the element")
@click.argument('filename')
def main(check_words, check_border, skip_empty_lines, trailing_dash_to_hyp, dummy_textline, dummy_word, textequiv_index, textequiv_fallback_strategy, filename):
    """
    Convert PAGE to ALTO
    """
    initLogging()
    converter = OcrdPageAltoConverter(
        page_filename=filename,
        check_words=check_words,
        check_border=check_border,
        skip_empty_lines=skip_empty_lines,
        trailing_dash_to_hyp=trailing_dash_to_hyp,
        dummy_textline=dummy_textline,
        dummy_word=dummy_word,
        textequiv_index=textequiv_index,
        textequiv_fallback_strategy=textequiv_fallback_strategy
    )
    converter.convert()
    print(converter)

if __name__ == '__main__':
    main() # pylint: disable=no-value-for-parameter
