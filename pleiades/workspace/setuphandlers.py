from Products.CMFCore.utils import getToolByName

def setupVarious(context):
    if context.readDataFile('pleiades.workspace_various.txt') is None:
        return
    portal = context.getSite()
    addToCatalog(portal)

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
