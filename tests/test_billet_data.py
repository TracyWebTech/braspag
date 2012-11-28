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
            'transaction_id': u'140c74cf-099a-4cd4-9545-feb0260cecc1',
        }

        with open('tests/data/get_billet_data_response.xml') as response:
            self.braspag._request.return_value = response.read()

        self.response = self.braspag.get_billet_data(**self.data_dict)

    def test_render_template(self):
        self.braspag._render_template = MagicMock(name='_render_template')
        response = self.braspag.get_billet_data(**self.data_dict)

        self.braspag._render_template.assert_called_with('get_billet_data.xml',
                                                         self.data_dict)

    def test_request(self):
        billet_request = 'tests/data/get_billet_data_request.xml'

        response = self.braspag.get_billet_data(**self.data_dict)
        matcher = RegexpMatcher(billet_request)
        self.braspag._request.assert_called_with(matcher, query=True)

    def test_correlation_id(self):
        assert self.response.correlation_id == u'4cd0ad15-0017-4ec2-80cd-c09ecc26c4a1'

    def test_success(self):
        assert self.response.success == True

    def test_transaction_id(self):
        assert self.response.transaction_id == u'140c74cf-099a-4cd4-9545-feb0260cecc1'

    def test_payment_method(self):
        assert self.response.payment_method == 10

    def test_document_number(self):
        assert self.response.document_number == u'0f7e5e31-c5ac-4a48-b985-47efb83007fd'

    def test_amount(self):
        print self.response.amount
        assert self.response.amount == Decimal('100.00')

    def test_number(self):
        assert self.response.number == 1000000135

    def test_expiration_date(self):
        assert self.response.expiration_date == datetime(2012, 11, 28, 12, 0)

    def test_url(self):
        assert self.response.url == 'https://homologacao.pagador.com.br/pagador/reenvia.asp?Id_Transacao=140c74cf-099a-4cd4-9545-feb0260cecc1'

    def test_type(self):
        assert self.response.type == 'CSR'

    def test_paid_amount(self):
        assert self.response.paid_amount == Decimal('0.00')

    def test_barcode(self):
        assert self.response.barcode == u'35691.23403 00456.750009 01000.000131 9 55310000010000'

    def test_assignor(self):
        assert self.response.assignor == u'SPRING PUBLICAÇÃO LTDA'
