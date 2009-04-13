from zope import schema
from zope.formlib import form
from zope.interface import implements

from plone.app.portlets.portlets import base
from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider

from DateTime import DateTime
from Acquisition import aq_inner
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFCore.utils import getToolByName

from pleiades.workspace.interfaces import IWorkspace, IResource
from pleiades.workspace.i18n import WorkspaceMessageFactory as _


class IWorkspacesPortlet(IPortletDataProvider):
    """Workspace portlet
    """


class Assignment(base.Assignment):
    implements(IWorkspacesPortlet)
    
    title = _(u"Workspaces")
    
    def __init__(self):
        pass


class Renderer(base.Renderer):
    
    render = ViewPageTemplateFile('workspaces.pt')
    
    @property
    def available(self):
        return len(self._data()) > 0
    
    def workspaces(self):
        for brain in self._data():
            workspace = brain.getObject()
            yield dict(title=workspace.title,
                       summary=workspace.description,
                       url=brain.getURL()
                       )
    
    @memoize
    def _data(self):
        context = aq_inner(self.context)
        r = IResource(context)
        query = dict(UID=r.wsuids)
        query['effectiveRange'] = DateTime()
        catalog = getToolByName(context, 'portal_catalog')
        return list(catalog(query))


class AddForm(base.AddForm):
    form_fields = form.Fields(IWorkspacesPortlet)
    label = _(u"Add Workspaces portlet")
    description = _(u"This portlet displays data workspaces.")
    
    def create(self, data):
        assignment = Assignment()
        form.applyChanges(assignment, self.form_fields, data)
        return assignment


class EditForm(base.EditForm):
    form_fields = form.Fields(IWorkspacesPortlet)
    label = _(u"Edit Workspaces portlet")
    description = _(u"This portlet displays data workspaces.")
