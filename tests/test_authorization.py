# -*- coding: utf8 -*-

from __future__ import absolute_import

import uuid
import codecs
import unittest
from braspag import BraspagRequest
from braspag.utils import spaceless

from mock import MagicMock, Mock


AUTHORIZATION_DATA = 'tests/data/authorization_request.xml'


class BraspagRequestAuthorizeTest(unittest.TestCase):

    def setUp(self):
        payment_method = BraspagRequest._PAYMENT_METHODS['Simulated']['BRL']
        merchant_id = '12345678-1234-1234-1234-1234567890AB'
        data_dict = {
            'request_id': '782a56e2-2dae-11e2-b3ee-080027d29772',
            'order_id': '782b632a-2dae-11e2-b3ee-080027d29772',
            'customer_id': '12345678900',
            'customer_name': u'José da Silva',
            'customer_email': 'jose123@dasilva.com.br',
            'amount': 10000,
        }

        # CreditCard data for request
        self.cc_dict = data_dict.copy()
        self.cc_dict.update({
            'card_holder': 'Jose da Silva',
            'card_number': '0000000000000001',
            'card_security_code': '123',
            'card_exp_date': '05/2018',
            'payment_method': payment_method,
        })

        # Boleto data for request
        self.boleto_dict = data_dict.copy()

        self.request = BraspagRequest(merchant_id=merchant_id)
        BraspagRequest._webservice_request = MagicMock(name='webservice_request')


    def test_render_cc_template(self):
        self.request._render_template = MagicMock(name='_render_template')
        response = self.request.authorize(**self.cc_dict)

        self.request._render_template.assert_called_once_with(
            'authorize_creditcard.xml',
            dict(self.cc_dict.items() + [
                ('currency', 'BRL'),
                ('payment_plan', 0),
                ('number_of_payments', 1),
                ('country', 'BRA'),
                ('transaction_type', 2),
            ])
        )

    def test_render_boleto_template(self):
        self.request._render_template = MagicMock(name='_render_template')
        response = self.request.issue_invoice(**self.boleto_dict)

        self.request._render_template.assert_called_once_with(
            'authorize_boleto.xml',
            dict(self.boleto_dict.items() + [
                ('currency', 'BRL'),
                ('country', 'BRA'),
                ('payment_method', 14),
            ])
        )

    def test_webservice_request(self):
        response = self.request.authorize(**self.cc_dict)
        with codecs.open(AUTHORIZATION_DATA, encoding='utf-8') as xml:
            BraspagRequest._webservice_request.assert_called_once_with(
                                   spaceless(xml.read()), 'www.pagador.com.br')
