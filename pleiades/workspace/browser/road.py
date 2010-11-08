import re
import simplejson
import transaction
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from pleiades.workspace.interfaces import IResource


from zope.interface import Interface, Invalid, invariant
from zope import schema
from z3c.form import form, field, button
from plone.app.z3cform.layout import wrap_form

period_ids = {
    "A": "archaic",
    "C": "classical",
    "H": "hellenistic-republican",
    "R": "roman",
    "L": "late-antique"
    }

class IRoadImport(Interface):
    """Road JSON import interface
    """
    file = schema.Bytes(title=u"File", 
    description=u"An uncompressed JSON road doc; Its objects will be imported as places", required=True)


class Form(form.Form):
    fields = field.Fields(IRoadImport)
    ignoreContext = True # don't use context to get widget data
    label = u"Import Places from Road JSON"
    
    @button.buttonAndHandler(u'Apply')
    def handleApply(self, action):
        upload_file = self.widgets['file'].value
        importer = RoadImporter(self.context, self.request)
        importer(upload_file.read())

        response = self.request.response
        response.redirect(self.context.absolute_url())

RoadImportForm = wrap_form(Form)


class RoadImporter(object):
    
    """Road JSON importing view
    """
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
    
    def __call__(self, json):
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        ptool = getToolByName(self.context, 'plone_utils')
        wtool = getToolByName(self.context, 'portal_workflow')
        catalog = getToolByName(self.context, 'portal_catalog')
        places = portal['places']
        
        savepoint = transaction.savepoint()
        try:
            doc = simplejson.loads(json)
            for key, road in doc['roads'].items():
                prime = road[0]
                pid = places.invokeFactory(
                                    'Place',
                                    places.generateId(prefix=''),
                                    title=prime['label'],
                                    placeType=['road'],
                                    description='An ancient place, cited: BAtlas %s %s' % (key, prime['label']),
                                    text=u'',
                                    creators=doc['compiler'],
                                    contributors='R. Talbert, T. Elliott, S. Gillies',
                                    )
                citations = []
                for ref in prime['refs']:
                    citations.append(dict(identifier=None, range=ref))
                        
                refCitations = places[pid].getField('referenceCitations')
                refCitations.resize(len(prime['refs']), places[pid])
                places[pid].update(referenceCitations=citations)

                self.context.attach(places[pid])

                for j, part in enumerate(road[1]):
                    if not part['label'] and not part['periods']:
                        continue
                    if not part['label']:
                        title = label = 'Barrington Atlas section'
                    else:
                        title = label = u'Section: ' + part['label']
                        label = re.sub(r'\W', '-', label, re.UNICODE)
                        label = re.sub(r'-+', '-', label)
                    try:
                        lid = places[pid].invokeFactory('Location',
                            ptool.normalizeString(label),
                            title=title, 
                            geometry='',
                            creators=doc['compiler'],
                            contributors='R. Talbert, T. Elliott, S. Gillies',
                        )
                    except:
                        import pdb; pdb.set_trace()
                        raise
                    loc = places[pid][lid]
                    m, g = key.split()
                    loc.setLocation(
                        'http://atlantides.org/capgrids/%s/%s' % (m, g))
                    loc.setDescription(
                        'Location overlaps the footprint of BAtlas map %s grid %s, but otherwise undetermined' % (m, g))
                    nodes = []
                    for name in part['nodes']:
                        hits = catalog(Title=name, portal_type='Place', pleiades_wsuids=[self.context.UID()])
                        if hits:
                            nodes.append(hits[0].UID)
                        else:
                            nodes.append(places)
                    loc.setNodes(nodes)

                    citations = []
                    for ref in part['refs']:
                        citations.append(dict(identifier=None, range=ref))
                        
                    refCitations = loc.getField('referenceCitations')
                    refCitations.resize(len(prime['refs']), loc)
                    loc.update(referenceCitations=citations)

                    times = []
                    for period in part['periods']:
                        if period.endswith('?'):
                            times.append(
                                dict(timePeriod=period_ids[period[0]], 
                                     confidence='less-confident'))
                        else:
                            times.append(
                                dict(timePeriod=period_ids[period], 
                                     confidence='confident'))
                    timePeriods = loc.getField('attestations')
                    timePeriods.resize(len(times), loc)
                    loc.update(attestations=times)

        except:
            savepoint.rollback()
            raise
        
        transaction.commit()
