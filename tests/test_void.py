
from base import BraspagTestCase
from cancel import CancelTestCase


class VoidTest(CancelTestCase, BraspagTestCase):
    def __init__(self, *args, **kwargs):
        super(VoidTest, self).__init__(*args, **kwargs)

        self.xml_response_data = 'tests/data/void_response.xml'
        self.xml_request_data = 'tests/data/void_request.xml'
        self.cancel_type = 'Void'

    def cancel_method(self, *args, **kwargs):
        return self.braspag.void(*args, **kwargs)
