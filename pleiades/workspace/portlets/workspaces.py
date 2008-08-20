"""Define a portlet used to show promotions. This follows the patterns from
plone.app.portlets.portlets. Note that we also need a portlet.xml in the
GenericSetup extension profile to tell Plone about our new portlet.
"""

import random

from zope import schema
from zope.component import getMultiAdapter
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

# This interface defines the configurable options (if any) for the portlet.
# It will be used to generate add and edit forms.

class IWorkspacesPortlet(IPortletDataProvider):

    count = schema.Int(title=_(u'Number of promotions to display'),
                       description=_(u'Maximum number of promotions to be shown'),
                       required=True,
                       default=5)
                       
# The assignment is a persistent object used to store the configuration of
# a particular instantiation of the portlet.

class Assignment(base.Assignment):
    implements(IWorkspacesPortlet)

    def __init__(self, count=5):
        self.count = count

    @property
    def title(self):
        return _(u"Workspaces")

# The renderer is like a view (in fact, like a content provider/viewlet). The
# item self.data will typically be the assignment (although it is possible
# that the assignment chooses to return a different object - see 
# base.Assignment).

class Renderer(base.Renderer):

    # render() will be called to render the portlet
    
    render = ViewPageTemplateFile('workspaces.pt')
       
    # The 'available' property is used to determine if the portlet should
    # be shown.
        
    @property
    def available(self):
        return len(self._data()) > 0

    # To make the view template as simple as possible, we return dicts with
    # only the necessary information.

    def workspaces(self):
        for brain in self._data():
            workspace = brain.getObject()
            yield dict(title=workspace.title,
                       summary=workspace.description,
                       url=brain.getURL()
                       )
        
    # By using the @memoize decorator, the return value of the function will
    # be cached. Thus, calling it again does not result in another query.
    # See the plone.memoize package for more.
        
    @memoize
    def _data(self):
        context = aq_inner(self.context)
        #limit = self.data.count
        
        r = IResource(context)
        query = dict(UID=r.wsuids)
        
        #if not self.data.sitewide:
        #    query['path'] = '/'.join(context.getPhysicalPath())
        #if not self.data.randomize:
        #    query['sort_on'] = 'modified'
        #    query['sort_order'] = 'reverse'
        #    query['sort_limit'] = limit
        
        # Ensure that we only get active objects, even if the user would
        # normally have the rights to view inactive objects (as an
        # administrator would)
        query['effectiveRange'] = DateTime()
        
        catalog = getToolByName(context, 'portal_catalog')
        return list(catalog(query))

# Define the add forms and edit forms, based on zope.formlib. These use
# the interface to determine which fields to render.

class AddForm(base.AddForm):
    form_fields = form.Fields(IWorkspacesPortlet)
    label = _(u"Add Workspaces portlet")
    description = _(u"This portlet displays data workspaces.")

    # This method must be implemented to actually construct the object.
    # The 'data' parameter is a dictionary, containing the values entered
    # by the user.

    def create(self, data):
        assignment = Assignment()
        form.applyChanges(assignment, self.form_fields, data)
        return assignment

class EditForm(base.EditForm):
    form_fields = form.Fields(IWorkspacesPortlet)
    label = _(u"Edit Workspaces portlet")
    description = _(u"This portlet displays data workspaces.")
