from Products.Five import zcml
from Products.Five import fiveconfigure

from Testing import ZopeTestCase as ztc

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

ztc.installProduct('ATVocabularyManager')
ztc.installProduct('PleiadesEntity')

@onsetup
def setup_pleiades_workspace():
    """Set up the additional products required for the Optilux Cinema Content.
    
    The @onsetup decorator causes the execution of this body to be deferred
    until the setup of the Plone site testing layer.
    """
    
    # Load the ZCML configuration for the optilux.policy package.
    # This includes the other products below as well.
    
    #fiveconfigure.debug_mode = True
    #import pleiades.workspace
    #zcml.load_config('configure.zcml', pleiades.workspace)
    #fiveconfigure.debug_mode = False
    
    # We need to tell the testing framework that these products
    # should be available. This can't happen until after we have loaded
    # the ZCML.
    
    ztc.installPackage('pleiades.workspace')
    
# The order here is important: We first call the (deferred) function which
# installs the products we need for the Optilux package. Then, we let 
# PloneTestCase set up this product on installation.

setup_pleiades_workspace()
ptc.setupPloneSite(products=['ATVocabularyManager', 'PleiadesEntity', 'pleiades.workspace'])

class WorkspaceTestCase(ptc.PloneTestCase):
    """Base class used for test cases
    """
        
class WorkspaceFunctionalTestCase(ptc.FunctionalTestCase):
    """Test case class used for functional (doc-)tests
    """

    def afterSetUp(test):
        pt = test.portal.portal_types
        wf = pt['Workspace Folder']
        wf_allow = wf.global_allow
        wf.global_allow = True

        lpf = pt['Large Plone Folder']
        lpf_allow = lpf.global_allow
        lpf.global_allow = True

        n = pt['Name']
        n_allow = n.global_allow
        n.global_allow = True

        try:
            test.setRoles(('Manager', 'Contributor'))
            test.portal.invokeFactory('Large Plone Folder', id='names')
            test.portal.invokeFactory('LocationContainer', id='locations')
            test.portal.invokeFactory('PlaceContainer', id='places')
        except:
            raise
