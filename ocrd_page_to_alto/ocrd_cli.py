from .ocrd_processor import Page2AltoProcessor
from click import command
from ocrd.decorators import ocrd_cli_options, ocrd_cli_wrap_processor

@command()
@ocrd_cli_options
def main(*args, **kwargs):
    return ocrd_cli_wrap_processor(Page2AltoProcessor, *args, **kwargs)

if __name__ == '__main__':
    main()
