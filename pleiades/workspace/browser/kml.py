#from Acquisition import aq_inner
import transaction
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from elementtree import ElementTree as etree


class KMLImporter(BrowserView):
    
    """KML importing view
    """

    def __call__(self):
        request = self.request
        response = self.request.response
        
        places = self.context['places']
        names = self.context['names']
        locations = self.context['locations']

        ptool = getToolByName(self.context, 'plone_utils')

        savepoint = transaction.savepoint()

        try:
            k = etree.fromstring(request.file.read())
            for p in k.findall('*/{http://earth.google.com/kml/2.1}Placemark'):
                n = p.find('{http://earth.google.com/kml/2.1}name')
                name = n.text
                nid = names.invokeFactory(
                        'Name',
                        id=ptool.normalizeString(name),
                        title=name.encode('utf-8')
                        )
                pid = places.invokeFactory(
                        'Place',
                        id=ptool.normalizeString(name),
                        title=name.encode('utf-8')
                        )
                place = places[pid]
                aid = place.invokeFactory(
                        'PlacefulAssociation',
                        id=nid
                        )
                a = place[aid]
                a.addReference(names[nid], 'hasName')
        except:
            savepoint.rollback()
            raise

        transaction.commit()
        return "Success"


class KMLImportForm(BrowserView):

    __call__ = ViewPageTemplateFile('import_kml_form.pt')

