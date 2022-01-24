import click
from .convert import OcrdPageAltoConverter
from ocrd_utils import initLogging
from ocrd.decorators import ocrd_loglevel

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.command(context_settings=CONTEXT_SETTINGS)
@ocrd_loglevel
@click.option('--alto-version', default='4.2', help='Choose version of ALTO-XML schema to produce (older versions may not preserve all features)',
              type=click.Choice(['4.2', '4.1', '4.0', '3.1', '3.0', '2.1', '2.0']))
@click.option('--check-words/--no-check-words', default=True, help='Check whether PAGE-XML contains any Words and fail if not')
@click.option('--check-border/--no-check-border', default=True, help='Check whether PAGE-XML contains Border or PrintSpace')
@click.option('--skip-empty-lines/--no-skip-empty-lines', default=False, help='Whether to omit or keep empty lines in PAGE-XML')
@click.option('--trailing-dash-to-hyp/--no-trailing-dash-to-hyp', default=False, help='Whether to add a <HYP/> element if the last word in a line ends in "-"')
@click.option('--dummy-textline/--no-dummy-textline', default=True, help='Whether to create a TextLine for regions that have TextEquiv/Unicode but no TextLine')
@click.option('--dummy-word/--no-dummy-word', default=True, help='Whether to create a Word for TextLine that have TextEquiv/Unicode but no Word')
@click.option('--textequiv-index', default=0, help='If multiple textequiv, use the n-th TextEquiv by @index')
@click.option('--textequiv-fallback-strategy', default='last', type=click.Choice(['raise', 'first', 'last']), help="What to do if nth textequiv isn't available. 'raise' will lead to a runtime error, 'first' will use the first TextEquiv, 'last' will use the last TextEquiv on the element")
@click.option('--region-order', default='document', help="Order in which to iterate over the regions", type=click.Choice(['document', 'reading-order', 'reading-order-only']))
@click.option('-O', '--output-file', default='-', help='Output filename (or "-" for standard output, the default)',
              type=click.Path(dir_okay=False, writable=True, exists=False, allow_dash=True))
@click.argument('filename',  type=click.Path(dir_okay=False, exists=True))
def main(log_level, alto_version, check_words, check_border, skip_empty_lines, trailing_dash_to_hyp, dummy_textline, dummy_word, textequiv_index, textequiv_fallback_strategy, region_order, output_file, filename):
    """
    Convert PAGE to ALTO
    """
    initLogging()
    converter = OcrdPageAltoConverter(
        alto_version=alto_version,
        page_filename=filename,
        check_words=check_words,
        check_border=check_border,
        skip_empty_lines=skip_empty_lines,
        trailing_dash_to_hyp=trailing_dash_to_hyp,
        dummy_textline=dummy_textline,
        dummy_word=dummy_word,
        textequiv_index=textequiv_index,
        textequiv_fallback_strategy=textequiv_fallback_strategy,
        region_order=region_order
    )
    converter.convert()
    with open(1 if output_file == '-' else output_file, 'w') as output:
        output.write(str(converter))

if __name__ == '__main__':
    main() # pylint: disable=no-value-for-parameter
