from zope.interface import implements
from zope.lifecycleevent.interfaces import IObjectModifiedEvent


class IResourceModifiedEvent(IObjectModifiedEvent):
    """An event signaling that a resource has been attached or detached.
    """


class ResourceModifiedEvent(object):
    implements(IResourceModifiedEvent)
    
    def __init__(self, ob):
        self.object = ob


def reindexDocSubscriber(event):
    event.object.reindexObject()
