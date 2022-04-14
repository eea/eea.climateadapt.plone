import logging
import requests

from zope import event
from zope.security import checkPermission

from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
import re

from babel._compat import BytesIO
from babel.messages import Catalog
from babel.messages.pofile import write_po

icon_re = re.compile("\[.*\]")


class MenuPot(BrowserView):

    @property
    def ptool(self):
        return getToolByName(self.context,
                             'portal_properties')['site_properties']
    def get_content(self):
        contents = {}
        contents['site_menu'] = self.ptool.getProperty('main_navigation_menu')
        contents['health_menu'] = self.ptool.getProperty('health_navigation_menu')

        catalog = Catalog()
        buf = BytesIO()
        for key in contents:
            for (i, line) in enumerate(contents[key].split("\n")):
                # print(line)
                line = line.strip()
                if not line:
                    continue
                if line.startswith("--"):
                    continue
                if line.startswith("-"):
                    line = line[1:].strip()
                if "/" in line:
                    b0, b1 = line.split("/", 1)
                else:
                    b0 = line

                msg = icon_re.sub("", b0)
                msg = msg.strip()

                catalog.add(msg, locations=[(key, i)])

        write_po(buf, catalog, omit_header=False)
        return buf.getvalue().decode("utf8")
