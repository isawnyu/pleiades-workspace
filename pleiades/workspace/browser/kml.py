import transaction
import uuid
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from lxml import etree
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
    file = schema.Bytes(title=u"File", 
    description=u"An uncompressed KML file; Its folders and placemarks will be imported as places", required=True)


class Form(form.Form):
    fields = field.Fields(IKMLImport)
    ignoreContext = True # don't use context to get widget data
    label = u"Import Places from KML"
    
    @button.buttonAndHandler(u'Apply')
    def handleApply(self, action):
        upload_file = self.widgets['file'].value
        importer = KMLImporter(self.context, self.request)
        importer(upload_file.read())

        response = self.request.response
        response.redirect(self.context.absolute_url())

KMLImportForm = wrap_form(Form)


class KMLImporter(object):
    
    """KML importing view
    """
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
    
    def __call__(self, kml):
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        ptool = getToolByName(self.context, 'plone_utils')
        wtool = getToolByName(self.context, 'portal_workflow')
        
        places = portal['places']
        features = portal['features']
        
        savepoint = transaction.savepoint()
        try:
            k = etree.fromstring(kml)
            kmlns = k.tag.split('}')[0][1:]
            
            # metadata doc
            dtitle = getattr(k.find('*/{%s}name' % kmlns), 
                        'text', 'Unnamed KML Document')
            mdid = features['metadata'].invokeFactory('PositionalAccuracy', 
                        str(uuid.uuid4()), title=dtitle, 
                        value=100.0, source=kml)
            features['metadata'][mdid].setTitle(dtitle)
            features['metadata'][mdid].setValue(100.0)
            features['metadata'][mdid].setSource(kml)
            features['metadata'][mdid].source.filename = dtitle
            features['metadata'][mdid].source.content_type = 'application/vnd.google-earth.kml+xml'
            self.context.attach(features['metadata'][mdid])
            
            # Build up a mapping of place and location elements
            kmlplaces = {}
            for pm_element in k.xpath('//kml:Placemark', 
                                      namespaces={'kml': kmlns}):
                parent = pm_element.getparent()
                if parent.tag == "{%s}Folder" % kmlns:
                    if parent not in kmlplaces:
                        kmlplaces[parent] = []
                    kmlplaces[parent].append(pm_element)
                else:
                    kmlplaces[pm_element] = [pm_element] 

            # Marshal them into Pleiades content objects
            for i, (place, locations) in enumerate(kmlplaces.items()):

                # Do place
                kmlid = place.attrib.get('id')
                title = getattr(place.find('{%s}name' % kmlns),
                                'text',
                                'Unnamed Place')
                description = getattr(place.find('{%s}Snippet' % kmlns),
                                    'text',
                                    "%s: %s" % (title, (kmlid or "%s of %s imported places" 
                                                        % (i+1, len(kmlplaces)))))
                text = getattr(place.find('{%s}description' % kmlns),
                               'text',
                               '')
                pid = places.invokeFactory(
                                    'Place',
                                    places.generateId(prefix=''),
                                    title=title,
                                    description=description,
                                    text=text
                                    )
                places[pid].setTitle(title)
                places[pid].setDescription(description)
                places[pid].setText(text)
                self.context.attach(places[pid])

                posAccDoc = features['metadata'][mdid]
                places[pid].addReference(posAccDoc, 'location_accuracy')
                
                # TODO: names

                for j, location in enumerate(locations):

                    f = keytree.feature(location)
                    
                    if location is not place:
                        name = f.properties['name']
                        description = getattr(
                            location.find('{%s}Snippet' % kmlns), 
                            'text', 'Imported KML Placemark')
                        text = getattr(
                            pm_element.find('{%s}description' % kmlns),
                            'text', '')
                        title = name or 'Unnamed Location'
                    else:
                        name = title = 'Position'
                        description = 'Nominal position of the ancient place'
                        text = ''
                   
                    # TODO: parse out temporal information

                    # Process a geo-interface provider into strict GeoJSON
                    # shorthand.
                    where = geojson.GeoJSON.to_instance(dict(
                                type=f.geometry.type,
                                coordinates=f.geometry.coordinates))
                    data = geojson.loads(geojson.dumps(where))
                    geometry = '%s:%s' % (str(data['type']), data['coordinates'])

                    lid = places[pid].invokeFactory('Location',
                            ptool.normalizeString(name 
                                            or "location-%s" % (f.id or j)), 
                            title=title, description=description,
                            text=text, geometry=geometry)
                    
                    places[pid][lid].setTitle(title)
                    places[pid][lid].setDescription(description)
                    places[pid][lid].setText(text)

                #transliteration = name.encode('utf-8')
                #nid = f.invokeFactory(
                #        'Name',
                #        ptool.normalizeString(transliteration),
                #        nameTransliterated=transliteration
                #        )
                
                    places[pid][lid].addReference(posAccDoc, 'location_accuracy')
                
        except:
            savepoint.rollback()
            raise
        
        transaction.commit()
