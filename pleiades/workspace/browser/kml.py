import transaction
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from elementtree import ElementTree as etree
import keytree
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
        names = portal['names']
        locations = portal['locations']
        
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
                        title=name.encode('utf-8')
                        )
                pid = places.invokeFactory(
                        'Place',
                        title=name.encode('utf-8')
                        )
                fid = features.invokeFactory(
                        'Feature',
                        )
                f = features[fid]
                f.addReference(names[nid], 'hasName')
                f.addReference(locations[lid], 'hasLocation')
                p = places[pid]
                p.addReference(f, 'hasFeature')

                # Attach to workspace
                self.context.attach(names[nid])
                self.context.attach(locations[lid])
                self.context.attach(f)
                self.context.attach(p)
               
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

