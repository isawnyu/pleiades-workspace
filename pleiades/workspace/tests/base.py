from Products.Five import zcml
from Products.Five import fiveconfigure

from Testing import ZopeTestCase as ztc

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

from pleiades.workspace.content.workspace import initTypeTopic, initStateTopic

ztc.installProduct('ATVocabularyManager')
ztc.installProduct('Products.ATBackRef')
ztc.installProduct('Products.CompoundField')
ztc.installProduct('PleiadesEntity')


@onsetup
def setup_pleiades_workspace():
    fiveconfigure.debug_mode = True
    import pleiades.workspace
    zcml.load_config('configure.zcml', pleiades.workspace)
    fiveconfigure.debug_mode = False
    ztc.installPackage('pleiades.workspace')

setup_pleiades_workspace()
ptc.setupPloneSite(products=['ATVocabularyManager', 'Products.ATBackRef', 'Products.CompoundField', 'PleiadesEntity', 'pleiades.workspace'])


class WorkspaceTestCase(ptc.PloneTestCase):
    """Base class used for test cases
    """

class WorkspaceFunctionalTestCase(ptc.FunctionalTestCase):
    """Test case class used for functional (doc-)tests
    """
    
    def afterSetUp(self):
        
        pt = self.portal.portal_types
        wf = pt['Workspace Folder']
        wf_allow = wf.global_allow
        wf.global_allow = True
        
        lpf = pt['Large Plone Folder']
        lpf_allow = lpf.global_allow
        lpf.global_allow = True
        
        self.setRoles(('Manager', 'Contributor'))
        
        try:
            self.portal.invokeFactory('FeatureContainer', id='features')
            self.portal['features'].invokeFactory('Folder', id='metadata')
            self.portal.invokeFactory('PlaceContainer', id='places')
            mid = self.portal['features']['metadata'].invokeFactory('PositionalAccuracy', id='cap-map65')
            self.portal['features']['metadata'][mid].setValue(0.01)
            self.portal['features']['metadata'][mid].setText("That's right, 1 cm!")
        except:
            raise


class ContentFunctionalTestCase(ptc.FunctionalTestCase):
    
    def afterSetUp(test):
        test.setRoles(('Manager', 'Contributor'))
        pt = test.portal.portal_types
        for type in [
            'Topic',
            'PlaceContainer',
            'FeatureContainer',
            'Workspace Folder',
            'Workspace',
            'Workspace Collection',
            'Place',
            'Feature',
            ]:
            lpf = pt[type]
            lpf.global_allow = True
        
        test.portal.invokeFactory(
            'Workspace Folder', id='workspaces', title='Workspaces'
            )
        test.portal.invokeFactory(
            'PlaceContainer', id='places', title='Places',
            description='All Places'
            )
        test.portal.invokeFactory(
            'FeatureContainer', id='features', title='Features'
            )
        test.portal['features'].invokeFactory('Folder', id='metadata')
        mid = test.portal['features']['metadata'].invokeFactory('PositionalAccuracy', id='cap-map65')
        test.portal['features']['metadata'][mid].setValue(0.01)
        test.portal['features']['metadata'][mid].setText("That's right, 1 cm!")
        test.features = test.portal['features']
        test.places = test.portal['places']
        test.workspaces = test.portal['workspaces']
        
        # Add feature
        fid = test.features.invokeFactory('Feature', '1', title='Ninoe', featureType='settlement')
        f = test.features[fid]
        nameAttested = u'\u039d\u03b9\u03bd\u1f79\u03b7'.encode('utf-8')
        nid = f.invokeFactory('Name', 'ninoe', nameAttested=nameAttested, nameLanguage='grc', nameType='geographic', accuracy='accurate', completeness='complete')
        attestations = f[nid].Schema()['attestations']
        attestations.resize(1)
        f[nid].update(attestations=[dict(confidence='certain', timePeriod='roman')])
        lid = f.invokeFactory('Location', 'location', title='Point 1', geometry='Point:[-86.4808333333333, 34.769722222222]')
        
        # Add place
        
        pid = test.places.invokeFactory('Place', '1', title='Ninoe')
        p = test.places[pid]
        nid = p.invokeFactory('Name', 'ninoe', nameAttested=nameAttested, nameLanguage='grc', nameType='geographic', accuracy='accurate', completeness='complete')
        attestations = p[nid].Schema()['attestations']
        attestations.resize(1)
        p[nid].update(attestations=[dict(confidence='certain', timePeriod='roman')])
        
        # And references
        f.addReference(p, 'feature_place')
        
        f.reindexObject()
        p.reindexObject()
        
        # Add a workspace
        wsid = test.workspaces.invokeFactory('Workspace', 'test-ws', title='Test Workspace')
        ob = test.workspaces[wsid]
        # from zope.event import notify
        # from Products.Archetypes.event import ObjectInitializedEvent
        # notify(ObjectInitializedEvent(ob))
        wsuid = ob.UID()
        for s in ['private', 'pending', 'published']:
            sid = ob.invokeFactory(
                    'Workspace Collection', id=s, title=s.capitalize()
                    )
            topic = ob[sid]
            initStateTopic(topic, s, wsuid)
        ob.attach(f)
        ob.attach(p)
