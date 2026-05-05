from contextlib import contextmanager
from pytest import raises, main, fixture
from lxml import etree as ET
from datetime import datetime

from ocrd_page_to_alto.convert import OcrdPageAltoConverter, NAMESPACES as _NAMESPACES
from ocrd_utils import initLogging

NAMESPACES = {**_NAMESPACES, 'alto': _NAMESPACES['alto'] % '4'}

initLogging()

@contextmanager
def roundtrip(c):
    tree = ET.fromstring(str(c.convert()).encode('utf-8'))
    def xpath(sel):
        return tree.xpath(sel, namespaces=NAMESPACES)
    yield xpath


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
    c = OcrdPageAltoConverter(page_filename='tests/data/language.page.xml')
    with roundtrip(c) as xpath:
        assert xpath('//*[@ID="r1"]/@LANG')[0] == 'vol'
        assert xpath('//*[@ID="r1-l1"]/@LANG')[0] == 'nob'
        assert xpath('//*[@ID="r1-l1-w1"]/@LANG')[0] == 'epo'

def test_convert_processingstep():
    c = OcrdPageAltoConverter(page_filename='tests/data/OCR-D-OCR-TESS_00001.xml')
    with roundtrip(c) as xpath:
        assert xpath('//alto:Processing/alto:processingSoftware/alto:softwareName')[0].text == 'ocrd-olena-binarize'

def test_layouttag():
    c = OcrdPageAltoConverter(page_filename='tests/data/layouttag.page.xml')
    print(str(c))
    with roundtrip(c) as xpath:
        assert [x.get('LABEL') for x in xpath('//alto:Tags/alto:LayoutTag')] == ['paragraph']
        assert len(xpath('//*[@LABEL="paragraph"]')) == 1
        assert len(xpath('//*[@LABEL="catch-word"]')) == 0 # @TYPE only allowed for BlockType

def test_pararaphstyle():
    c = OcrdPageAltoConverter(page_filename='tests/data/align.page.xml')
    with roundtrip(c) as xpath:
        assert xpath('//alto:ParagraphStyle')[0].get('ALIGN') == 'Block'
        assert 'parastyle-Block---None---None---None---None' in xpath('//alto:TextBlock')[0].get('STYLEREFS')

def test_dummy():
    c = OcrdPageAltoConverter(check_border=False, dummy_textline=True, dummy_word=True, page_filename='tests/data/region_no_line.page.xml')
    with roundtrip(c) as xpath:
        assert len(xpath('//alto:TextLine[@ID="r0-dummy-TextLine"]')) == 1
        assert len(xpath('//alto:String[@ID="r0-dummy-TextLine-dummy-Word"]')) == 1
        assert xpath('//alto:String[@ID="r0-dummy-TextLine-dummy-Word"]')[0].get('CONTENT') == 'CONTENT BUT NO LINES'

def test_pageclass():
    c = OcrdPageAltoConverter(page_filename='tests/data/blank.page.xml')
    with roundtrip(c) as xpath:
        assert xpath('//alto:Page')[0].get('PAGECLASS') == 'blank'

def test_sp():
    c = OcrdPageAltoConverter(page_filename='tests/data/sp-hyp.page.xml')
    with roundtrip(c) as xpath:
        assert len(xpath('//alto:SP')) == 2

def test_hyp():
    c = OcrdPageAltoConverter(trailing_dash_to_hyp=True, page_filename='tests/data/sp-hyp.page.xml')
    with roundtrip(c) as xpath:
        assert xpath('//alto:HYP')

def test_reading_order():
    c = OcrdPageAltoConverter(page_filename='tests/data/FILE_0010_OCR-D-OCR-CALAMARI.xml')
    # region_order='document'
    with roundtrip(c) as xpath:
        assert len(xpath('//alto:PrintSpace/alto:TextBlock')) == 3
        assert xpath('//alto:TextBlock[1]')[0].get('ID') == 'region_0001'
        assert xpath('//alto:TextBlock[1]/alto:TextLine/alto:String')[0].get('CONTENT') == 'wird'
    # region_order='reading-order'
    c = OcrdPageAltoConverter(region_order='reading-order', page_filename='tests/data/FILE_0010_OCR-D-OCR-CALAMARI.xml')
    with roundtrip(c) as xpath:
        assert len(xpath('//alto:PrintSpace/alto:TextBlock')) == 3
        assert xpath('//alto:TextBlock[1]')[0].get('ID') == 'region_0003'
    # region_order='reading-order-only'
    c = OcrdPageAltoConverter(region_order='reading-order-only', page_filename='tests/data/FILE_0010_OCR-D-OCR-CALAMARI.xml')
    with roundtrip(c) as xpath:
        assert len(xpath('//alto:PrintSpace/alto:TextBlock')) == 2
        assert xpath('//alto:TextBlock[1]')[0].get('ID') == 'region_0003'

def test_convert_timestamp():
    ts = datetime.fromisoformat

    last_changed = ts('2018-04-25T17:44:49.605+01:00')
    with roundtrip(OcrdPageAltoConverter(page_filename='tests/data/timestamp.page.xml', timestamp_src='LastChange')) as xpath:
        assert ts(xpath('//alto:processingDateTime/text()')[0]) == last_changed

    created = ts('2016-09-20T11:09:27.041+02:00')
    with roundtrip(OcrdPageAltoConverter(page_filename='tests/data/timestamp.page.xml', timestamp_src='Created')) as xpath:
        assert ts(xpath('//alto:processingDateTime/text()')[0]) == created

    with roundtrip(OcrdPageAltoConverter(page_filename='tests/data/timestamp.page.xml', timestamp_src='none')) as xpath:
        with raises(IndexError):
            assert xpath('//alto:processingDateTime/text()')[0]

def test_skip_empty_line():
    with roundtrip(OcrdPageAltoConverter(page_filename='tests/data/empty-lines.page.xml', skip_empty_lines=True)) as xpath:
        # Ensure that lines after an empty line are transcribed
        # ID="r1-l1-w1" HEIGHT="1" WIDTH="1" HPOS="0" VPOS="0" CONTENT="bar"
        assert len(xpath('//alto:String[@ID="r1-l1-w1"][@CONTENT="bar"]')) == 1


def test_no_duplicate_table_regions():
    c = OcrdPageAltoConverter(page_filename='tests/data/PPN860789411-00000001.page.xml')
    with roundtrip(c) as xpath:
        # with open('tests/data/PPN860789411-00000001.alto.xml', 'w') as f:
        #     f.write(str(c))
        # Ensure that this String is converted only once
        # WIDTH="63" HPOS="860" VPOS="1049" CONTENT="auch"
        assert len(xpath('//alto:String[@WIDTH="63"][@HPOS="860"][@VPOS="1049"][@CONTENT="auch"]')) == 1



if __name__ == "__main__":
    main([__file__])
