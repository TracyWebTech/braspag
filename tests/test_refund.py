
from base import BraspagTestCase
from cancel import CancelTestCase


class RefundTest(CancelTestCase, BraspagTestCase):
    def __init__(self, *args, **kwargs):
        super(RefundTest, self).__init__(*args, **kwargs)

        self.xml_response_data = 'tests/data/refund_response.xml'
        self.xml_request_data = 'tests/data/refund_request.xml'
        self.cancel_type = 'Refund'

    def cancel_method(self, *args, **kwargs):
        return self.braspag.refund(*args, **kwargs)
