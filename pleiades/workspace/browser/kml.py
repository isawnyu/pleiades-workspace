#from Acquisition import aq_inner
import transaction
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from elementtree import ElementTree as etree
import keytree

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
            kmlns = k.tag.split('}')[0][1:]
            for pm_element in k.findall('*/{%s}Placemark' % kmlns):
                f = keytree.feature(pm_element)
                name = f.properties['name']
                description = f.properties['description']
                where = f.geometry
                lid = locations.invokeFactory(
                        'Location',
                        geometryType=where.type,
                        spatialCoordinates='%f %f' % (where.coordinates[1], where.coordinates[0])
                        )
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
                a.addReference(locations[lid], 'hasLocation')
        except:
            savepoint.rollback()
            raise

        transaction.commit()
        return "Success"


class KMLImportForm(BrowserView):

    __call__ = ViewPageTemplateFile('import_kml_form.pt')

