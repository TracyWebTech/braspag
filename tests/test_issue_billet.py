# -*- coding: utf-8 -*-

import codecs

from decimal import Decimal
from datetime import datetime

from mock import MagicMock
from base import BraspagTestCase, RegexpMatcher

from braspag.utils import spaceless


class IssueBilletTest(BraspagTestCase):

    def setUp(self):
        super(IssueBilletTest, self).setUp()

        self.data_dict = {
            'order_id': u'c449e66b-731b-4ae4-9ea6-9c37a208986a',
            'customer_id': u'12345678900',
            'customer_name': u'Jose da Silva',
            'customer_email': 'jose123@dasilva.com.br',
            'amount': 10000,
            'payment_method': 10,
        }

        with open('tests/data/billet_auth_response.xml') as response:
            self.braspag._request.return_value = response.read()

        self.response = self.braspag.issue_billet(**self.data_dict)

    def test_render_template(self):
        self.braspag._render_template = MagicMock(name='_render_template')
        response = self.braspag.issue_billet(**self.data_dict)

        self.braspag._render_template.assert_called_with('authorize_billet.xml',
            dict(self.data_dict.items() + [
                ('country', 'BRA'),
                ('currency', 'BRL'),
                ('is_billet', True),
            ])
        )

    def test_request(self):
        billet_request = 'tests/data/billet_request.xml'

        response = self.braspag.issue_billet(**self.data_dict)
        matcher = RegexpMatcher(billet_request)
        self.braspag._request.assert_called_with(matcher)

    def test_correlation_id(self):
        assert self.response.correlation_id == u'3c1e4731-fad5-445c-bd85-cf59be415e24'

    def test_success(self):
        assert self.response.success == True

    def test_braspag_order_id(self):
        assert self.response.braspag_order_id == u'999c496f-cc80-438c-bbbb-1548b6c478c9'

    def test_transaction_id(self):
        assert self.response.transaction_id == u'632bf9f2-007e-44b8-a581-3917a0f9a61c'

    def test_payment_method(self):
        assert self.response.payment_method == 10

    def test_amount(self):
        assert self.response.amount == Decimal('100.00')

    def test_number(self):
        assert self.response.number == 100000002

    def test_expiration_date(self):
        assert self.response.expiration_date == datetime(2012, 11, 27, 12, 0)

    def test_url(self):
        assert self.response.url == 'https://homologacao.pagador.com.br/pagador/reenvia.asp?Id_Transacao=632bf9f2-007e-44b8-a581-3917a0f9a61c'

    def test_barcode(self):
        assert self.response.barcode == '35691.23403 00456.780006 01000.000024 9 55300000010000'

    def test_assignor(self):
        assert self.response.assignor == u'SPRING PUBLICAÇÃO LTDA'

    def test_message(self):
        assert self.response.message == u'Operation Successful'
