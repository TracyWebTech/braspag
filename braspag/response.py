
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element

from decimal import Decimal


def to_bool(value):
    value = value.lower()
    if value == 'true':
        return True
    elif value == 'false':
        return False


def to_decimal(value):
    return Decimal(int(value)/100.0).quantize(Decimal('1.00'))


def to_unicode(value):
    if isinstance(value, str):
        return value.decode('utf-8')
    return value


class PagadorResponse(object):

    def __init__(self, xml):
        self._fields = getattr(self, '_fields', {})

        self._fields['transaction_id'] = 'BraspagTransactionId'
        self._fields['correlation_id'] = 'CorrelationId'
        self._fields['amount'] = ('Amount', to_decimal)
        self._fields['success'] = ('Success', to_bool)

        # TODO
        #self.errors = []

        self.parse_xml(xml)

    def parse_xml(self, xml):
        # Set None as defaults
        for field in self._fields:
            setattr(self, field, None)

        xml = ET.fromstring(xml)
        for elem in xml.iter():
            if elem.text:
                for field, tag_info in self._fields.items():
                    if isinstance(tag_info, (list, tuple)):
                        tag, convert = tag_info
                    else:
                        tag = tag_info
                        convert = to_unicode

                    if elem.tag.endswith(tag):
                        value = convert(elem.text.strip())
                        setattr(self, field, value)


class CreditCardResponse(PagadorResponse):

    def __init__(self, xml):

        self._fields = {}

        # auth fields
        self._fields['order_id'] = 'OrderId'
        self._fields['braspag_order_id'] = 'BraspagOrderId'
        self._fields['payment_method'] = ('PaymentMethod', int)

        self._fields['acquirer_transaction_id'] = 'AcquirerTransactionId'
        self._fields['authorization_code'] = 'AuthorizationCode'

        self._fields['return_code'] = ('ReturnCode', int)
        self._fields['return_message'] = 'ReturnMessage'

        self._fields['status'] = ('Status', int)

        #self.status_message = None

        super(CreditCardResponse, self).__init__(xml)
        if self._STATUS and hasattr(self, 'status'):
            self.status_message = dict(self._STATUS)[self.status]


class CreditCardAuthorizationResponse(CreditCardResponse):
    _STATUS = (
        (0, 'Captured'),
        (1, 'Authorized'),
        (2, 'Not Authorized'),
        (3, 'Disqualifying Error'),
        (4, 'Waiting for Answer'),
    )


class CreditCardCancelResponse(CreditCardResponse):
    _STATUS = (
        (0, 'Void/Refund Confirmed'),
        (1, 'Void/Refund Denied'),
        (2, 'Invalid Transaction'),
    )


class BilletResponse(PagadorResponse):

    def __init__(self):
        self._fields = {}

        # auth fields
        self._fields['order_id'] = 'OrderId'
        self._fields['braspag_order_id'] = 'BraspagOrderId'
        self._fields['payment_method'] = 'PaymentMethod'

        self._fields['number'] = 'BoletoNumber'
        self._fields['expiration_date'] = 'BoletoExpirationDate'
        self._fields['url'] = 'BoletoUrl'
        self._fields['assignor'] = 'Assignor'
        self._fields['barcode_number'] = 'BarCodeNumber'
        self._fields['message'] = 'Message'

        super(BilletResponse, self).__init__(xml)
