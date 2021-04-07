from lxml import etree as ET
from ocrd_utils import xywh_from_points

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
