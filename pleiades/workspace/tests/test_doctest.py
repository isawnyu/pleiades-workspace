import unittest
import doctest
from zope.testing import doctestunit
from zope.component import testing, eventtesting
from Testing import ZopeTestCase as ztc
from pleiades.workspace.tests import base


def test_suite():
    return unittest.TestSuite([
        ztc.ZopeDocFileSuite(
            'factory.txt',
            package='pleiades.workspace.tests',
            test_class=base.WorkspaceFunctionalTestCase,
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE | doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),
        ztc.ZopeDocFileSuite(
            'kml-import.txt',
            package='pleiades.workspace.tests',
            test_class=base.WorkspaceFunctionalTestCase,
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE | doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),
        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
