from zope.interface import implements

from Acquisition import aq_inner, aq_parent

from Products.Archetypes import atapi
from Products.Archetypes.interfaces import IObjectInitializedEvent

from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content.schemata import finalizeATCTSchema

from pleiades.workspace.interfaces import IWorkspaceFolder
from pleiades.workspace.config import PROJECTNAME
from pleiades.workspace.i18n import WorkspaceMessageFactory as _

from Products.PleiadesEntity.content.PlaceContainer import PlaceContainer


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

WorkspaceFolderSchema['title'].storage = atapi.AnnotationStorage()
WorkspaceFolderSchema['description'].storage = atapi.AnnotationStorage()

finalizeATCTSchema(WorkspaceFolderSchema, folderish=True, moveDiscussion=False)


class WorkspaceFolder(folder.ATFolder):
    """Contains multiple workspaces
    """
    implements(IWorkspaceFolder)
    
    portal_type = "Workspace Folder"
    
    _at_rename_after_creation = True
    
    schema = WorkspaceFolderSchema
    
    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    text = atapi.ATFieldProperty('text')

atapi.registerType(WorkspaceFolder, PROJECTNAME)
