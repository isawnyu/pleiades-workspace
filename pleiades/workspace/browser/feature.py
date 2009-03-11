import transaction
from Products.CMFCore.utils import getToolByName
from zope.interface import Interface, Invalid, invariant
from zope import schema
from z3c.form import form, field, button
from plone.app.z3cform.layout import wrap_form

from pleiades.workspace.interfaces import IResource


class IAddNamed(Interface):
    """Feature or Place adding interface
    """
    title = schema.TextLine(title=u"Title", description=u"Enter a title for the feature or place. It may be subsequently changed.", required=True)
    portal_type = schema.Choice(title=u"Portal type", description=u"Select portal content type.", required=True, values=['Feature', 'Place'], default='Feature')


class Form(form.Form):
    fields = field.Fields(IAddNamed)
    ignoreContext = True # don't use context to get widget data
    label = u"Add an ancient place or feature to this workspace"
    
    @button.buttonAndHandler(u'Apply')
    def handleApply(self, action):
        data, errors = self.extractData()
        factory = NamedFactory(self.context, self.request)
        oid, to_url = factory(data['title'], data['portal_type'])
        response = self.request.response
        response.setStatus(201)
        response.setHeader(
            'Location',
            '%s/base_edit' % to_url
            )
        response.redirect('%s/base_edit' % to_url)


AddNamedForm = wrap_form(Form)


class NamedFactory(object):
    
    """Feature/Place adding view
    """
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
    
    def __call__(self, title, portal_type):        
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        ptool = getToolByName(self.context, 'plone_utils')
        wtool = getToolByName(self.context, 'portal_workflow')
        containers = {
            'Place': portal['places'],
            'Feature': portal['features']
            }
        oid = containers[portal_type].invokeFactory(portal_type, containers[portal_type].generateId(prefix=''), title=title)
        ob = containers[portal_type][oid]
        self.context.attach(ob)
        return (oid, ob.absolute_url())
