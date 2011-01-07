from csv import DictReader

from plone.app.z3cform.layout import wrap_form
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
import transaction
from z3c.form import form, field, button
from zope.interface import Interface, Invalid, invariant
from zope import schema

from pleiades.workspace.interfaces import IResource


class ICSVImport(Interface):
    """CSV import interface
    """
    file = schema.Bytes(
        title=u"File", 
        description=u"A CSV file; its rows will be imported as places",
        required=True)


class Form(form.Form):
    fields = field.Fields(ICSVImport)
    ignoreContext = True # don't use context to get widget data
    label = u"Import Places from CSV"
    
    @button.buttonAndHandler(u'Apply')
    def handleApply(self, action):
        upload_file = self.widgets['file'].value
        importer = CSVImporter(self.context, self.request)
        importer(upload_file)

        response = self.request.response
        response.redirect(self.context.absolute_url())

CSVImportForm = wrap_form(Form)


class CSVImporter(object):
    
    """CSV importing view
    """
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
    
    def __call__(self, csvfile):
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        ptool = getToolByName(self.context, 'plone_utils')
        wtool = getToolByName(self.context, 'portal_workflow')
        places = portal['places']

        reader = DictReader(csvfile)

        savepoint = transaction.savepoint()

        try:
            for row in reader:
                pid = places.invokeFactory(
                        'Place',
                        row['id'],
                        title=row['title'],
                        placeType=row['featureTypes'].split(','),
                        description=row['description'],
                        text=u'',
                        creators=row['creators'],
                        contributors='R. Talbert, T. Elliott, S. Gillies')

                #citations = ]
                #for ref in prime['refs']:
                #    citations.append(dict(identifier=None, range=ref))
                #        
                #refCitations = places[pid].getField('referenceCitations')
                #refCitations.resize(len(prime['refs']), places[pid])
                #places[pid].update(referenceCitations=citations)

                self.context.attach(places[pid])

        except:
            savepoint.rollback()
            raise
        
        transaction.commit()

