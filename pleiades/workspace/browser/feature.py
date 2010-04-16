import transaction
from Products.CMFCore.utils import getToolByName
from zope.interface import Interface, Invalid, invariant
from zope import schema
from z3c.form import interfaces, form, field, button
from plone.app.z3cform.layout import wrap_form

from pleiades.workspace.interfaces import IResource

TYPES = {
    'Ancient Place': 'Place',
    'Positional Accuracy Assessment': 'PositionalAccuracy',
}

class IAddNamed(Interface):
    """Feature or Place adding interface
    """
    title = schema.TextLine(
            title=u"Title", 
            description=u"The title of the new item", required=True)
    portal_type = schema.Choice(
                        title=u"Portal type", 
                        description=u"The type of the new item", 
                        required=True, 
                        values=['Positional Accuracy Assessment', 
                                'Ancient Place'], 
                        default='Positional Accuracy Assessment')


class Form(form.Form):
    fields = field.Fields(IAddNamed)
    ignoreContext = True # don't use context to get widget data
    label = u"Add an item to workspace"
    formErrorsMessage = u'Invalid title or id'

    @button.buttonAndHandler(u'Apply')
    def handleApply(self, action):
        data, errors = self.extractData()
        ptname = TYPES[data['portal_type']]
        factory = NamedFactory(self.context, self.request)
        try:
            oid, to_url = factory(data['title'], ptname)
        except KeyError:
            raise interfaces.WidgetActionExecutionError('title', 
                Invalid('Id already exists'))

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
        #    'Feature': portal['features'],
            'PositionalAccuracy': portal['features']['metadata'],
            }
        if portal_type in ['Place', 'Feature']:
            oid = containers[portal_type].invokeFactory(
                portal_type, containers[portal_type].generateId(prefix=''), 
                title=title)
        else:
            if ptool.normalizeString(title) in containers[portal_type]:
                raise KeyError, "Id already exists"
            oid = containers[portal_type].invokeFactory(
                portal_type, ptool.normalizeString(title), title=title)
        ob = containers[portal_type][oid]
        ob.setTitle(title)
        self.context.attach(ob)
        return (oid, ob.absolute_url())
