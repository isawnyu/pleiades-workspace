import glob
from os.path import basename
import logging
from lxml import etree
import transaction
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
import keytree
from Products.PleiadesEntity.Extensions.loader import load_cap
from pleiades.workspace.interfaces import IResource

from zope.interface import Interface, Invalid, invariant
from zope import schema
from z3c.form import form, field, button
from plone.app.z3cform.layout import wrap_form


class ICAPImport(Interface):
    """CAP import interface
    """
    path = schema.TextLine(title=u"XML file path", description=u"Enter absolute path to data file", required=True)


class Form(form.Form):
    fields = field.Fields(ICAPImport)
    ignoreContext = True # don't use context to get widget data
    label = u"Import CAP directory XML file"
    
    @button.buttonAndHandler(u'Apply')
    def handleApply(self, action):
        importer = CAPImporter(self.context, self.request)
        msg = importer(self.widgets['path'].value)
        response = self.request.response
        response.setStatus(201)
        response.setHeader(
            'Location',
            '%s' % self.context.absolute_url()
            )
        response.redirect(self.context.absolute_url())

CAPImportForm = wrap_form(Form)


class CAPImporter(object):
    
    """XML importing view
    """
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
    
    def __call__(self, path):
        request = self.request
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        places = portal['places']
        failures = []
        count = 0
        log = logging.getLogger("pleiades.entity")
        doc = etree.parse(path)
        mapid = doc.getroot().attrib.get('mapnum', None)
        for i, pelem in enumerate(doc.findall('{http://atlantides.org/batlas/}place')):
            try:
                result = load_cap(portal, pelem, mapid, cb=self.context.attach)
                count += 1
            except Exception, e:
                raise
                log.error("Failed to load %s:%s", path, i, exc_info=1)
                failures.append([str(i), str(e)])
        
        if len(failures) == 0:
            return "Loaded %d of %d files." % (count, count)
        else:
            msg = "Loaded %d of %d files. Failures:\n" % (count, count + len(failures))
            for f in failures:
                msg += "%s\n" % str(f)
            return msg
