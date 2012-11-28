# -*- coding: utf8 -*-

from __future__ import absolute_import

from decimal import Decimal

from base import BraspagTestCase, RegexpMatcher

from mock import MagicMock



class CancelTestCase(object):

    def setUp(self):
        super(CancelTestCase, self).setUp()
        self.data_dict = {
            'transaction_id': '0dfc078c-4c8b-454a-af0f-1f02023a4141',
            'amount': '123496',
        }

        with open(self.xml_response_data) as response:
            self.braspag._request.return_value = response.read()

        self.response = self.cancel_method(**self.data_dict)

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

    def test_render_template(self):
        self.braspag._render_template = MagicMock(name='_render_template')
        response = self.cancel_method(**self.data_dict)

        self.braspag._render_template.assert_called_with('base.xml',
            dict(self.data_dict.items() + [
                ('type', self.cancel_type),
            ])
        )

    def test_webservice_request(self):
        response = self.cancel_method(**self.data_dict)
        matcher = RegexpMatcher(self.xml_request_data)
        self.braspag._request.assert_callede_with(matcher)
