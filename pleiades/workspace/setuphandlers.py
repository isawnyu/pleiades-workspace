from zope.component.interfaces import ComponentLookupError
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.CatalogTool import registerIndexableAttribute
from pleiades.workspace.interfaces import IResource

def setupVarious(context):
    if context.readDataFile('pleiades.workspace_various.txt') is None:
        return
    portal = context.getSite()
    addToCatalog(portal)

def pleiades_wsids_value(object, portal, **kwargs):
    try:
        resource = IResource(object)
        return list(resource.wsuids)
    except (ComponentLookupError, TypeError, ValueError, KeyError):
 	# The catalog expects AttributeErrors when a value can't be found
        raise AttributeError

registerIndexableAttribute('pleiades_wsuids', pleiades_wsids_value)

def addToCatalog(portal):
    cat = getToolByName(portal, 'portal_catalog', None)
    metadata = [('pleiades_wsuids', 'KeywordIndex'),]
    reindex = []
    if cat is not None:
        for column, type in metadata:
            if column in cat.schema():
                continue
            cat.addIndex(column, type)
            cat.addColumn(column)
            reindex.append(column)
        if reindex:
            cat.refreshCatalog()
