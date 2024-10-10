from lxml import etree as ET
from ocrd_utils import xywh_from_points
import langcodes

def setxml(el, name, val):
    el.set(name, str(val))

def set_alto_xywh_from_coords(reg_alto, reg_page, classes=None):
    if classes is None:
        classes = ['HEIGHT', 'WIDTH', 'HPOS', 'VPOS']
    xywh = xywh_from_points(reg_page.get_Coords().points)
    mapping = {'HEIGHT': 'h', 'WIDTH': 'w', 'HPOS': 'x', 'VPOS': 'y'}
    for k_alto, k_xywh in mapping.items():
        if k_alto in classes:
            setxml(reg_alto, k_alto, str(xywh[k_xywh]))

def set_alto_shape_from_coords(reg_alto, reg_page):
    shape = ET.SubElement(reg_alto, 'Shape')
    polygon = ET.SubElement(shape, 'Polygon')
    setxml(polygon, 'POINTS', reg_page.get_Coords().points)

def set_alto_id_from_page_id(reg_alto, reg_page):
    setxml(reg_alto, 'ID', reg_page.id)

def set_alto_lang_from_page_lang(reg_alto, reg_page, attribute_name='LANG'):
    for prefix in ('primaryL', 'secondaryL', 'l'):
        lang_page = getattr(reg_page, f'{prefix}anguage', None)
        if lang_page:
            lang_alto = langcodes.find(lang_page).to_alpha3()
            setxml(reg_alto, attribute_name, lang_alto)
            return

def get_nth_textequiv(reg_page, textequiv_index, textequiv_fallback_strategy):
    if textequiv_fallback_strategy not in ('raise', 'first', 'last'):
        raise RuntimeError("Invalid value for textequiv_fallback_strategy: %s" % textequiv_fallback_strategy)
    textequivs = reg_page.get_TextEquiv()
    if not len(textequivs):
        if textequiv_fallback_strategy == 'raise':
            raise ValueError("PAGE element '%s' has no TextEquivs and fallback strategy is to raise" % reg_page.id)
        return ''
    for textequiv in textequivs:
        if textequiv.get_index() == textequiv_index:
            return textequiv.Unicode
    if textequiv_fallback_strategy == 'raise':
        raise ValueError("PAGE element '%s' has no TextEquiv index %d" % (
            reg_page.id, textequiv_index))
    elif textequiv_fallback_strategy == 'first':
        return textequivs[0].Unicode
    else:
        return textequivs[-1].Unicode

def contains(el, bbox):
    minx1, miny1, maxx1, maxy1 = bbox
    minx2 = int(el.get('HPOS'))
    miny2 = int(el.get('VPOS'))
    maxx2 = minx2 + int(el.get('WIDTH'))
    maxy2 = miny2 + int(el.get('HEIGHT'))
    if minx1 < minx2:
        return False
    if maxx1 > maxx2:
        return False
    if miny1 < miny2:
        return False
    if maxy1 > maxy2:
        return False
    return True
