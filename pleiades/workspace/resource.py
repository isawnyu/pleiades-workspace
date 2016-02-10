from Acquisition import aq_parent
from persistent.dict import PersistentDict
from pleiades.workspace.interfaces import IResource
from plone.indexer import indexer
from zope.annotation.interfaces import IAnnotations
from zope.component.interfaces import ComponentLookupError
from zope.interface import implements
from zope.interface import Interface
import logging

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

    def _get_wsuids(self):
        return self.anno['wsuids']

    def _set_wsuids(self, value):
        self.anno['wsuids'] = value

    wsuids = property(_get_wsuids, _set_wsuids)


@indexer(Interface)
def pleiades_wsuids_value(object, portal, **kwargs):
    try:
        return list(IResource(object).wsuids) or list(IResource(aq_parent(object)).wsuids)
    except (ComponentLookupError, TypeError, ValueError, KeyError, IndexError):
        # The catalog expects AttributeErrors when a value can't be found
        raise AttributeError
