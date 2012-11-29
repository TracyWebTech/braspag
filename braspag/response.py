
import xml.parsers.expat
import xml.etree.ElementTree as ET

from decimal import Decimal
from datetime import datetime
from xml.etree.ElementTree import Element


def unescape(s):
    """Copied from http://wiki.python.org/moin/EscapingXml"""

    want_unicode = False
    if isinstance(s, unicode):
        s = s.encode("utf-8")
        want_unicode = True

    # the rest of this assumes that `s` is UTF-8
    list = []

    # create and initialize a parser object
    p = xml.parsers.expat.ParserCreate("utf-8")
    p.buffer_text = True
    p.returns_unicode = want_unicode
    p.CharacterDataHandler = list.append

    # parse the data wrapped in a dummy element
    # (needed so the "document" is well-formed)
    p.Parse("<e>", 0)
    p.Parse(s, 0)
    p.Parse("</e>", 1)

    # join the extracted strings and return
    es = ""
    if want_unicode:
        es = u""
    return es.join(list)


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
        value = value.decode('utf-8')

    return unescape(value)


def to_date(value):
    return datetime.strptime(value, '%m/%d/%Y %H:%M:%S %p')


class PagadorResponse(object):

    def __init__(self, xml):
        self._fields = getattr(self, '_fields', {})

        self._fields['transaction_id'] = 'BraspagTransactionId'
        self._fields['correlation_id'] = 'CorrelationId'
        self._fields['amount'] = ('Amount', to_decimal)
        self._fields['success'] = ('Success', to_bool)
        self.errors = []

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

                    if elem.tag.endswith('}' + tag):
                        value = convert(elem.text.strip())
                        setattr(self, field, value)
                    elif elem.tag.endswith('}ErrorReportDataResponse'):
                        error = self._get_error(elem)
                        if not error in self.errors:
                            self.errors.append(self._get_error(elem))


    def _get_error(self, error_node):
        for node in error_node.iter():
            if node.tag.endswith('}ErrorCode'):
                code = node.text.strip()
            elif node.tag.endswith('}ErrorMessage'):
                msg = node.text.strip()
        return int(code), msg


class CreditCardResponse(PagadorResponse):

    def __init__(self, xml):

        self._fields = getattr(self, '_fields', {})

        # auth fields
        self._fields['order_id'] = 'OrderId'
        self._fields['braspag_order_id'] = 'BraspagOrderId'
        self._fields['payment_method'] = ('PaymentMethod', int)

        self._fields['acquirer_transaction_id'] = 'AcquirerTransactionId'
        self._fields['authorization_code'] = 'AuthorizationCode'

        self._fields['return_code'] = ('ReturnCode', int)
        self._fields['return_message'] = 'ReturnMessage'

        self._fields['status'] = ('Status', int)

        super(CreditCardResponse, self).__init__(xml)

        status = getattr(self, 'status', None)
        if self._STATUS and status is not None:
            self.status_message = dict(self._STATUS)[status]
        else:
            self.status_message = None


class CreditCardAuthorizationResponse(CreditCardResponse):

    _STATUS = (
        (0, 'Captured'),
        (1, 'Authorized'),
        (2, 'Not Authorized'),
        (3, 'Disqualifying Error'),
        (4, 'Waiting for Answer'),
    )

    def __init__(self, xml):
        self._fields = getattr(self, '_fields', {})
        self._fields['card_token'] = 'CreditCardToken'
        super(CreditCardAuthorizationResponse, self).__init__(xml)


class CreditCardCancelResponse(CreditCardResponse):
    _STATUS = (
        (0, 'Void/Refund Confirmed'),
        (1, 'Void/Refund Denied'),
        (2, 'Invalid Transaction'),
    )


class BilletResponse(PagadorResponse):

    def __init__(self, xml):
        self._fields = getattr(self, '_fields', {})

        # auth fields
        self._fields['order_id'] = 'OrderId'
        self._fields['braspag_order_id'] = 'BraspagOrderId'
        self._fields['payment_method'] = ('PaymentMethod', int)

        self._fields['number'] = ('BoletoNumber', int)
        self._fields['expiration_date'] = ('BoletoExpirationDate', to_date)
        self._fields['url'] = 'BoletoUrl'
        self._fields['assignor'] = 'Assignor'
        self._fields['barcode'] = 'BarCodeNumber'
        self._fields['message'] = 'Message'

        super(BilletResponse, self).__init__(xml)


class BilletDataResponse(BilletResponse):

    def __init__(self, xml):
        self._fields = getattr(self, '_fields', {})

        self._fields['document_number'] = 'DocumentNumber'
        self._fields['document_date'] = ('DocumentDate', to_date)
        self._fields['payment_date'] = ('PaymentDate', to_date)
        self._fields['type'] = 'BoletoType'
        self._fields['paid_amount'] = ('PaidAmount', to_decimal)
        self._fields['bank_number'] = 'BankNumber'
        self._fields['agency'] = 'Agency'
        self._fields['account'] = 'Account'

        super(BilletDataResponse, self).__init__(xml)
