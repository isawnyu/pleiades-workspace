from zope.interface import implements
from zope.component import adapter, getMultiAdapter, getUtility
from zope.event import notify

from zope.app.container.interfaces import INameChooser

from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignmentMapping

from Acquisition import aq_inner, aq_parent

from Products.Archetypes import atapi
from Products.Archetypes.interfaces import IObjectInitializedEvent

from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content.schemata import finalizeATCTSchema

from pleiades.workspace.config import PROJECTNAME
from pleiades.workspace.i18n import WorkspaceMessageFactory as _

from Products.PleiadesEntity.content.PlaceContainer import PlaceContainer
from Products.PleiadesEntity.content.LocationContainer import LocationContainer

from pleiades.workspace.interfaces import IResource, IWorkspace
from pleiades.workspace.event import ResourceModifiedEvent

# This is the Archetypes schema, defining fields and widgets. We extend
# the one from ATContentType's ATFolder with our additional fields.
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

# We want to ensure that the properties we use as field properties (see
# below), use AnnotationStorage. Without this, our property will conflict
# with the attribute with the same name that is being managed by the default
# attributestorage

WorkspaceSchema['title'].storage = atapi.AnnotationStorage()
WorkspaceSchema['description'].storage = atapi.AnnotationStorage()
    
# Calling this re-orders a few fields to comply with Plone conventions.
finalizeATCTSchema(WorkspaceSchema, folderish=True, moveDiscussion=False)

class Workspace(folder.ATFolder):
    """Contains multiple cinemas
    
    Can also contain promotions, which will then apply to all cinemas in
    this folder, and other cinema folders to allow cinemas to be grouped
    into sub-groups.
    """
    implements(IWorkspace)
    
    # The portal type name must be set here, matching the one in types.xml
    # in the GenericSetup profile
    portal_type = "Workspace"
    
    # This enables Archetypes' standard title-to-id renaming machinery
    # If you need different semantics, it's possible to override the method
    # _renameAfterCreation() from BaseObject
    _at_rename_after_creation = True
    
    # We then associate the schema with our content type
    schema = WorkspaceSchema
    
    # Our interface specifies that we should use simple Python properties
    # for various fields. To simplify creating these, we can map them to 
    # the Archetypes schema, using an ATFieldProperty. Note, however,
    # that the default Archetypes storage is AttributeStorage. If the name
    # of the property and the name of the corresponding field are the same,
    # these may conflict. Therefore, we explicitly switch the 'title' and
    # 'description' fields (which are inherited from Archetypes' 
    # ExtensibleMetadata mix-in class) to AnnotationStorage above.
    
    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    text = atapi.ATFieldProperty('text')

    def initTopic(self, oid, type):
        topic = self[oid]
        c = topic.addCriterion('pleiades_wsuids', 'ATSimpleStringCriterion')
        c.setValue(self.UID())
        c = topic.addCriterion('Type', 'ATPortalTypeCriterion')
        c.setValue(type)

    def initializeArchetype(self, **kwargs):
        tid = self.invokeFactory('Topic', id='locations', title='Locations')
        self.initTopic(tid, 'Location')
        tid = self.invokeFactory('Topic', id='names', title='Names')
        self.initTopic(tid, 'Name')
        tid = self.invokeFactory('Topic', id='features', title='Features')
        self.initTopic(tid, 'Feature')
        tid = self.invokeFactory('Topic', id='places', title='Places')
        self.initTopic(tid, 'Place')

    def attach(self, ob):
        IResource(ob).wsuids = [self.UID()]
        notify(ResourceModifiedEvent(ob))

    def detach(self, ob):
        IResource(ob).wsuids = []
        notify(ResourceModifiedEvent(ob))


# This line tells Archetypes about the content type
atapi.registerType(Workspace, PROJECTNAME)

