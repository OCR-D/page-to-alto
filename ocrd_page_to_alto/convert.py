# pylint: disable=no-member, c-extension-no-member
from lxml import etree as ET
from ocrd_models.ocrd_page import parse, parseString, to_xml
from ocrd_models.constants import NAMESPACES as NAMESPACES_
from ocrd_utils import getLogger, xywh_from_points

from .utils import (
    set_alto_id_from_page_id,
    set_alto_xywh_from_coords,
    set_alto_shape_from_coords,
    setxml
)
from .styles import TextStylesManager

NAMESPACES = {**NAMESPACES_}
NAMESPACES['xsi'] = 'http://www.w3.org/2001/XMLSchema-instance'
NAMESPACES['alto'] = 'http://www.loc.gov/standards/alto/ns-v4#'

REGION_PAGE_TO_ALTO = {
    'Text': 'TextBlock',
    'Separator': 'GraphicalElement',
    'Graphic': 'Illustration',
    'LineDrawing': 'Illustration',
    'Chart': 'Illustration',
    'Image': 'Illustration',
    "Table": 'ComposedBlock',
    # TODO how to handle these
    "Chart": None,
    "Maths": None,
    "Chem": None,
    "Music": None,
    "Advert": None,
    "Noise": None,
    "Unknown": None,
    "Custom": None,
}

class OcrdPageAltoConverter():

    def __init__(self, *, check_words=True, check_border=True, skip_empty_lines=False, page_filename=None, page_etree=None, pcgts=None, logger=None):
        """
        Keyword Args:
            check_words (boolean): Whether to check if PAGE-XML contains any words before conversion and fail if not
            check_border (boolean): Whether to abort if neither Border nor PrintSpace is defined
            skip_empty_lines (boolean): Whether to omit empty lines completely (True) or create a placeholder empty String in ALTO (False)
        """
        if not (page_filename or page_etree or pcgts):
            raise ValueError("Must pass either pcgts, page_etree or page_filename to constructor")
        self.skip_empty_lines = skip_empty_lines
        self.logger = logger if logger else getLogger('page-to-alto')
        if pcgts:
            self.page_pcgts = pcgts
        elif page_etree:
            self.page_pcgts = parseString(ET.tostring(page_etree))
        else:
            self.page_pcgts = parse(page_filename)
        self.page_page = self.page_pcgts.get_Page()
        if check_words or check_border:
            tree = ET.fromstring(to_xml(self.page_pcgts).encode('utf-8'))
            if check_words:
                self.check_words(tree)
            if check_border:
                self.check_border(tree)
        self.alto_alto, self.alto_description, self.alto_styles, self.alto_tags, self.alto_page = self.create_alto()
        self.alto_printspace = self.convert_border()
        self.textstyle_mgr = TextStylesManager()

    def __str__(self):
        return ET.tostring(self.alto_alto, pretty_print=True).decode('utf-8')

    def check_words(self, tree):
        for reg_page in self.page_page.get_AllRegions(classes=['Text']):
            print(reg_page)
            for line_page in reg_page.get_TextLine():
                print(line_page)
                textequiv = line_page.get_TextEquiv()
                if any(x.Unicode for x in textequiv) and not line_page.get_Word():
                    raise ValueError("Line %s has TextEquiv but not words, so cannot be converted to ALTO without losing information. Use --no-skip-words to override" % line_page.id)

    def check_border(self, tree):
        if tree.find('.//page:Border', NAMESPACES) is None and tree.find('.//page:PrintSpace', NAMESPACES) is None:
            raise ValueError("The PAGE-XML to transform contains neither Border nor PrintSpace")

    def create_alto(self):
        alto_alto = ET.Element('alto')
        setxml(alto_alto, 'xmlns', NAMESPACES['alto'])
        setxml(alto_alto, '{%s}schemaLocation' % NAMESPACES['xsi'], "http://www.loc.gov/standards/alto/v4/alto-4-2.xsd")
        alto_description = ET.SubElement(alto_alto, 'Description')
        alto_styles = ET.SubElement(alto_alto, 'Styles')
        alto_tags = ET.SubElement(alto_alto, 'Tags')
        alto_layout = ET.SubElement(alto_alto, 'Layout')
        alto_page = ET.SubElement(alto_layout, 'Page')
        setxml(alto_page, 'ID', getattr(self.page_pcgts, 'pcGtsId', 'page0'))
        setxml(alto_page, 'PHYSICAL_IMG_NR', 0)
        return alto_alto, alto_description, alto_styles, alto_tags, alto_page

    def convert(self):
        self.convert_metadata()
        self.convert_text()
        self.convert_reading_order()
        self.convert_styles()

    def convert_styles(self):
        self.textstyle_mgr.to_xml(self.alto_styles)
        # TODO ParagraphStyle

    def convert_reading_order(self):
        index_order = [x.id for x in self.page_page.get_AllRegions(order='reading-order', depth=0)]
        for id_cur, id_next in zip(index_order[:-1], index_order[1:]):
            self.alto_printspace.find('.//*[@ID="%s"]' % id_cur).set('IDNEXT', id_next)

    def convert_border(self):
        page_width = self.page_page.imageHeight
        page_height = self.page_page.imageHeight
        setxml(self.alto_page, 'WIDTH', page_width)
        setxml(self.alto_page, 'HEIGHT',  page_height)
        self.alto_page.set('WIDTH', str(page_width))
        page_border = self.page_page.get_Border()
        dummy_printspace = False
        if page_border is None:
            self.logger.warning("PAGE-XML has no Border, trying to fall back to PrintSpace")
            page_border = self.page_page.get_PrintSpace()
            if page_border is None:
                dummy_printspace = True

        if dummy_printspace:
            self.logger.warning("PAGE-XML has neither Border nor PrintSpace")
            for pos in ('Top', 'Left', 'Right', 'Bottom'):
                margin = ET.SubElement(self.alto_page, '%sMargin' % pos)
                for att in ('VPOS', 'HPOS', 'HEIGHT', 'WIDTH'):
                    setxml(margin, att, 0)
        else:
            xywh = xywh_from_points(page_border.get_Coords().points)
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

        alto_printspace = ET.SubElement(self.alto_page, 'PrintSpace')
        if page_border:
            set_alto_xywh_from_coords(alto_printspace, page_border)
            set_alto_shape_from_coords(alto_printspace, page_border)
        return alto_printspace

    def convert_metadata(self):
        alto_measurementunit = ET.SubElement(self.alto_description, 'MeasurementUnit')
        alto_measurementunit.text = 'pixel'
        alto_sourceimageinformation = ET.SubElement(self.alto_description, 'sourceImageInformation')
        alto_filename = ET.SubElement(alto_sourceimageinformation, 'fileName')
        alto_filename.text = self.page_page.imageFilename

    def _convert_textlines(self, reg_alto, reg_page):
        for line_page in reg_page.get_TextLine():
            is_empty_line = not(line_page.get_TextEquiv() and line_page.get_TextEquiv()[0].get_Unicode())
            if is_empty_line and self.skip_empty_lines:
                return
            line_alto = ET.SubElement(reg_alto, 'TextLine')
            set_alto_id_from_page_id(line_alto, line_page)
            set_alto_xywh_from_coords(line_alto, line_page)
            set_alto_shape_from_coords(line_alto, line_page)
            self.textstyle_mgr.set_alto_styleref_from_textstyle(line_alto, line_page)
            # XXX ALTO does not allow TextLine without at least one String
            if is_empty_line:
                word_alto_empty = ET.SubElement(line_alto, 'String')
                word_alto_empty.set('CONTENT', '')
            for word_page in line_page.get_Word():
                word_alto = ET.SubElement(line_alto, 'String')
                set_alto_id_from_page_id(word_alto, word_page)
                set_alto_xywh_from_coords(word_alto, word_page)
                set_alto_shape_from_coords(word_alto, word_page)
                word_alto.set('CONTENT', word_page.get_TextEquiv()[0].get_Unicode())

    def _convert_table(self, parent_alto, parent_page, level=0):
        if not level:
            for reg_page in parent_page.get_TextRegion():
                self._convert_table(parent_alto, reg_page, level=level + 1)
        else:
            if parent_page.get_TextRegion():
                reg_alto = ET.SubElement(parent_alto, 'ComposedBlock')
                set_alto_id_from_page_id(reg_alto, parent_page) # TODO not unique!
                for reg_page in parent_page.get_TextRegion():
                    self._convert_table(reg_alto, reg_page, level=level + 1)
            else:
                textblock_alto = ET.SubElement(parent_alto, 'TextBlock')
                set_alto_id_from_page_id(textblock_alto, parent_page)
                self._convert_textlines(textblock_alto, parent_page)

    def convert_text(self):
        for reg_page in self.page_page.get_AllRegions(depth=1):
            reg_page_type = reg_page.__class__.__name__[0:-10] # len('RegionType') == 10
            reg_alto_type = REGION_PAGE_TO_ALTO[reg_page_type]
            if not reg_alto_type:
                raise ValueError("Cannot handle PAGE-XML %sRegion" % reg_page_type)
            reg_alto = ET.SubElement(self.alto_printspace, reg_alto_type)
            set_alto_id_from_page_id(reg_alto, reg_page)
            set_alto_xywh_from_coords(reg_alto, reg_page)
            set_alto_shape_from_coords(reg_alto, reg_page)
            self.textstyle_mgr.set_alto_styleref_from_textstyle(reg_alto, reg_page)
            if reg_page_type == 'Text':
                self._convert_textlines(reg_alto, reg_page)
            elif reg_page_type == 'Table':
                self._convert_table(reg_alto, reg_page)
            elif reg_page_type in ('Image', 'Separator'):
                pass # nothing more to do
            else:
                raise ValueError('Unhandled region type %s' % reg_page_type)

