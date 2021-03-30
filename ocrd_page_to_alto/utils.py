from lxml import etree as ET
from ocrd_utils import xywh_from_points

def set_alto_xywh_from_coords(reg_alto, reg_page, classes=None):
    if classes is None:
        classes = ['HEIGHT', 'WIDTH', 'HPOS', 'VPOS']
    xywh = xywh_from_points(reg_page.get_Coords().points)
    if 'HEIGHT' in classes:
        reg_alto.set('HEIGHT', str(xywh['h']))
    if 'WIDTH' in classes:
        reg_alto.set('WIDTH', str(xywh['w']))
    if 'HPOS' in classes:
        reg_alto.set('HPOS', str(xywh['x']))
    if 'VPOS' in classes:
        reg_alto.set('VPOS', str(xywh['y']))

def set_alto_shape_from_coords(reg_alto, reg_page):
    shape = ET.SubElement(reg_alto, 'Shape')
    polygon = ET.SubElement(shape, 'Polygon')
    setxml(polygon, 'POINTS', reg_page.get_Coords().points)

def set_alto_id_from_page_id(reg_alto, reg_page):
    setxml(reg_alto, 'ID', reg_page.id)

def setxml(el, name, val):
    el.set(name, str(val))

