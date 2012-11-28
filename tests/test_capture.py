# -*- coding: utf8 -*-

from __future__ import absolute_import

from decimal import Decimal

from base import BraspagTestCase, RegexpMatcher

from mock import MagicMock


CAPTURE_DATA = 'tests/data/capture_request.xml'


class CaptureTest(BraspagTestCase):

    def setUp(self):
        super(CaptureTest, self).setUp()
        self.data_dict = {
            'transaction_id': '782b632a-2dae-11e2-b3ee-080027d29772',
            'amount': '10000',
        }

        with open('tests/data/capture_response.xml') as response:
            self.braspag._request.return_value = response.read()

        self.response = self.braspag.capture(**self.data_dict)

    def test_correlation_id(self):
        assert self.response.correlation_id == '7eb38395-c17e-4b85-8204-8065563c548f'

    def test_success(self):
        assert self.response.success == True

    def test_transaction_id(self):
        assert self.response.transaction_id == '0dfc078c-4c8b-454a-af0f-1f02023a4141'

    def test_acquirer_transaction_id(self):
        assert self.response.acquirer_transaction_id == '1127023808906'
    def test_amount(self):
        assert self.response.amount == Decimal('100.00')

    def test_authorization_code(self):
        assert self.response.authorization_code == '20121127023809171'

    def test_return_code(self):
        assert self.response.return_code == 6

    def test_return_message(self):
        assert self.response.return_message == 'Operation Successful'

    def test_status(self):
        assert self.response.status == 0

    def test_status_message(self):
        assert self.response.status_message == 'Captured'

    def test_capture_render_template(self):
        self.braspag._render_template = MagicMock(name='_render_template')
        response = self.braspag.capture(**self.data_dict)

        self.braspag._render_template.assert_called_with('base.xml',
            dict(self.data_dict.items() + [
                ('type', 'Capture'),
            ])
        )

    def test_capture_webservice_request(self):
        response = self.braspag.capture(**self.data_dict)
        matcher = RegexpMatcher(CAPTURE_DATA)
        self.braspag._request.assert_callede_with(matcher)
