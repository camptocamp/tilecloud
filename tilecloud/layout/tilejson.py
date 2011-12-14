import re

from tilecloud.layout.template import TemplateTileLayout



class TileJSONTileLayout(TemplateTileLayout):

    def __init__(self, template):
        TemplateTileLayout.__init__(self, re.sub(r'\{([xyz])\}', lambda m: '%%(%s)d' % m.group(1), template))
