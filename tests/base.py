
from __future__ import absolute_import

import unittest

from mock import MagicMock

from braspag import BraspagRequest


class BraspagTestCase(unittest.TestCase):

    def setUp(self):
        merchant_id = '12345678-1234-1234-1234-1234567890AB'
        self.braspag = BraspagRequest(merchant_id=merchant_id)
        self.braspag._request = MagicMock()
