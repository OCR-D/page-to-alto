from json import loads
from ocrd_models.ocrd_page import PageType, PcGtsType
from pkg_resources import resource_string
from os.path import join

from ocrd import Processor
from ocrd_modelfactory import page_from_file
from ocrd_utils import (
    getLogger,
    assert_file_grp_cardinality,
    make_file_id
)

from .convert import OcrdPageAltoConverter

OCRD_TOOL = loads(resource_string(__name__, 'ocrd-tool.json').decode('utf8'))

# @dataclass()
# class OcrdPageResult():
#     pcgts : OcrdPage
#     images : List = field(default_factory=list)

class Page2AltoProcessor(Processor):

    def __init__(self, *args, **kwargs):
        kwargs['ocrd_tool'] = OCRD_TOOL['tools']['ocrd-page2alto-transform']
        kwargs['version'] = OCRD_TOOL['version']
        super().__init__(*args, **kwargs)
        self.log = getLogger('ocrd.processor.page2alto')


    def process(self):
        assert_file_grp_cardinality(self.input_file_grp, 1)
        assert_file_grp_cardinality(self.output_file_grp, 1)
        assert isinstance(self.parameter, dict)
        for n, input_file in enumerate(self.input_files):
            page_id = input_file.pageId or input_file.ID
            self.log.info("INPUT FILE %s (%d/%d) ", page_id, n + 1, len(self.input_files))
            pcgts = page_from_file(self.workspace.download_file(input_file))
            assert isinstance(pcgts, PcGtsType)
            self.log.debug('width %s height %s', pcgts.get_Page().imageWidth, pcgts.get_Page().imageHeight)
            self.add_metadata(pcgts)
            page = pcgts.get_Page()
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
            pcgts.set_pcGtsId(file_id)
            self.add_metadata(pcgts)
            self.workspace.add_file(
                ID=file_id,
                file_grp=self.output_file_grp,
                pageId=page_id,
                mimetype='application/alto+xml',
                local_filename=join(self.output_file_grp, file_id) + '.xml',
                content=str(converter))
