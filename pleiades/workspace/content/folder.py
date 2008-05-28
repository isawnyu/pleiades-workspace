"""Definition of the CinemaFolder content type and associated schemata and
other logic.

This file contains a number of comments explaining the various lines of
code. Other files in this sub-package contain analogous code, but will 
not be commented as heavily.

Please see README.txt for more information on how the content types in
this package are used.
"""

from zope.interface import implements
from zope.component import adapter, getMultiAdapter, getUtility

from zope.app.container.interfaces import INameChooser

from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignmentMapping

from Acquisition import aq_inner, aq_parent

from Products.Archetypes import atapi
from Products.Archetypes.interfaces import IObjectInitializedEvent

from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content.schemata import finalizeATCTSchema

from pleiades.workspace.interfaces import IWorkspaceFolder
from pleiades.workspace.config import PROJECTNAME
from pleiades.workspace import WorkspaceMessageFactory as _

from Products.PleiadesEntity.content.PlaceContainer import PlaceContainer
from Products.PleiadesEntity.content.LocationContainer import LocationContainer

# This is the Archetypes schema, defining fields and widgets. We extend
# the one from ATContentType's ATFolder with our additional fields.
WorkspaceFolderSchema = folder.ATFolderSchema.copy() + atapi.Schema((
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

WorkspaceFolderSchema['title'].storage = atapi.AnnotationStorage()
WorkspaceFolderSchema['description'].storage = atapi.AnnotationStorage()
    
# Calling this re-orders a few fields to comply with Plone conventions.
finalizeATCTSchema(WorkspaceFolderSchema, folderish=True, moveDiscussion=False)

class WorkspaceFolder(folder.ATFolder):
    """Contains multiple workspaces
    """
    implements(IWorkspaceFolder)
    
    # The portal type name must be set here, matching the one in types.xml
    # in the GenericSetup profile
    portal_type = "Workspace Folder"
    
    # This enables Archetypes' standard title-to-id renaming machinery
    # If you need different semantics, it's possible to override the method
    # _renameAfterCreation() from BaseObject
    _at_rename_after_creation = True
    
    # We then associate the schema with our content type
    schema = WorkspaceFolderSchema
    
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

# This line tells Archetypes about the content type
atapi.registerType(WorkspaceFolder, PROJECTNAME)
