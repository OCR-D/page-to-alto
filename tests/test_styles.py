from pytest import raises, main, fixture
from lxml import etree as ET
from ocrd_models.ocrd_page import TextStyleType, to_xml

from ocrd_page_to_alto.styles import TextStylesManager, LayoutTagManager, ParagraphStyleManager

def test_styles_id():
    m = TextStylesManager(alto_version='4')
    assert m.get_id(font_family='Foo') == 'textstyle-Foo---None---None---None---None---None'
    assert m.elements['textstyle-Foo---None---None---None---None---None']['font_family'] == 'Foo'

def test_styles_to_xml():
    m = TextStylesManager(alto_version='4')
    m.get_id(font_family='Foo Serif')
    el = ET.Element('Styles')
    m.to_xml(el)
    assert ET.tostring(el).decode('utf-8') == '<Styles><TextStyle ID="textstyle-Foo%20Serif---None---None---None---None---None" FONTFAMILY="Foo Serif"/></Styles>'
    assert m.elements['textstyle-Foo%20Serif---None---None---None---None---None']['font_family'] == 'Foo Serif'

def test_styles_from_textstyle():
    m = TextStylesManager(alto_version='4')
    textstyle = TextStyleType(fontFamily='Times New Roman', serif=True, textColourRgb=6559300)
    print(m.from_textstyle(textstyle))

def test_layouttagmanager():
    m = LayoutTagManager(alto_version='4')
    m.get_id(label='paragraph')
    el = ET.Element('Tags')
    m.to_xml(el)
    assert ET.tostring(el) == b'<Tags><LayoutTag ID="layouttag-paragraph" LABEL="paragraph"/></Tags>'

if __name__ == "__main__":
    main([__file__])
