from Acquisition import aq_inner
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from pleiades.workspace.interfaces import IWorkspace, IWorkspaceCollection
from plone.memoize.instance import memoize


class WorkspaceView(BrowserView):
    """Default view of a workspace
    """
    
    __call__ = ViewPageTemplateFile('workspace.pt')
    
    @memoize
    def collections_data(self):
        data = {}
        for name in ['features', 'places', 'metadata', 'citations']:
            row = {}
            for state in ['drafting', 'pending', 'published']:
                collection = self.context[name][state]
                url = collection.absolute_url()
                brains = collection.queryCatalog()
                row[state] = dict(count=len(brains), url=url)
            
            # Now the column of all states
            collection = self.context[name]
            url = collection.absolute_url()
            brains = collection.queryCatalog()
            row['all'] = dict(count=len(brains), url=url)
            data[name] = row
        
        # final row
        row = {}
        for state in ['drafting', 'pending', 'published']:
            collection = self.context[state]
            url = collection.absolute_url()
            brains = collection.queryCatalog()
            row[state] = dict(count=len(brains), url=url)
        data['all'] = row
        
        return data