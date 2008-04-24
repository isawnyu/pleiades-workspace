from Acquisition import aq_inner
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from pleiades.workspace.interfaces import IWorkspace
from plone.memoize.instance import memoize 


class WorkspaceView(BrowserView):
    """Default view of a workspace
    """
    
    __call__ = ViewPageTemplateFile('workspace.pt')
    
    # Methods called from the associated template
    
    # The memoize decorator means that the function will be executed only
    # once (for a given set of arguments, but in this case there are no
    # arguments). On subsequent calls, the return value is looked up from a
    # cache, meaning we can call this function several times without a 
    # performance hit.
   
    def have_cinema_folders(self):
        return False

    #@memoize
    #def cinema_folders(self):
    #    context = aq_inner(self.context)
    #    catalog = getToolByName(context, 'portal_catalog')
    #    return [ dict(url=cinema_folder.getURL(),
    #                  title=cinema_folder.Title,
    #                  description=cinema_folder.Description,)
    #             for cinema_folder in 
    #                catalog(object_provides=ICinemaFolder.__identifier__,
    #                        path=dict(query='/'.join(context.getPhysicalPath()),
    #                                  depth=1),
    #                        sort_on='sortable_title')
    #           ]
    
    def have_cinemas(self):
        return False

    #@memoize
    #def cinemas(self):
    #    context = aq_inner(self.context)
    #    catalog = getToolByName(context, 'portal_catalog')
        
        # Note that we are cheating a bit here - to avoid having to "wake up"
        # the cinema object, we rely on our implementation that uses the 
        # Dublin Core Title and Description fields as title and address,
        # respectively. To rely only on the interface and not the 
        # implementation, we'd need to call getObject() and then use the
        # associated attributes of the interface, or we could add new catalog
        # metadata for these fields (with a catalog.xml GenericSetup file).

    #    return [ dict(url=cinema.getURL(),
    #                  title=cinema.Title,
    #                  address=cinema.Description,)
    #             for cinema in 
    #                catalog(object_provides=ICinema.__identifier__,
    #                        path=dict(query='/'.join(context.getPhysicalPath()),
    #                                  depth=1),
    #                        sort_on='sortable_title')
    #           ]
