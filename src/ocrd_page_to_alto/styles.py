from lxml import etree as ET
from packaging import version

class TextStylesManager():
    """
    Keeps track of combination of PAGE attributes on the element level to map them
    to ALTO TextStyles. The @ID is a concatenation of the values with a prefix.
    """

    def __init__(self, alto_version):
        self.alto_version = alto_version
        self._elements = set()
        self.prefix = 'textstyle-'
        self.fields = ['font_family', 'font_type', 'font_width', 'font_size', 'font_color', 'font_style']
        self.output_element = 'TextStyle'

    def get_id(self, **kwargs):
        if any(k not in self.fields for k in kwargs):
            raise ValueError(f"Unknown fields in {kwargs}")
        key = self.prefix + '---'.join([str(kwargs.get(x, None)).replace(' ', '%20') for x in self.fields])
        if key not in self.elements:
            self._elements.add(key)
        return key

    @property
    def elements(self):
        ret = {}
        for key in self._elements:
            ret[key] = {}
            vals = key[len(self.prefix):].split('---')
            for field_idx, field in enumerate(self.fields):
                ret[key][field] = vals[field_idx].replace('%20', ' ')
        return ret

    def from_textstyle(self, textstyle):
        kwargs = {}
        kwargs['font_family'] = textstyle.fontFamily
        kwargs['font_type'] = 'serif' if textstyle.serif else 'sans-serif'
        kwargs['font_width'] = 'fixed' if textstyle.monospace else 'proportional'
        if textstyle.fontSize:
            kwargs['font_size'] = textstyle.fontSize
        if textstyle.textColourRgb:
            b = textstyle.textColourRgb // 65336
            g = (textstyle.textColourRgb - (b * 65336)) // 256
            r = textstyle.textColourRgb - (b * 65336) - (g * 256)
            kwargs['font_color'] = '%2x%2x%2x' % (r, g, b)
        if textstyle.textColour:
            # https://en.wikipedia.org/wiki/Web_colors
            rgb = 'ffffff' if textstyle.textColour == 'white' else \
                  '000000' if textstyle.textColour == 'black' else \
                  'ff0000' if textstyle.textColour == 'red' else \
                  '800000' if textstyle.textColour == 'brown' else \
                  '00ffff' if textstyle.fontColour == 'cyan' else \
                  '00ff00' if textstyle.fontColour == 'green' else \
                  '999999' if textstyle.fontColour == 'grey' else \
                  '4b0082' if textstyle.fontColour == 'indigo' else \
                  'ff00ff' if textstyle.fontColour == 'magenta' else \
                  'ffa500' if textstyle.fontColour == 'orange' else \
                  'ff00cb' if textstyle.fontColour == 'pink' else \
                  '40e0d0' if textstyle.fontColour == 'turquoise' else \
                  'ee82ee' if textstyle.fontColour == 'violet' else \
                  'ffff00' if textstyle.fontColour == 'yellow' else \
                  None
            if rgb:
                kwargs['font_color'] = rgb
        font_style = []
        if textstyle.italic:
            font_style.append('italics')
        if textstyle.underlined:
            font_style.append('underline')
        possible_atts = ['bold', 'smallCaps', 'subscript', 'superscript']
        if version.parse(self.alto_version) >= version.parse('4.2'):
            possible_atts.append('strikethrough')
        for att in possible_atts:
            if getattr(textstyle, att):
                font_style.append(att.lower())
        if font_style:
            kwargs['font_style'] = ' '.join(font_style)
        # TODO kerning
        # TODO underlineStyle
        # TODO bgColour
        # TODO bgColourRgb
        # TODO reverseVideo
        # TODO xHeight
        # TODO letterSpaced
        return self.get_id(**kwargs)

    def set_alto_styleref_from_textstyle(self, reg_alto, reg_page):
        textstyle = reg_page.get_TextStyle() if hasattr(reg_page, 'get_TextStyle') else None
        if textstyle:
            refs = reg_alto.get('STYLEREFS').split(' ') if reg_alto.get('STYLEREFS') else []
            refs.append(self.from_textstyle(textstyle))
            reg_alto.set('STYLEREFS', ' '.join(refs))

    def to_xml(self, alto_parent):
        for style_id, style in self.elements.items():
            el = ET.SubElement(alto_parent, self.output_element)
            el.set('ID', style_id)
            for k, v in style.items():
                if v != 'None':
                    el.set(k.replace('_', '').upper(), v)

class ParagraphStyleManager(TextStylesManager):

    def __init__(self, alto_version):
        super().__init__(alto_version)
        self.fields = ['align', 'left', 'right', 'line_space', 'first_line']
        self.prefix = 'parastyle-'
        self.output_element = 'ParagraphStyle'
        self.align_mapping = {'left': 'Left', 'right': 'Right', 'centre': 'center', 'justify': 'Block'}

    def set_alto_styleref_from_textstyle(self, reg_alto, reg_page):
        align_page = reg_page.align if hasattr(reg_page, 'align') else None
        if align_page:
            refs = reg_alto.get('STYLEREFS').split(' ') if reg_alto.get('STYLEREFS') else []
            refs.append(self.get_id(align=self.align_mapping[align_page]))
            reg_alto.set('STYLEREFS', ' '.join(refs))

class LayoutTagManager(TextStylesManager):

    def __init__(self, alto_version):
        super().__init__(alto_version)
        self.fields = ['label']
        self.prefix = 'layouttag-'
        self.output_element = 'LayoutTag'

    def set_alto_tag_from_type(self, reg_alto, reg_page):
        typ = reg_page.get_type() if hasattr(reg_page, 'get_type') else None
        if typ:
            if reg_alto.tag in ['ComposedBlock', 'Illustration']:
                reg_alto.set('TYPE', typ)
            reg_alto.set('TAGREFS', self.get_id(label=typ))

