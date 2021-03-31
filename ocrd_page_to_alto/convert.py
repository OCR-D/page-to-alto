# pylint: disable=no-member, c-extension-no-member
from lxml import etree as ET
from ocrd_models.ocrd_page import (parse, parseString)
from ocrd_models.constants import NAMESPACES as NAMESPACES_
from ocrd_utils import getLogger, xywh_from_points

from .utils import (
    set_alto_id_from_page_id,
    set_alto_xywh_from_coords,
    set_alto_shape_from_coords,
    setxml
)

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

    def __init__(self, *, page_filename=None, page_etree=None, pcgts=None, logger=None):
        if not (page_filename or page_etree or pcgts):
            raise ValueError("Must pass either pcgts, page_etree or page_filename to constructor")
        self.logger = logger if logger else getLogger('page-to-alto')
        if pcgts:
            self.page_pcgts = pcgts
        elif page_etree:
            self.page_pcgts = parseString(ET.tostring(page_etree))
        else:
            self.page_pcgts = parse(page_filename)
        self.page_page = self.page_pcgts.get_Page()
        # TODO self.check_for_words()
        self.alto_alto, self.alto_description, self.alto_styles, self.alto_tags, self.alto_page = self.create_alto()
        self.alto_printspace = self.convert_border()

    def __str__(self):
        return ET.tostring(self.alto_alto, pretty_print=True).decode('utf-8')

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

    def convert_reading_order(self):
        index_order = [x.id for x in self.page_page.get_AllRegions(order='reading-order', depth=1)]
        for id_cur, id_next in zip(index_order[:-1], index_order[1:]):
            self.alto_printspace.find('*[@ID="%s"]' % id_cur).set('IDNEXT', id_next)

    def convert_border(self):
        page_width = self.page_page.imageHeight
        page_height = self.page_page.imageHeight
        setxml(self.alto_page, 'WIDTH', page_width)
        setxml(self.alto_page, 'HEIGHT',  page_height)
        self.alto_page.set('WIDTH', str(page_width))
        page_border = self.page_page.get_Border()
        if page_border is None:
            self.logger.warning("PAGE-XML has no Border, trying to fall back to PrintSpace")
            page_border = self.page_page.get_PrintSpace()
            if page_border is None:
                raise ValueError("PAGE-XML has neither Border nor PrintSpace")

        xywh = xywh_from_points(page_border.get_Coords().points)
        alto_topmargin = ET.SubElement(self.alto_page, 'TopMargin')
        setxml(alto_topmargin, 'VPOS', 0)
        setxml(alto_topmargin, 'HPOS', 0)
        setxml(alto_topmargin, 'HEIGHT', xywh['x'])
        setxml(alto_topmargin, 'WIDTH', page_width)
        alto_bottommargin = ET.SubElement(self.alto_page, 'BottomMargin')
        setxml(alto_bottommargin, 'VPOS', xywh['y'] + xywh['h'])
        setxml(alto_bottommargin, 'HPOS', 0)
        setxml(alto_bottommargin, 'HEIGHT', page_height - (xywh['y'] + xywh['h']))
        setxml(alto_bottommargin, 'WIDTH', page_width)
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

        alto_printspace = ET.SubElement(self.alto_page, 'PrintSpace')
        set_alto_xywh_from_coords(alto_printspace, page_border)
        set_alto_shape_from_coords(alto_printspace, page_border)
        return alto_printspace

    def convert_metadata(self):
        alto_measurementunit = ET.SubElement(self.alto_description, 'MeasurementUnit')
        alto_measurementunit.text = 'pixels'
        alto_sourceimageinformation = ET.SubElement(self.alto_description, 'sourceImageInformation')
        alto_filename = ET.SubElement(alto_sourceimageinformation, 'filename')
        alto_filename.text = self.page_page.imageFilename

    def _convert_textlines(self, reg_alto, reg_page):
        for line_page in reg_page.get_TextLine():
            line_alto = ET.SubElement(reg_alto, 'TextLine')
            set_alto_id_from_page_id(line_alto, line_page)
            set_alto_xywh_from_coords(line_alto, line_page)
            set_alto_shape_from_coords(line_alto, line_page)
            if not line_page.get_Word() and line_page.get_TextEquiv() and line_page.get_TextEquiv()[0].get_Unicode():
                raise ValueError("pc:TextLine '%s' has no pc:Word" % line_page.id)
            for word_page in line_page.get_Word():
                word_alto = ET.SubElement(line_alto, 'String')
                set_alto_id_from_page_id(word_alto, word_page)
                set_alto_xywh_from_coords(word_alto, word_page)
                set_alto_shape_from_coords(word_alto, word_page)
                word_alto.set('CONTENT', word_page.get_TextEquiv()[0].get_Unicode())

    def convert_text(self):
        for reg_page in self.page_page.get_AllRegions(depth=1):
            reg_page_type = reg_page.__class__.__name__[0:-10] # len('RegionType') == 10
            reg_alto_type = REGION_PAGE_TO_ALTO[reg_page_type]
            if not reg_alto_type:
                raise ValueError("Cannot handle PAGE-XML %sRegion" % reg_page_type)
            reg_alto = ET.SubElement(self.alto_printspace, reg_alto_type)
            if reg_page_type == 'Text':
                self._convert_textlines(reg_alto, reg_page)
            elif reg_page_type == 'Table':
                for reg_page_in_table in reg_page.get_TextRegion():
                    reg_alto_in_table = ET.SubElement(reg_alto, 'TextBlock')
                    self._convert_textlines(reg_alto_in_table, reg_page_in_table)
            elif reg_page_type in ('Image', 'Separator'):
                pass # nothing more to do
            else:
                raise ValueError('Unhandled region type %s' % reg_page_type)
            set_alto_id_from_page_id(reg_alto, reg_page)
            set_alto_xywh_from_coords(reg_alto, reg_page)
            set_alto_shape_from_coords(reg_alto, reg_page)

