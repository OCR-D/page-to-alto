from pytest import raises, main, fixture
from lxml import etree as ET

from ocrd_page_to_alto.convert import OcrdPageAltoConverter, NAMESPACES
from ocrd_utils import initLogging

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
    assert str(c).split('\n')[0] == '<alto xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.loc.gov/standards/alto/ns-v4#" xsi:schemaLocation="http://www.loc.gov/standards/alto/v4/alto-4-2.xsd">'

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
    tree = ET.fromstring(str(c).encode('utf-8'))
    assert [x.get('LABEL') for x in tree.xpath('//alto:Tags/alto:LayoutTag', namespaces=NAMESPACES)] == ['paragraph']

def test_pararaphstyle():
    c = OcrdPageAltoConverter(page_filename='tests/data/align.page.xml').convert()
    tree = ET.fromstring(str(c).encode('utf-8'))
    assert tree.xpath('//alto:ParagraphStyle', namespaces=NAMESPACES)[0].get('ALIGN') == 'Block'
    assert 'parastyle-Block---None---None---None---None' in tree.xpath('//alto:TextBlock', namespaces=NAMESPACES)[0].get('STYLEREFS')

if __name__ == "__main__":
    main([__file__])
