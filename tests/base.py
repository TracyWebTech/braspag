
from __future__ import absolute_import

import re
import codecs
import unittest

from mock import MagicMock

from braspag import BraspagRequest


class BraspagTestCase(unittest.TestCase):

    def setUp(self):
        merchant_id = '12345678-1234-1234-1234-1234567890AB'
        self.braspag = BraspagRequest(merchant_id=merchant_id)
        self.braspag._request = MagicMock()


class RegexpMatcher(object):
    def __init__(self, data_filepath):
        with codecs.open(data_filepath, 'rb', encoding='utf-8') as data_file:
            self.data = data_file.read().strip()

    def __eq__(self, other):
        if not isinstance(other, basestring):
            return False

        if not re.match(self.data, other):
            return False

        return True

    def __unicode__(self):
        return self.data

    def __repr__(self):
        return repr(unicode(self))
