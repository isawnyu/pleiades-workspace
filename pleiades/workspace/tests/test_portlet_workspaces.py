from zope.component import getUtility, getMultiAdapter
from plone.portlets.interfaces import IPortletType
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletRenderer
from plone.app.portlets.storage import PortletAssignmentMapping
from pleiades.workspace.interfaces import IResource
from pleiades.workspace.portlets import workspaces
from pleiades.workspace.tests.base import WorkspaceTestCase, WorkspaceFunctionalTestCase

class TestPortlet(WorkspaceTestCase):

    def afterSetUp(self):
        self.setRoles(('Manager',))

    def testPortletTypeRegistered(self):
        portlet = getUtility(IPortletType, name='pleiades.Workspaces')
        self.assertEquals(portlet.addview, 'pleiades.Workspaces')

    def testInterfaces(self):
        portlet = workspaces.Assignment()
        self.failUnless(IPortletAssignment.providedBy(portlet))
        self.failUnless(IPortletDataProvider.providedBy(portlet.data))

    def testInvokeAddview(self):
        portlet = getUtility(IPortletType, name='pleiades.Workspaces')
        mapping = self.portal.restrictedTraverse('++contextportlets++plone.leftcolumn')
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse('+/' + portlet.addview)

        addview.createAndAdd(data={})

        self.assertEquals(len(mapping), 1)
        self.failUnless(isinstance(mapping.values()[0], workspaces.Assignment))

    def testInvokeEditView(self):
        mapping = PortletAssignmentMapping()
        request = self.folder.REQUEST

        mapping['foo'] = workspaces.Assignment()
        editview = getMultiAdapter((mapping['foo'], request), name='edit')
        self.failUnless(isinstance(editview, workspaces.EditForm))

    def testRenderer(self):
        context = self.folder
        request = self.folder.REQUEST
        view = self.folder.restrictedTraverse('@@plone')
        manager = getUtility(IPortletManager, name='plone.rightcolumn', context=self.portal)
        assignment = workspaces.Assignment()

        renderer = getMultiAdapter((context, request, view, manager, assignment), IPortletRenderer)
        self.failUnless(isinstance(renderer, workspaces.Renderer))

class TestRenderer(WorkspaceFunctionalTestCase):
    
    def afterSetUp(self):
        WorkspaceFunctionalTestCase.afterSetUp(self)
        self.portal.invokeFactory('Workspace Folder', 'workspaces')
        self.portal['workspaces'].invokeFactory('Workspace', 'ws1')
        pid = self.portal['places'].invokeFactory('Place', '0', title='Test')
        self.place = self.portal['places'][pid]
        self.workspace = self.portal['workspaces']['ws1']
        self.workspace.attach(self.place)

    def renderer(self, context=None, request=None, view=None, manager=None, assignment=None):
        context = context or self.folder
        request = request or self.folder.REQUEST
        view = view or self.folder.restrictedTraverse('@@plone')
        manager = manager or getUtility(IPortletManager, name='plone.rightcolumn', context=self.portal)
        assignment = assignment or workspaces.Assignment()

        return getMultiAdapter((context, request, view, manager, assignment), IPortletRenderer)

    def test_renderer(self):
        r = self.renderer(context=self.place)
        ws_url = self.workspace.absolute_url()
        self.failUnless(ws_url in [p['url'] for p in r.workspaces()])

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPortlet))
    suite.addTest(makeSuite(TestRenderer))
    return suite
