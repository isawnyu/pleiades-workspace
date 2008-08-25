import glob
from os.path import basename
from elementtree import ElementTree as etree
import transaction
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
import keytree
from Products.PleiadesEntity.Extensions.loader import load_place
from pleiades.workspace.interfaces import IResource


class XMLImporter(BrowserView):
    
    """XML importing view
    """

    def __call__(self):
        request = self.request
        sourcedir = request.form.get('sourcedir', None)
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        places = portal['places']
        features = portal['features']
        names = portal['names']
        locations = portal['locations']
        failures = []
        count = 0
        for xml in glob.glob("%s/*.xml" % sourcedir):
            try:
                result = load_place(portal, xml)
                for nid in result['name_ids']:
                    self.context.attach(names[nid])
                for lid in result['location_ids']:
                    self.context.attach(locations[lid])
                for fid in result['feature_ids']:
                    self.context.attach(features[fid])
                self.context.attach(places[result['place_id']])
                count += 1
            except Exception, e:
                failures.append([basename(xml), str(e)])
    
        if len(failures) == 0:
            return "Loaded %d of %d files." % (count, count)
        else:
            msg = "Loaded %d of %d files. Failures:\n" % (count, count + len(failures))
            for f in failures:
                msg += "%s\n" % str(f)
            return msg


class XMLImportForm(BrowserView):

    __call__ = ViewPageTemplateFile('import_xml_form.pt')

