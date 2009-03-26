import unittest
import doctest
from zope.testing import doctestunit
import zope.component.eventtesting
from Testing import ZopeTestCase as ztc
from pleiades.workspace.tests import base

optionflags = (
    doctest.REPORT_ONLY_FIRST_FAILURE |
    doctest.NORMALIZE_WHITESPACE |
    doctest.ELLIPSIS
    )

def test_suite():
    return unittest.TestSuite([
        ztc.ZopeDocFileSuite(
            'factory.txt',
            package='pleiades.workspace.tests',
            test_class=base.WorkspaceFunctionalTestCase,
            optionflags=optionflags
            ),
        ztc.ZopeDocFileSuite(
            'workspaces.txt',
            package='pleiades.workspace.tests',
            test_class=base.WorkspaceFunctionalTestCase,
            optionflags=optionflags
            ),
        ztc.ZopeDocFileSuite(
            'kml-import.txt',
            package='pleiades.workspace.tests',
            test_class=base.WorkspaceFunctionalTestCase,
            optionflags=optionflags
            ),
        # ztc.ZopeDocFileSuite(
        #             'xml-import.txt',
        #             package='pleiades.workspace.tests',
        #             test_class=base.WorkspaceFunctionalTestCase,
        #             optionflags=optionflags
        #             ),
        ztc.ZopeDocFileSuite(
            'add-feature.txt',
            package='pleiades.workspace.tests',
            test_class=base.WorkspaceFunctionalTestCase,
            optionflags=optionflags
            ),
        ztc.ZopeDocFileSuite(
            'manage.txt',
            package='pleiades.workspace.tests',
            test_class=base.ContentFunctionalTestCase,
            optionflags=optionflags
            ),            
        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
