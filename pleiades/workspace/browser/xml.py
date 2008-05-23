#from Acquisition import aq_inner
import transaction
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from elementtree import ElementTree as etree
import keytree
from Products.PleiadesEntity.Extensions.loader import loaden


class XMLImporter(BrowserView):
    
    """XML importing view
    """

    def __call__(self):
        request = self.request
        return loaden(self.context, request.form['sourcedir'])


class XMLImportForm(BrowserView):

    __call__ = ViewPageTemplateFile('import_xml_form.pt')

