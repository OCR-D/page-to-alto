from pytest import raises, main, fixture
from lxml import etree as ET
from datetime import datetime

from ocrd_page_to_alto.convert import OcrdPageAltoConverter, NAMESPACES as _NAMESPACES
from ocrd_utils import initLogging

NAMESPACES = {**_NAMESPACES, 'alto': _NAMESPACES['alto'] % '4'}

from tests.assets import Assets

# @fixture
# def assets():
#     return Assets('')

initLogging()

def test_empty_init_kwargs():
    with raises(ValueError):
        OcrdPageAltoConverter()

def test_create_alto():
    c = OcrdPageAltoConverter(page_filename='tests/assets/kant_aufklaerung_1784/data/OCR-D-GT-PAGE/PAGE_0017_PAGE.xml')
    assert str(c).split('\n')[1] == '<alto xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.loc.gov/standards/alto/ns-v4#" xsi:schemaLocation="http://www.loc.gov/standards/alto/ns-v4# http://www.loc.gov/standards/alto/v4/alto-4-2.xsd" SCHEMAVERSION="4.2">'

def test_convert1():
    c = OcrdPageAltoConverter(page_filename='tests/assets/kant_aufklaerung_1784/data/OCR-D-GT-PAGE/PAGE_0017_PAGE.xml')
    c.convert()
    # print(c)
    # assert 0

def test_convert2():
    c = OcrdPageAltoConverter(page_filename='tests/assets/origin/Blumbach/extra_regions.xml')
    c.convert()
    # print(c)
    # assert 0

def test_convert3():
    c = OcrdPageAltoConverter(page_filename='tests/assets/origin/Blumbach/extra_regions.xml')
    c.convert()
    # print(c)
    # assert 0

def test_convert_no_words():
    with raises(ValueError, match='Line the-bad-one has.*not words'):
        OcrdPageAltoConverter(check_border=False, page_filename='tests/data/content-no-words.page.xml')

def test_convert_language():
    c = OcrdPageAltoConverter(page_filename='tests/data/language.page.xml').convert()
    tree = ET.fromstring(str(c).encode('utf-8'))
    assert tree.xpath('//*[@ID="r1"]/@LANG', namespaces=NAMESPACES)[0] == 'vol'
    assert tree.xpath('//*[@ID="r1-l1"]/@LANG', namespaces=NAMESPACES)[0] == 'nob'
    assert tree.xpath('//*[@ID="r1-l1-w1"]/@LANG', namespaces=NAMESPACES)[0] == 'epo'

def test_convert_processingstep():
    c = OcrdPageAltoConverter(page_filename='tests/data/OCR-D-OCR-TESS_00001.xml').convert()
    tree = ET.fromstring(str(c).encode('utf-8'))
    assert tree.xpath('//alto:Processing/alto:processingSoftware/alto:softwareName', namespaces=NAMESPACES)[0].text == 'ocrd-olena-binarize'

def test_layouttag():
    c = OcrdPageAltoConverter(page_filename='tests/data/layouttag.page.xml').convert()
    print(str(c))
    tree = ET.fromstring(str(c).encode('utf-8'))
    assert [x.get('LABEL') for x in tree.xpath('//alto:Tags/alto:LayoutTag', namespaces=NAMESPACES)] == ['paragraph']
    assert len(tree.xpath('//*[@LABEL="paragraph"]')) == 1
    assert len(tree.xpath('//*[@LABEL="catch-word"]')) == 0 # @TYPE only allowed for BlockType

def test_pararaphstyle():
    c = OcrdPageAltoConverter(page_filename='tests/data/align.page.xml').convert()
    tree = ET.fromstring(str(c).encode('utf-8'))
    assert tree.xpath('//alto:ParagraphStyle', namespaces=NAMESPACES)[0].get('ALIGN') == 'Block'
    assert 'parastyle-Block---None---None---None---None' in tree.xpath('//alto:TextBlock', namespaces=NAMESPACES)[0].get('STYLEREFS')

def test_dummy():
    c = OcrdPageAltoConverter(check_border=False, dummy_textline=True, dummy_word=True, page_filename='tests/data/region_no_line.page.xml').convert()
    tree = ET.fromstring(str(c).encode('utf-8'))
    assert len(tree.xpath('//alto:TextLine[@ID="r0-dummy-TextLine"]', namespaces=NAMESPACES)) == 1
    assert len(tree.xpath('//alto:String[@ID="r0-dummy-TextLine-dummy-Word"]', namespaces=NAMESPACES)) == 1
    assert tree.xpath('//alto:String[@ID="r0-dummy-TextLine-dummy-Word"]', namespaces=NAMESPACES)[0].get('CONTENT') == 'CONTENT BUT NO LINES'

def test_pageclass():
    c = OcrdPageAltoConverter(page_filename='tests/data/blank.page.xml').convert()
    tree = ET.fromstring(str(c).encode('utf-8'))
    assert tree.xpath('//alto:Page', namespaces=NAMESPACES)[0].get('PAGECLASS') == 'blank'

def test_sp():
    c = OcrdPageAltoConverter(page_filename='tests/data/sp-hyp.page.xml').convert()
    tree = ET.fromstring(str(c).encode('utf-8'))
    assert len(tree.xpath('//alto:SP', namespaces=NAMESPACES)) == 2

def test_hyp():
    c = OcrdPageAltoConverter(trailing_dash_to_hyp=True, page_filename='tests/data/sp-hyp.page.xml').convert()
    tree = ET.fromstring(str(c).encode('utf-8'))
    assert tree.xpath('//alto:HYP', namespaces=NAMESPACES)

def test_reading_order():
    c = OcrdPageAltoConverter(page_filename='tests/data/FILE_0010_OCR-D-OCR-CALAMARI.xml').convert()
    # region_order='document'
    tree = ET.fromstring(str(c).encode('utf-8'))
    assert len(tree.xpath('//alto:PrintSpace/alto:TextBlock', namespaces=NAMESPACES)) == 3
    assert tree.xpath('//alto:TextBlock[1]', namespaces=NAMESPACES)[0].get('ID') == 'region_0001'
    assert tree.xpath('//alto:TextBlock[1]/alto:TextLine/alto:String', namespaces=NAMESPACES)[0].get('CONTENT') == 'wird'
    # region_order='reading-order'
    c = OcrdPageAltoConverter(region_order='reading-order', page_filename='tests/data/FILE_0010_OCR-D-OCR-CALAMARI.xml').convert()
    tree = ET.fromstring(str(c).encode('utf-8'))
    assert len(tree.xpath('//alto:PrintSpace/alto:TextBlock', namespaces=NAMESPACES)) == 3
    assert tree.xpath('//alto:TextBlock[1]', namespaces=NAMESPACES)[0].get('ID') == 'region_0003'
    # region_order='reading-order-only'
    c = OcrdPageAltoConverter(region_order='reading-order-only', page_filename='tests/data/FILE_0010_OCR-D-OCR-CALAMARI.xml').convert()
    tree = ET.fromstring(str(c).encode('utf-8'))
    assert len(tree.xpath('//alto:PrintSpace/alto:TextBlock', namespaces=NAMESPACES)) == 2
    assert tree.xpath('//alto:TextBlock[1]', namespaces=NAMESPACES)[0].get('ID') == 'region_0003'

def test_convert_timestamp():
    ts = datetime.fromisoformat

    last_changed = ts('2018-04-25T17:44:49.605+01:00')
    tree = ET.fromstring(str(OcrdPageAltoConverter(
        page_filename='tests/data/timestamp.page.xml',
        timestamp_src='LastChange',
    ).convert()).encode('utf-8'))
    assert ts(tree.xpath('//alto:processingDateTime/text()', namespaces=NAMESPACES)[0]) == last_changed

    created = ts('2016-09-20T11:09:27.041+02:00')
    tree = ET.fromstring(str(OcrdPageAltoConverter(
        page_filename='tests/data/timestamp.page.xml',
        timestamp_src='Created',
    ).convert()).encode('utf-8'))
    assert ts(tree.xpath('//alto:processingDateTime/text()', namespaces=NAMESPACES)[0]) == created

    tree = ET.fromstring(str(OcrdPageAltoConverter(
        page_filename='tests/data/timestamp.page.xml',
        timestamp_src='none',
    ).convert()).encode('utf-8'))
    with raises(IndexError):
        assert tree.xpath('//alto:processingDateTime/text()', namespaces=NAMESPACES)[0]


if __name__ == "__main__":
    main([__file__])
