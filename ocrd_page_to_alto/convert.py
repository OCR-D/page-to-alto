# pylint: disable=no-member, c-extension-no-member
from json import dumps
from packaging import version

from lxml import etree as ET
from ocrd_models.ocrd_page import (
    TextLineType,
    WordType,
    parse,
    parseString,
    to_xml)
from ocrd_models.constants import NAMESPACES as NAMESPACES_
from ocrd_utils import getLogger, xywh_from_points

from .utils import (
    set_alto_id_from_page_id,
    set_alto_lang_from_page_lang,
    set_alto_shape_from_coords,
    set_alto_xywh_from_coords,
    setxml,
    get_nth_textequiv)
from .styles import TextStylesManager, ParagraphStyleManager, LayoutTagManager

NAMESPACES = {**NAMESPACES_}
NAMESPACES['xsi'] = 'http://www.w3.org/2001/XMLSchema-instance'
NAMESPACES['alto'] = 'http://www.loc.gov/standards/alto/ns-v%s#'

REGION_PAGE_TO_ALTO = {
    'Text': 'TextBlock',
    'Separator': 'GraphicalElement',
    'Graphic': 'Illustration',
    'LineDrawing': 'Illustration',
    'Chart': 'Illustration',
    'Image': 'Illustration',
    "Table": 'ComposedBlock',
    # TODO how to handle these
    "Maths": None,
    "Chem": None,
    "Music": None,
    "Advert": None,
    "Noise": None,
    "Unknown": None,
    "Custom": None,
}

HYPHEN_CHARS = ['-', '⸗', '=']

XSD_ALTO_URLS = {
    '4.2': 'http://www.loc.gov/standards/alto/v4/alto-4-2.xsd',
    '4.1': 'http://www.loc.gov/standards/alto/v4/alto-4-1.xsd',
    '4.0': 'http://www.loc.gov/standards/alto/v4/alto-4-0.xsd',
    '3.1': 'http://www.loc.gov/standards/alto/v3/alto-3-1.xsd',
    '3.0': 'http://www.loc.gov/standards/alto/v3/alto-3-0.xsd',
    '2.1': 'http://www.loc.gov/standards/alto/alto.xsd',
    '2.0': 'http://www.loc.gov/standards/alto/v2/alto-2-0.xsd'
}

class OcrdPageAltoConverter():

    def __init__(
        self,
        *,
        alto_version='4.2',
        check_words=True,
        check_border=True,
        skip_empty_lines=False,
        trailing_dash_to_hyp=False,
        textequiv_index=0,
        textequiv_fallback_strategy='last',
        page_filename=None,
        dummy_textline=True,
        dummy_word=True,
        page_etree=None,
        pcgts=None,
        logger=None
    ):
        """
        Keyword Args:
            alto_version (string): Version of ALTO-XML schema to produce (older versions may not preserve all features)
            check_words (boolean): Whether to check if PAGE-XML contains any words before conversion and fail if not
            check_border (boolean): Whether to abort if neither Border nor PrintSpace is defined
            skip_empty_lines (boolean): Whether to omit empty lines completely (True) or create a placeholder empty String in ALTO (False)
            trailing_dash_to_hyp (boolean): Whether to add a <HYP/> element if the last word in a line ends in ``-``
            textequiv_index (int): @index of the TextEquiv to choose
            textequiv_fallback_strategy ("raise"|"first"|"last"): Strategy to handle case of no matchin TextEquiv by textequiv_index
            dummy_textline (boolean): Whether to create a TextLine for regions that have TextEquiv/Unicode but no TextLine
            dummy_word (boolean): Whether to create a Word for TextLine that have TextEquiv/Unicode but no Word
        """
        if not (page_filename or page_etree or pcgts):
            raise ValueError("Must pass either pcgts, page_etree or page_filename to constructor")
        if alto_version not in XSD_ALTO_URLS:
            raise ValueError("Converting to ALTO-XML v%s is not supported" % alto_version)
        self.alto_version = alto_version
        self.skip_empty_lines = skip_empty_lines
        self.trailing_dash_to_hyp = trailing_dash_to_hyp
        self.dummy_textline = dummy_textline
        self.dummy_word = dummy_word
        self.logger = logger if logger else getLogger('page-to-alto')
        if pcgts:
            self.page_pcgts = pcgts
        elif page_etree:
            self.page_pcgts = parseString(ET.tostring(page_etree))
        else:
            self.page_pcgts = parse(page_filename)
        self.page_page = self.page_pcgts.get_Page()
        if check_words:
            self.check_words()
        if check_border:
            tree = ET.fromstring(to_xml(self.page_pcgts).encode('utf-8'))
            self.check_border(tree)
        self.textequiv_index = textequiv_index
        self.textequiv_fallback_strategy = textequiv_fallback_strategy
        self.alto_alto, self.alto_description, self.alto_styles, self.alto_tags, self.alto_page = self.create_alto()
        self.alto_printspace = self.convert_border()
        self.textstyle_mgr = TextStylesManager(self.alto_version)
        self.parastyle_mgr = ParagraphStyleManager(self.alto_version)
        self.layouttag_mgr = LayoutTagManager(self.alto_version)

    def __str__(self):
        return ET.tostring(self.alto_alto,
                           pretty_print=True,
                           xml_declaration=True,
                           standalone=True,
                           encoding="UTF-8").decode('utf-8')

    def to_etree(self):
        return self.alto_alto

    def check_words(self):
        for reg_page in self.page_page.get_AllRegions(classes=['Text']):
            for line_page in reg_page.get_TextLine():
                textequiv = line_page.get_TextEquiv()
                if any(x.Unicode for x in textequiv) and not line_page.get_Word():
                    raise ValueError("Line %s has TextEquiv but not words, so cannot be converted to ALTO without losing information. Use --no-check-words to override" % line_page.id)

    def check_border(self, tree):
        if tree.find('.//page:Border', NAMESPACES) is None and tree.find('.//page:PrintSpace', NAMESPACES) is None:
            raise ValueError("The PAGE-XML to transform contains neither Border nor PrintSpace")

    def create_alto(self):
        alto_alto = ET.Element('alto')
        setxml(alto_alto, 'xmlns', NAMESPACES['alto'] % self.alto_version[:1])
        setxml(alto_alto, '{%s}schemaLocation' % NAMESPACES['xsi'],
               "%s %s" % (NAMESPACES['alto'] % self.alto_version[:1],
                          XSD_ALTO_URLS[self.alto_version]))
        alto_description = ET.SubElement(alto_alto, 'Description')
        alto_styles = ET.SubElement(alto_alto, 'Styles')
        if version.parse(self.alto_version) >= version.parse('2.1'):
            alto_tags = ET.SubElement(alto_alto, 'Tags')
        else:
            alto_tags = None
        alto_layout = ET.SubElement(alto_alto, 'Layout')
        if version.parse(self.alto_version) >= version.parse('3.0'):
            setxml(alto_alto, 'SCHEMAVERSION', self.alto_version)
        alto_page = ET.SubElement(alto_layout, 'Page')
        setxml(alto_page, 'ID', getattr(self.page_pcgts, 'pcGtsId', 'page0'))
        setxml(alto_page, 'PHYSICAL_IMG_NR', 0)
        page_type = self.page_page.get_type()
        if page_type:
            setxml(alto_page, 'PAGECLASS', page_type)
        return alto_alto, alto_description, alto_styles, alto_tags, alto_page

    def convert(self):
        self.convert_metadata()
        self.convert_text()
        self.convert_reading_order()
        self.convert_styles()
        return self

    def convert_styles(self):
        self.textstyle_mgr.to_xml(self.alto_styles)
        self.parastyle_mgr.to_xml(self.alto_styles)
        if version.parse(self.alto_version) >= version.parse('2.1'):
            self.layouttag_mgr.to_xml(self.alto_tags)

    def convert_reading_order(self):
        index_order = [x.id for x in self.page_page.get_AllRegions(order='reading-order', depth=0)]
        for id_cur, id_next in zip(index_order[:-1], index_order[1:]):
            self.alto_printspace.find('.//*[@ID="%s"]' % id_cur).set('IDNEXT', id_next)

    def convert_border(self):
        page_width = self.page_page.imageWidth
        page_height = self.page_page.imageHeight
        setxml(self.alto_page, 'WIDTH', page_width)
        setxml(self.alto_page, 'HEIGHT',  page_height)
        page_printspace = self.page_page.get_PrintSpace()
        dummy_printspace = False
        if page_printspace is None:
            self.logger.warning("PAGE-XML has no PrintSpace, trying to fall back to Border")
            page_printspace = self.page_page.get_Border()
            if page_printspace is None:
                dummy_printspace = True

        alto_printspace = ET.SubElement(self.alto_page, 'PrintSpace')
        if dummy_printspace:
            self.logger.warning("PAGE-XML has neither Border nor PrintSpace")
            for pos in ('Top', 'Left', 'Right', 'Bottom'):
                margin = ET.SubElement(self.alto_page, '%sMargin' % pos)
                for att in ('VPOS', 'HPOS', 'HEIGHT', 'WIDTH'):
                    setxml(margin, att, 0)
        else:
            xywh = xywh_from_points(page_printspace.get_Coords().points)
            alto_topmargin = ET.SubElement(self.alto_page, 'TopMargin')
            setxml(alto_topmargin, 'VPOS', 0)
            setxml(alto_topmargin, 'HPOS', 0)
            setxml(alto_topmargin, 'HEIGHT', xywh['x'])
            setxml(alto_topmargin, 'WIDTH', page_width)
            alto_leftmargin = ET.SubElement(self.alto_page, 'LeftMargin')
            setxml(alto_leftmargin, 'VPOS', 0)
            setxml(alto_leftmargin, 'HPOS', 0)
            setxml(alto_leftmargin, 'HEIGHT', page_height)
            setxml(alto_leftmargin, 'WIDTH', xywh['x'])
            alto_rightmargin = ET.SubElement(self.alto_page, 'RightMargin')
            setxml(alto_rightmargin, 'VPOS', 0)
            setxml(alto_rightmargin, 'HPOS', xywh['x'] + xywh['w'])
            setxml(alto_rightmargin, 'HEIGHT', page_height)
            setxml(alto_rightmargin, 'WIDTH', page_width - (xywh['x'] + xywh['w']))
            alto_bottommargin = ET.SubElement(self.alto_page, 'BottomMargin')
            setxml(alto_bottommargin, 'VPOS', xywh['y'] + xywh['h'])
            setxml(alto_bottommargin, 'HPOS', 0)
            setxml(alto_bottommargin, 'HEIGHT', page_height - (xywh['y'] + xywh['h']))
            setxml(alto_bottommargin, 'WIDTH', page_width)
            set_alto_xywh_from_coords(alto_printspace, page_printspace)
            if version.parse(self.alto_version) >= version.parse('3.1'):
                set_alto_shape_from_coords(alto_printspace, page_printspace)

        if dummy_printspace:
            setxml(alto_printspace, 'VPOS', 0)
            setxml(alto_printspace, 'HPOS', 0)
            setxml(alto_printspace, 'HEIGHT', page_height)
            setxml(alto_printspace, 'WIDTH', page_width)
        else:
            set_alto_xywh_from_coords(alto_printspace, page_printspace)
            if version.parse(self.alto_version) >= version.parse('3.1'):
                set_alto_shape_from_coords(alto_printspace, page_printspace)

        return alto_printspace

    def convert_metadata(self):
        alto_measurementunit = ET.SubElement(self.alto_description, 'MeasurementUnit')
        alto_measurementunit.text = 'pixel'
        alto_sourceimageinformation = ET.SubElement(self.alto_description, 'sourceImageInformation')
        alto_filename = ET.SubElement(alto_sourceimageinformation, 'fileName')
        alto_filename.text = self.page_page.imageFilename
        page_metadata = self.page_pcgts.get_Metadata()
        if not page_metadata:
            return
        for step_idx, step_page in enumerate([x for x in page_metadata.get_MetadataItem() if x.get_type() == 'processingStep']):
            if version.parse(self.alto_version) >= version.parse('4.0'):
                step_alto = ET.SubElement(self.alto_description, 'Processing')
            else:
                step_alto = ET.SubElement(self.alto_description, 'OCRProcessing')
                step_alto = ET.SubElement(step_alto, 'ocrProcessingStep')
            setxml(step_alto, 'ID', f'{step_page.value}-{step_idx}')
            step_alto_description = ET.SubElement(step_alto, 'processingStepDescription')
            step_alto_description.text = step_page.name
            if step_page.get_Labels():
                step_alto_settings = ET.SubElement(step_alto, 'processingStepSettings')
                json = {}
                for label in step_page.get_Labels()[0].get_Label():
                    json[label.get_type()] = label.value
                step_alto_settings.text = dumps(json)
            step_alto_software = ET.SubElement(step_alto, 'processingSoftware')
            step_alto_software_name = ET.SubElement(step_alto_software, 'softwareName')
            step_alto_software_name.text = step_page.value


    def _convert_textlines(self, reg_alto, reg_page):
        if self.dummy_textline:
            self.set_dummy_line_for_region(reg_page)
        for line_page in reg_page.get_TextLine():
            is_empty_line = not(line_page.get_TextEquiv() and line_page.get_TextEquiv()[0].get_Unicode()) and not(line_page.get_Word())
            if is_empty_line and self.skip_empty_lines:
                self.logger.debug("Skipping empty line '%s'", line_page.id)
                return
            line_alto = ET.SubElement(reg_alto, 'TextLine')
            set_alto_id_from_page_id(line_alto, line_page)
            set_alto_xywh_from_coords(line_alto, line_page)
            if version.parse(self.alto_version) >= version.parse('3.1'):
                set_alto_shape_from_coords(line_alto, line_page)
            if version.parse(self.alto_version) >= version.parse('2.1'):
                set_alto_lang_from_page_lang(line_alto, line_page)
            self.textstyle_mgr.set_alto_styleref_from_textstyle(line_alto, line_page)
            if is_empty_line:
                word_alto_empty = ET.SubElement(line_alto, 'String')
                word_alto_empty.set('ID', '%s-word0' % line_page.id)
                word_alto_empty.set('CONTENT', '')
            if self.dummy_word:
                self.set_dummy_word_for_textline(line_page)
            words_page = line_page.get_Word()
            for word_idx, word_page in enumerate(words_page):
                is_last_word = word_idx == len(words_page) - 1
                word_alto = ET.SubElement(line_alto, 'String')
                set_alto_id_from_page_id(word_alto, word_page)
                set_alto_xywh_from_coords(word_alto, word_page)
                if version.parse(self.alto_version) >= version.parse('3.1'):
                    set_alto_shape_from_coords(word_alto, word_page)
                if version.parse(self.alto_version) >= version.parse('2.1'):
                    set_alto_lang_from_page_lang(word_alto, word_page)
                self.textstyle_mgr.set_alto_styleref_from_textstyle(word_alto, word_page)
                word_content = get_nth_textequiv(word_page, self.textequiv_index, self.textequiv_fallback_strategy)
                if not is_last_word:
                    ET.SubElement(line_alto, 'SP')
                else:
                    if self.trailing_dash_to_hyp and word_content and word_content[-1] in HYPHEN_CHARS:
                        hyphen_content = word_content[-1]
                        hyp_alto = ET.SubElement(line_alto, 'HYP')
                        hyp_alto.set('CONTENT', hyphen_content)
                        word_content = word_content[:-1]
                word_alto.set('CONTENT', word_content)

    def _convert_table(self, parent_alto, parent_page, level=0):
        if not level:
            for reg_page in parent_page.get_TextRegion():
                self._convert_table(parent_alto, reg_page, level=level + 1)
        else:
            if parent_page.get_TextRegion():
                reg_alto = ET.SubElement(parent_alto, 'ComposedBlock')
                set_alto_id_from_page_id(reg_alto, parent_page) # TODO not unique!
                if version.parse(self.alto_version) >= version.parse('2.1'):
                    set_alto_lang_from_page_lang(reg_alto, parent_page)
                for reg_page in parent_page.get_TextRegion():
                    self._convert_table(reg_alto, reg_page, level=level + 1)
            else:
                textblock_alto = ET.SubElement(parent_alto, 'TextBlock')
                set_alto_id_from_page_id(textblock_alto, parent_page)
                if version.parse(self.alto_version) >= version.parse('2.1'):
                    set_alto_lang_from_page_lang(textblock_alto, parent_page)
                else:
                    set_alto_lang_from_page_lang(textblock_alto, parent_page, attribute_name="language")
                self._convert_textlines(textblock_alto, parent_page)

    def convert_text(self):
        for reg_page in self.page_page.get_AllRegions(depth=0):
            reg_page_type = reg_page.__class__.__name__[0:-10] # len('RegionType') == 10
            reg_alto_type = REGION_PAGE_TO_ALTO[reg_page_type]
            if not reg_alto_type:
                raise ValueError("Cannot handle PAGE-XML %sRegion" % reg_page_type)
            reg_alto = ET.SubElement(self.alto_printspace, reg_alto_type)
            set_alto_id_from_page_id(reg_alto, reg_page)
            set_alto_xywh_from_coords(reg_alto, reg_page)
            if version.parse(self.alto_version) >= version.parse('3.1'):
                set_alto_shape_from_coords(reg_alto, reg_page)
            if version.parse(self.alto_version) >= version.parse('2.1'):
                set_alto_lang_from_page_lang(reg_alto, reg_page)
            self.textstyle_mgr.set_alto_styleref_from_textstyle(reg_alto, reg_page)
            self.parastyle_mgr.set_alto_styleref_from_textstyle(reg_alto, reg_page)
            if version.parse(self.alto_version) >= version.parse('2.1'):
                self.layouttag_mgr.set_alto_tag_from_type(reg_alto, reg_page)
            if reg_page_type == 'Text':
                self._convert_textlines(reg_alto, reg_page)
            elif reg_page_type == 'Table':
                self._convert_table(reg_alto, reg_page)
            elif reg_page_type in ('Image', 'Separator'):
                pass # nothing more to do
            else:
                raise ValueError('Unhandled region type %s' % reg_page_type)

    def _set_dummy_x_for_y(self, el, parent_level):
        child_level = 'Word' if parent_level == 'TextLine' else 'TextLine'
        child_type = WordType if parent_level == 'TextLine' else TextLineType
        children = getattr(el, 'get_%s' % child_level)()
        if not children:
            self.logger.debug("%s '%s' has no %s", parent_level, el.id, child_level)
            if len(el.get_TextEquiv()) and any(x.Unicode for x in el.get_TextEquiv()):
                child_id = '%s-dummy-%s' % (el.id, child_level)
                self.logger.info("%s '%s' does have TextEquiv/Unicode though, creating dummy %s '%s'", parent_level, el.id, child_level, child_id)
                getattr(el, 'add_%s' % child_level)(child_type(id=child_id, Coords=el.get_Coords(), TextEquiv=el.get_TextEquiv()))

    def set_dummy_word_for_textline(self, line_page):
        self._set_dummy_x_for_y(line_page, 'TextLine')

    def set_dummy_line_for_region(self, reg_page):
        self._set_dummy_x_for_y(reg_page, 'TextRgion')
