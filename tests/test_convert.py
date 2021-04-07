from pytest import raises, main, fixture
from ocrd_page_to_alto.convert import OcrdPageAltoConverter
from tests.assets import Assets
from ocrd_utils import initLogging

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

if __name__ == "__main__":
    main([__file__])
