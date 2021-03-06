from zope.interface import implements
from zope.component import adapter
from zope.event import notify

from Products.Archetypes import atapi
from Products.Archetypes.interfaces import IObjectInitializedEvent
from Products.ATContentTypes.content import folder, topic
from Products.ATContentTypes.content.schemata import finalizeATCTSchema

from Products.PleiadesEntity.content.PlaceContainer import PlaceContainer

from pleiades.workspace.config import PROJECTNAME
from pleiades.workspace.i18n import WorkspaceMessageFactory as _
from pleiades.workspace.interfaces import IResource, IWorkspace, IWorkspaceCollection
from pleiades.workspace.event import ResourceModifiedEvent


class WorkspaceCollection(topic.ATTopic):
    """Specialized topic.
    """
    implements(IWorkspaceCollection)
    portal_type = "Workspace Collection"
    
    @property
    def members(self):
        for brain in self.queryCatalog():
            yield brain.getObject()


WorkspaceSchema = folder.ATFolderSchema.copy() + atapi.Schema((
    atapi.TextField('text',
        required=False,
        searchable=True,
        storage=atapi.AnnotationStorage(),
        validators=('isTidyHtmlWithCleanup',),
        default_output_type='text/x-html-safe',
        widget=atapi.RichWidget(label=_(u"Descriptive text"),
                                description=_(u""),
                                rows=25,
                                allow_file_upload=False),
        ),
    ))

WorkspaceSchema['title'].storage = atapi.AnnotationStorage()
WorkspaceSchema['description'].storage = atapi.AnnotationStorage()

finalizeATCTSchema(WorkspaceSchema, folderish=True, moveDiscussion=False)


class Workspace(folder.ATFolder):
    
    """Collects content so their workflow states can be changed in bulk.
    """
    
    implements(IWorkspace)
    
    portal_type = "Workspace"
    
    _at_rename_after_creation = True
    
    schema = WorkspaceSchema
    
    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    text = atapi.ATFieldProperty('text')
    
    def attach(self, ob):
        IResource(ob).wsuids = [self.UID()]
        notify(ResourceModifiedEvent(ob))
    
    def detach(self, ob):
        IResource(ob).wsuids = []
        notify(ResourceModifiedEvent(ob))


# This line tells Archetypes about the content type
atapi.registerType(Workspace, PROJECTNAME)
atapi.registerType(WorkspaceCollection, PROJECTNAME)


def initTypeTopic(topic, portal_type, wsuid, acquire=True):
    topic.setAcquireCriteria(acquire)
    c = topic.addCriterion('pleiades_wsuids', 'ATSimpleStringCriterion')
    c.setValue(wsuid)
    c = topic.addCriterion('portal_type', 'ATPortalTypeCriterion')
    c.setValue(portal_type)

def initStateTopic(topic, state, wsuid, acquire=True):
    topic.setAcquireCriteria(acquire)
    c = topic.addCriterion('pleiades_wsuids', 'ATSimpleStringCriterion')
    c.setValue(wsuid)
    c = topic.addCriterion('review_state', 'ATSimpleStringCriterion')
    c.setValue(state)


@adapter(IWorkspace, IObjectInitializedEvent)
def add_workspace_collections(ob, event):
    types = [
        ('features', 'Feature'),
        ('places', 'Place'),
        ('metadata', 'PositionalAccuracy'),
        ]
    states = ['drafting', 'pending', 'published']
    wsuid = ob.UID()
    for name, tname in types:
        tid = ob.invokeFactory(
                'Workspace Collection', id=name, title=name.capitalize()
                )
        topic = ob[tid]
        initTypeTopic(topic, tname, wsuid)
        for s in states:
            sid = topic.invokeFactory(
                    'Workspace Collection', id=s, title=s.capitalize()
                    )
            subtopic = topic[sid]
            initStateTopic(subtopic, sid, wsuid, True)
    for s in states:
        sid = ob.invokeFactory(
                'Workspace Collection', id=s, title=s.capitalize()
                )
        topic = ob[sid]
        initStateTopic(topic, s, wsuid)
        for name, tname in types:
            tid = topic.invokeFactory(
                    'Workspace Collection', id=name, title=name.capitalize()
                    )
            subtopic = topic[tid]
            initTypeTopic(subtopic, tname, wsuid, True)
    
    ob.plone_utils.addPortalMessage(_(u'Adding a positional accuracy assessment is a good way to begin.'))
