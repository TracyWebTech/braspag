#!/usr/bin/python
# -*- coding: utf8 -*-

import httplib
import logging

import jinja2

from xml.dom import minidom
from xml.etree import ElementTree
from decimal import Decimal, InvalidOperation


__version__ = '0.1'


__all__ = [
    'BraspagResponse',
    'PAYMENT_METHODS',
    'authorize_transaction',
]


PAYMENT_METHODS = {
    'Cielo': {
        'Visa': 500,
        'MasterCard': 501,
        'Amex': 502,
        'Diners': 503,
        'Elo': 504,
    },
    'Banorte': {
        'Visa': 505,
        'MasterCard': 506,
        'Diners': 507,
        'Amex': 508,
    },
    'Redecard': {
        'Visa': 509,
        'MasterCard': 510,
        'Diners':511,
    },
    'PagosOnLine': {
        'Visa': 512,
        'MasterCard': 513,
        'Amex': 514,
        'Diners': 515,
    },
    'Payvision': {
        'Visa': 516,
        'MasterCard': 517,
        'Diners': 518,
        'Amex': 519,
    },
    'Banorte Cargos Automaticos': {
        'Visa': 520,
        'MasterCard': 521,
        'Diners': 522,
    },
    'Amex': {
        '2P': 523,
    },
    'SITEF': {
        'Visa': 524,
        'MasterCard': 525,
        'Amex': 526,
        'Diners': 527,
        'HiperCard': 528,
        'Leader': 529,
        'Aura': 530,
        'Santander Visa': 531,
        'Santander MasterCard': 532,
    },
    'Simulated': {
        'USD': 995,
        'EUR': 996,
        'BRL': 997,
    }
}


JINJA_ENV = jinja2.Environment(
    autoescape=True,
    loader=jinja2.PackageLoader('braspag'),
)


#Exceptions
class BraspagException(Exception):
    """
    Custom exception base
    """
    pass


class BraspagHttpResponseException(BraspagException):
    """
    Status code Exception
    """
    def __init__(self,code,msg):
        self.code = code
        self.msg = msg

    def __str__(self):
        return "[{}] {}".format(self.code,self.msg)


class BraspagResponse(object):

    STATUS = [
        (0, 'Captured'),
        (1, 'Authorized'),
        (2, 'Not Authorized'),
        (3, 'Disqualifying Error'),
        (4, 'Waiting for Answer'),
    ]

    NAMESPACE = 'https://www.pagador.com.br/webservice/pagador'

    def __init__(self, http_reponse):
        if http_reponse.status != 200:
            raise BraspagHttpResponseException(http_reponse.status,
                                               http_reponse.reason)

        xml_response = http_reponse.read()
        self.root = ElementTree.fromstring(xml_response)

        logging.debug(minidom.parseString(xml_response).\
                                                    toprettyxml(indent='  '))

        if self._get_text('Success') == 'true':
            self.success = True
        else:
            self.success = False

        self.order_id = self._get_text('OrderId')
        self.braspag_order_id = self._get_text('BraspagOrderId')
        self.transaction_id = self._get_text('BraspagTransactionId')
        self.payment_method = self._get_int('PaymentMethod')
        self.amount = self._get_amount('Amount')
        self.acquirer_transaction_id = self._get_text('AcquirerTransactionId')
        self.authorization_code = self._get_text('AuthorizationCode')
        self.return_code = self._get_int('ReturnCode')
        self.return_message = self._get_text('ReturnMessage')
        self.card_token = self._get_text('CreditCardToken')
        self.status = BraspagResponse.STATUS[self._get_int('Status')]
        self.errors = self._get_errors()

    def _get_text(self, field, node=None):
        if node is None:
            node = self.root
        xml_tag = node.find('.//{{{0}}}{1}'.format(
                                            BraspagResponse.NAMESPACE, field))
        if xml_tag is not None:
            if xml_tag.text is not None:
                return xml_tag.text.strip()
        return ''

    def _get_int(self, field):
        try:
            return int(self._get_text(field))
        except ValueError:
            return 0

    def _get_amount(self, field):
        try:
            amount = Decimal(self._get_text(field))
        except InvalidOperation:
            return Decimal('0.00')

        return (amount/100).quantize(Decimal('1.00'))

    def _get_errors(self):
        errors = []
        xml_errors = self.root.findall('.//{{{0}}}ErrorReportDataResponse'.\
                                             format(BraspagResponse.NAMESPACE))
        for error_node in xml_errors:
            code = self._get_text('ErrorCode', error_node)
            msg = self._get_text('ErrorMessage', error_node)
            errors.append((int(code), msg))

        return errors


def webservice_request(xml):
    WSDL = '/webservice/pagadorTransaction.asmx?WSDL'

    if isinstance(xml, unicode):
        xml = xml.encode('utf-8')

    http = httplib.HTTPSConnection('homologacao.pagador.com.br')
    http.request("POST", WSDL, body=xml, headers = {
        "Host": "localhost",
        "Content-Type": "text/xml; charset=UTF-8",
    })
    return BraspagResponse(http.getresponse())


def authorize_transaction(data_dict):

    if data_dict.get('card_number'):
        card_keys = (
            'card_security_code',
            'card_exp_date',
            'card_number',
        )
        assert all(data_dict.has_key(key) for key in card_keys), \
            ("Transações com Cartão de Crédito exigem os "
            "parametros: {0}".format(' ,'.join(card_keys)))

    if not data_dict.get('number_of_payments'):
        data_dict['number_of_payments'] = 1

    if not data_dict.get('payment_plan'):
        if data_dict.get('number_of_payments') > 1:
            # 2 = parcelado pelo emissor do cartão
            data_dict['payment_plan'] = 2
        else:
            # 0 = a vista
            data_dict['payment_plan'] = 0

    if not data_dict.get('currency'):
        data_dict['currency'] = 'BRL'

    if not data_dict.get('country'):
        data_dict['country'] = 'BRA'

    if not data_dict.get('transaction_type'):
        # 2 = captura automatica
        data_dict['transaction_type'] = 2

    if data_dict.get('save_card', False):
        data_dict['save_card'] = 'true'

    template = JINJA_ENV.get_template('authorize.xml')
    xml_request = template.render(data_dict)
    logging.debug(xml_request)
    return webservice_request(xml_request)
