# -*- coding: utf8 -*-

from __future__ import absolute_import

import re
import uuid
import codecs
import unittest

from xml.dom import minidom

from mock import MagicMock, Mock

from braspag import BraspagRequest
from braspag.utils import spaceless


VOID_DATA = 'tests/data/void_request.xml'
REFUND_DATA = 'tests/data/refund_request.xml'
CAPTURE_DATA = 'tests/data/capture_request.xml'


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

class BraspagRequestCancelTest(unittest.TestCase):

    def setUp(self):
        merchant_id = '12345678-1234-1234-1234-1234567890AB'
        self.data_dict = {
            'transaction_id': '782b632a-2dae-11e2-b3ee-080027d29772',
            'amount': '12330',
        }

        self.request = BraspagRequest(merchant_id=merchant_id)
        BraspagRequest._webservice_request = MagicMock(name='webservice_request')

    def test_void_render_template(self):
        self.request._render_template = MagicMock(name='_render_template')
        response = self.request.void(**self.data_dict)

        self.request._render_template.assert_called_once_with('base.xml',
            dict(self.data_dict.items() + [
                ('type', 'Void'),
            ])
        )

    def test_void_webservice_request(self):
        response = self.request.void(**self.data_dict)
        matcher = RegexpMatcher(VOID_DATA)
        BraspagRequest._webservice_request.\
                        assert_called_once_with(matcher, 'www.pagador.com.br')

    def test_refund_render_template(self):
        self.request._render_template = MagicMock(name='_render_template')
        response = self.request.refund(**self.data_dict)

        self.request._render_template.assert_called_once_with('base.xml',
            dict(self.data_dict.items() + [
                ('type', 'Refund'),
            ])
        )

    def test_refund_webservice_request(self):
        response = self.request.refund(**self.data_dict)
        matcher = RegexpMatcher(REFUND_DATA)
        BraspagRequest._webservice_request.\
                        assert_called_once_with(matcher, 'www.pagador.com.br')

    def test_capture_render_template(self):
        self.request._render_template = MagicMock(name='_render_template')
        response = self.request.capture(**self.data_dict)

        self.request._render_template.assert_called_once_with('base.xml',
            dict(self.data_dict.items() + [
                ('type', 'Capture'),
            ])
        )

    def test_capture_webservice_request(self):
        response = self.request.capture(**self.data_dict)
        matcher = RegexpMatcher(CAPTURE_DATA)
        BraspagRequest._webservice_request.\
                        assert_called_once_with(matcher, 'www.pagador.com.br')
