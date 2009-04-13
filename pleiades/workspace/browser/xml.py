import glob
from os.path import basename
import logging
from elementtree import ElementTree as etree
import transaction
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
import keytree
from Products.PleiadesEntity.Extensions.loader import load_place
from pleiades.workspace.interfaces import IResource

from zope.interface import Interface, Invalid, invariant
from zope import schema
from z3c.form import form, field, button
from plone.app.z3cform.layout import wrap_form


class IXMLImport(Interface):
    """KML import interface
    """
    directory = schema.TextLine(title=u"XML source directory", description=u"Enter absolute path of a local directory containing XML data files.", required=True)
    metadataId = schema.TextLine(title=u"Metadata Id", description=u"Enter the Plone id of a postional accuracy assessment", required=False)


class Form(form.Form):
    fields = field.Fields(IXMLImport)
    ignoreContext = True # don't use context to get widget data
    label = u"Import XML files"
    
    @button.buttonAndHandler(u'Apply')
    def handleApply(self, action):
        data, errors = self.extractData()
        importer = XMLImporter(self.context, self.request)
        msg = importer(data['directory'], data.get('metadataId'))
        response = self.request.response
        response.setStatus(201)
        response.setHeader(
            'Location',
            '%s' % self.context.absolute_url()
            )
        response.redirect(self.context.absolute_url())

XMLImportForm = wrap_form(Form)


class XMLImporter(object):
    
    """XML importing view
    """
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
    
    def __call__(self, directory, metadataId=None):
        request = self.request
        sourcedir = directory
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        places = portal['places']
        features = portal['features']
        failures = []
        count = 0
        log = logging.getLogger("pleiades.entity")
        for xml in glob.glob("%s/*.xml" % sourcedir):
            try:
                result = load_place(portal, xml, metadataId, cb=self.context.attach)
                count += 1
            except Exception, e:
                raise
                log.error("Failed to load %s", xml, exc_info=1)
                failures.append([basename(xml), str(e)])
        
        if len(failures) == 0:
            return "Loaded %d of %d files." % (count, count)
        else:
            msg = "Loaded %d of %d files. Failures:\n" % (count, count + len(failures))
            for f in failures:
                msg += "%s\n" % str(f)
            return msg
