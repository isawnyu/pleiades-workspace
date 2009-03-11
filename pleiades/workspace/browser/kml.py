import transaction
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from elementtree import ElementTree as etree
import keytree
import geojson
from pleiades.workspace.interfaces import IResource


from zope.interface import Interface, Invalid, invariant
from zope import schema
from z3c.form import form, field, button
from plone.app.z3cform.layout import wrap_form


class IKMLImport(Interface):
    """KML import interface
    """
    file = schema.Bytes(title=u"KML File", description=u"Select an uncompressed KML file; Its placemarks will be imported as features.", required=True)
    metadataId = schema.TextLine(title=u"Metadata Id", description=u"Enter the Plone id of a postional accuracy assessment", required=False)


class Form(form.Form):
    fields = field.Fields(IKMLImport)
    ignoreContext = True # don't use context to get widget data
    label = u"Import KML"
    
    @button.buttonAndHandler(u'Apply')
    def handleApply(self, action):
        data, errors = self.extractData()
        importer = KMLImporter(self.context, self.request)
        importer(data['file'], data.get('metadataId'))
        response = self.request.response
        response.setStatus(201)
        response.setHeader(
            'Location',
            '%s' % self.context.absolute_url()
            )
        response.redirect(self.context.absolute_url())

KMLImportForm = wrap_form(Form)


class KMLImporter(object):
    
    """KML importing view
    """
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
    
    def __call__(self, file, metadataId):
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        ptool = getToolByName(self.context, 'plone_utils')
        wtool = getToolByName(self.context, 'portal_workflow')
        
        places = portal['places']
        features = portal['features']
        
        savepoint = transaction.savepoint()
        try:
            k = etree.fromstring(file)
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
                
                # Locations
                if metadataId is not None:
                    posAccDoc = portal['features']['metadata'][metadataId]
                    f[lid].addReference(posAccDoc, 'location_accuracy')
                
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




# class KMLImportForm(BrowserView):
#
#     __call__ = ViewPageTemplateFile('import_kml_form.pt')
# 
