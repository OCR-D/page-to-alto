from functools import cached_property
from typing import Optional
from os.path import join

from ocrd import Processor
from ocrd_models.ocrd_file import OcrdFileType
from ocrd_utils import (
    make_file_id,
    MIMETYPE_PAGE,
)

from .convert import OcrdPageAltoConverter


class Page2AltoProcessor(Processor):

    @cached_property
    def executable(self):
        return 'ocrd-page2alto-transform'

    def process_page_file(self, *input_files: Optional[OcrdFileType]) -> None:
        input_file = input_files[0]
        assert input_file
        assert input_file.local_filename
        assert isinstance(self.parameter, dict)
        assert input_file.mimetype == MIMETYPE_PAGE
        self.logger.debug("converting file %s", input_file.local_filename)
        converter = OcrdPageAltoConverter(
            page_filename=input_file.local_filename,
            alto_version=self.parameter["alto_version"].replace('v', ''),
            check_words=self.parameter["check_words"],
            timestamp_src=self.parameter["timestamp_src"],
            check_border=self.parameter["check_border"],
            skip_empty_lines=self.parameter["skip_empty_lines"],
            trailing_dash_to_hyp=self.parameter["trailing_dash_to_hyp"],
            dummy_textline=self.parameter["dummy_textline"],
            dummy_word=self.parameter["dummy_word"],
            textequiv_index=self.parameter["textequiv_index"],
            textequiv_fallback_strategy=self.parameter["textequiv_fallback_strategy"],
            region_order=self.parameter["region_order"],
            textline_order=self.parameter["textline_order"],
        )
        converter.convert()
        file_id = make_file_id(input_file, self.output_file_grp)
        self.workspace.add_file(
            file_id=file_id,
            file_grp=self.output_file_grp,
            pageId=input_file.pageId,
            mimetype='application/alto+xml',
            local_filename=join(self.output_file_grp, file_id) + '.xml',
            content=str(converter))
