from zope.interface import Interface, Attribute
from zope import schema
from zope.app.container.constraints import contains

from pleiades.workspace.i18n import WorkspaceMessageFactory as _


class IResource(Interface):
    
    wsuids = Attribute("List of workspace UIDs")


class IWorkspace(Interface):
    """A container
    """
    contains('Products.PleiadesEntity.content.interfaces.ILocationContainer',
             'Products.PleiadesEntity.content.interfaces.IPlaceContainer',
             'Products.ATContentTypes.interfaces.IATFolder'
             )
    
    title = schema.TextLine(
                title=_(u"Title"),
                required=True
                )
    description = schema.TextLine(
                title=_(u"Description"),
                description=_(u"A short summary of this folder")
                )

    def attach(ob):
        """Attach object to a workspace."""

    def detach(ob):
        """Detach object from a workspace."""


class IWorkspaceFolder(Interface):
    """A container
    """
    contains('pleiades.workspace.interfaces.IWorkspace',
             'Products.ATContentTypes.interfaces.IATDocument'
             )
    
    title = schema.TextLine(
                title=_(u"Title"),
                required=True
                )
    description = schema.TextLine(
                title=_(u"Description"),
                description=_(u"A short summary of this folder")
                )
