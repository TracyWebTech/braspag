# -*- coding: utf8 -*-

from __future__ import absolute_import

import uuid
import codecs
import unittest
from braspag.core import BraspagRequest
from braspag.utils import spaceless

from mock import MagicMock, Mock


AUTHORIZATION_DATA = 'tests/data/authorization_request.xml'


class BraspagRequestAuthorizeTest(unittest.TestCase):

    def setUp(self):
        payment_method = BraspagRequest.PAYMENT_METHODS['Simulated']['BRL']
        self.data_dict = {
            'request_id': '782a56e2-2dae-11e2-b3ee-080027d29772',
            'merchant_id': '12345678-1234-1234-1234-1234567890AB',
            'order_id': '782b632a-2dae-11e2-b3ee-080027d29772',
            'customer_id': '12345678900',
            'customer_name': u'José da Silva',
            'customer_email': 'jose123@dasilva.com.br',
            'payment_method': payment_method,
            'amount': 10000,
            'card_holder': 'Jose da Silva',
            'card_number': '0000000000000001',
            'card_security_code': '123',
            'card_exp_date': '05/2018',
        }

        self.request = BraspagRequest()
        BraspagRequest.webservice_request = MagicMock(name='webservice_request')


    def test_render_template(self):
        self.request._render_template = MagicMock(name='_render_template')
        response = self.request.authorize_transaction(self.data_dict)

        self.request._render_template.assert_called_once_with('authorize.xml',
            dict(self.data_dict.items() + [
                ('currency', 'BRL'),
                ('payment_plan', 0),
                ('number_of_payments', 1),
                ('country', 'BRA'),
                ('transaction_type', 2),
            ])
        )

    def test_webservice_request(self):
        response = self.request.authorize_transaction(self.data_dict)
        with codecs.open(AUTHORIZATION_DATA, encoding='utf-8') as xml:
            BraspagRequest.webservice_request.assert_called_once_with(
                                   spaceless(xml.read()), 'www.pagador.com.br')
