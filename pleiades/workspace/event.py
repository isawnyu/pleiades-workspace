from zope.component import getUtility, getMultiAdapter
from zope.interface import implements
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from zope.app.container.interfaces import INameChooser
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignmentMapping
from pleiades.workspace.config import WORKSPACES_PORTLET_COLUMN
from pleiades.workspace.portlets.workspaces import Assignment


class IResourceModifiedEvent(IObjectModifiedEvent):
    """An event signaling that a resource has been attached or detached.
    """


class ResourceModifiedEvent(object):
    implements(IResourceModifiedEvent)
    
    def __init__(self, ob):
        self.object = ob


def reindexDocSubscriber(event):
    event.object.reindexObject()


def addWorkspacesPortlet(ob):
    column = getUtility(IPortletManager, name=WORKSPACES_PORTLET_COLUMN)
    manager = getMultiAdapter((ob, column), IPortletAssignmentMapping)
    assignment = Assignment()
    chooser = INameChooser(manager)
    manager[chooser.chooseName(None, assignment)] = assignment
