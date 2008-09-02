from Acquisition import aq_inner, aq_parent
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from plone.memoize.instance import memoize 
from pleiades.workspace.interfaces import IResource, IWorkspace

class ManageCollection(BrowserView):
    
    def __call__(self):
        context = self.context
        request = self.request
        response = request.response
        transition = self.request.form['transition']
        wftool = getToolByName(self.context, 'portal_workflow')
        
        members = [b.getObject() for b in self.context.queryCatalog()]
        for ob in members:
            wftool.doActionFor(ob, action=transition)
        
        new_state = wftool.getInfoFor(members[0], 'review_state')

        # acquire the parent workspace
        workspace = None
        child = aq_inner(self.context)
        while 1:
            ob = aq_parent(child)
            if IWorkspace.providedBy(ob):
                workspace = ob
                break
            child = ob

        response.redirect('%s/%s' % (workspace.absolute_url(), new_state))


class ManageCollectionForm(BrowserView):

    __call__ = ViewPageTemplateFile('manage_collection_form.pt')

    @memoize
    def collects_state(self):
        return bool([k for k in self.context.keys() if 'review_state' in k])

    @memoize
    def transitions(self):
        wftool = getToolByName(self.context, 'portal_workflow')
        member = self.context.queryCatalog()[0].getObject()
        transitions = wftool.getTransitionsFor(member)
        return transitions
