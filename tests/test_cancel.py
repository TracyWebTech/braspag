# -*- coding: utf8 -*-

from __future__ import absolute_import

import uuid
import codecs
import unittest
from braspag.core import BraspagRequest
from braspag.utils import spaceless

from mock import MagicMock, Mock


VOID_DATA = 'tests/data/void_request.xml'


class BraspagRequestVoidTest(unittest.TestCase):

    def setUp(self):
        self.data_dict = {
            'request_id': '782a56e2-2dae-11e2-b3ee-080027d29772',
            'merchant_id': '12345678-1234-1234-1234-1234567890AB',
            'braspag_transaction_id': '782b632a-2dae-11e2-b3ee-080027d29772',
            'amount': '12330',
        }

        self.request = BraspagRequest()
        BraspagRequest.webservice_request = MagicMock(name='webservice_request')


    def test_render_template(self):
        self.request._render_template = MagicMock(name='_render_template')
        response = self.request.void_transaction(self.data_dict)

        self.request._render_template.assert_called_once_with('cancel.xml',
            dict(self.data_dict.items() + [
                ('cancel_type', 'Void'),
            ])
        )

    def test_webservice_request(self):
        response = self.request.void_transaction(self.data_dict)
        with codecs.open(VOID_DATA, encoding='utf-8') as xml:
            BraspagRequest.webservice_request.assert_called_once_with(
                                   spaceless(xml.read()), 'www.pagador.com.br')
