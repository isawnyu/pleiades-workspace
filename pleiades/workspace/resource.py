import logging
from zope.interface import implements
from zope.annotation.interfaces import IAnnotations
from zope.component.interfaces import ComponentLookupError
from zope.event import notify
from persistent.dict import PersistentDict
from pleiades.workspace.interfaces import IResource
from pleiades.workspace.event import ResourceModifiedEvent

logger = logging.getLogger('pleiades.workspace.resource')

KEY = 'pleiades.workspace'


class Resource(object):

    implements(IResource)

    def __init__(self, context):
        self.context = context
        annotations = IAnnotations(context)
        self.anno = annotations.get(KEY, None)
        if not self.anno:
            annotations[KEY] = PersistentDict()
            self.anno = annotations[KEY]
            self.anno['wsuids'] = []

    def attach(self, workspace):
        self.anno['wsuids'].append(workspace.UID())
        notify(ResourceModifiedEvent(self.context))

    def detach(self, workspace):
        self.anno['wsuids'].remove(workspace.UID())
        notify(ResourceModifiedEvent(self.context))

    @property
    def wsuids(self):
        return self.anno['wsuids']


def pleiades_wsuids_value(object, portal, **kwargs):
    try:
        resource = IResource(object)
        return list(resource.wsuids)
    except (ComponentLookupError, TypeError, ValueError, KeyError, IndexError):
 	# The catalog expects AttributeErrors when a value can't be found
        raise AttributeError
