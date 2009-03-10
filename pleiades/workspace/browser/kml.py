import transaction
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from elementtree import ElementTree as etree
import keytree
import geojson
from pleiades.workspace.interfaces import IResource


class KMLImporter(BrowserView):
    
    """KML importing view
    """

    def __call__(self):
        request = self.request
        response = self.request.response
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        ptool = getToolByName(self.context, 'plone_utils')
        wtool = getToolByName(self.context, 'portal_workflow')

        places = portal['places']
        features = portal['features']
                
        savepoint = transaction.savepoint()
        try:
            k = etree.fromstring(request.file.read())
            kmlns = k.tag.split('}')[0][1:]
            for pm_element in k.findall('*/{%s}Placemark' % kmlns):
                f = keytree.feature(pm_element)
                name = f.properties['name']
                description = f.properties['description']

                # Process a geo-interface provider into strict GeoJSON
                # shorthand.
                where = geojson.GeoJSON.to_instance(dict(
                            type=f.geometry.type,
                            coordinates=f.geometry.coordinates
                            ))
                data = geojson.loads(geojson.dumps(where))
                geometry = '%s:%s' % (str(data['type']), data['coordinates'])
                fid = features.invokeFactory(
                        'Feature',
                        features.generateId(prefix=''),
                        title=name.encode('utf-8'),
                        )
                f = features[fid]
                lid = f.invokeFactory('Location', 'position', title='Position', geometry=geometry)
                transliteration = name.encode('utf-8')
                nid = f.invokeFactory(
                        'Name',
                        ptool.normalizeString(transliteration),
                        nameTransliterated=transliteration
                        )

                # Attach to workspace
                self.context.attach(f)               
        except:
            savepoint.rollback()
            raise

        transaction.commit()
        
        # Redirect to the workspace
        response.setStatus(201)
        response.setHeader(
            'Location', 
            '%s/drafting' % self.context.absolute_url()
            )
        response.redirect('%s/drafting' % self.context.absolute_url())


class KMLImportForm(BrowserView):

    __call__ = ViewPageTemplateFile('import_kml_form.pt')

