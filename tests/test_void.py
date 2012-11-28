# -*- coding: utf8 -*-

from __future__ import absolute_import

from decimal import Decimal

from base import BraspagTestCase, RegexpMatcher

from mock import MagicMock


VOID_DATA = 'tests/data/void_request.xml'
#REFUND_DATA = 'tests/data/refund_request.xml'
#CAPTURE_DATA = 'tests/data/capture_request.xml'

class VoidTest(BraspagTestCase):

    def setUp(self):
        super(VoidTest, self).setUp()
        self.data_dict = {
            'transaction_id': '782b632a-2dae-11e2-b3ee-080027d29772',
            'amount': '12330',
        }

        with open('tests/data/void_response.xml') as response:
            self.braspag._request.return_value = response.read()

        self.response = self.braspag.void(**self.data_dict)

    def test_correlation_id(self):
        assert self.response.correlation_id == '87fcfcbe-1272-4a78-89d4-4d3b33ab74e0'

    def test_success(self):
        assert self.response.success == True

    def test_transaction_id(self):
        assert self.response.transaction_id == '0dfc078c-4c8b-454a-af0f-1f02023a4141'

    def test_acquirer_transaction_id(self):
        assert self.response.acquirer_transaction_id == '2cf84e51-c45b-45d9-9f64-554a6e088668'
    def test_amount(self):
        assert self.response.amount == Decimal('1234.96')

    def test_authorization_code(self):
        assert self.response.authorization_code == '20121127023809171'

    def test_return_code(self):
        assert self.response.return_code == 0

    def test_return_message(self):
        assert self.response.return_message == 'Operation Successful'

    def test_status(self):
        assert self.response.status == 0

    def test_status_message(self):
        assert self.response.status_message == 'Void/Refund Confirmed'

    def test_void_render_template(self):
        self.braspag._render_template = MagicMock(name='_render_template')
        response = self.braspag.void(**self.data_dict)

        self.braspag._render_template.assert_called_with('base.xml',
            dict(self.data_dict.items() + [
                ('type', 'Void'),
            ])
        )

    def test_void_webservice_request(self):
        response = self.braspag.void(**self.data_dict)
        matcher = RegexpMatcher(VOID_DATA)
        self.braspag._request.assert_callede_with(matcher)
