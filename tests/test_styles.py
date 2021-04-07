from pytest import raises, main, fixture
from lxml import etree as ET
from ocrd_models.ocrd_page import TextStyleType, to_xml

from ocrd_page_to_alto.styles import TextStylesManager

def test_styles_id():
    m = TextStylesManager()
    assert m.get_style_id(font_family='Foo') == 'Foo---None---None---None---None---None'
    assert m.styles['Foo---None---None---None---None---None']['font_family'] == 'Foo'

def test_styles_to_xml():
    m = TextStylesManager()
    m.get_style_id(font_family='Foo Serif')
    el = ET.Element('Styles')
    m.to_xml(el)
    assert ET.tostring(el).decode('utf-8') == '<Styles><TextStyle ID="Foo%20Serif---None---None---None---None---None" FONTFAMILY="Foo Serif"/></Styles>'
    assert m.styles['Foo%20Serif---None---None---None---None---None']['font_family'] == 'Foo Serif'

def test_styles_from_textstyle():
    m = TextStylesManager()
    textstyle = TextStyleType(fontFamily='Times New Roman', serif=True, textColourRgb=6559300)
    print(m.from_textstyle(textstyle))
    assert 0

if __name__ == "__main__":
    main([__file__])
