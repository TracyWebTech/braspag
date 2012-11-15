# -*- encoding: utf-8 -*-

from __future__ import absolute_import

import uuid
import httplib
import logging

import jinja2

from .utils import spaceless, is_valid_guid
from xml.dom import minidom
from xml.etree import ElementTree
from decimal import Decimal, InvalidOperation


class BraspagRequest(object):
    """Implements Braspag Pagador API (manual version 1.9).

Boleto generation is not yet implemented.

    """

    _PAYMENT_METHODS = {
        'Cielo': {
            'Visa Electron': 123,
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

    def __init__(self, merchant_id=None, homologation=False):
        if homologation:
            self.url = 'homologacao.pagador.com.br'
        else:
            self.url = 'www.pagador.com.br'

        self.merchant_id = merchant_id

        self.jinja_env = jinja2.Environment(
            autoescape=True,
            loader=jinja2.PackageLoader('braspag'),
        )

    @staticmethod
    def _webservice_request(xml, url):
        WSDL = '/webservice/pagadorTransaction.asmx?WSDL'

        if isinstance(xml, unicode):
            xml = xml.encode('utf-8')

        http = httplib.HTTPSConnection(url)
        http.request("POST", WSDL, body=xml, headers = {
            "Host": "localhost",
            "Content-Type": "text/xml; charset=UTF-8",
        })
        return BraspagResponse(http.getresponse())

    def _request(self, xml_request):
        return BraspagRequest._webservice_request(spaceless(xml_request),
                                                 self.url)

    def authorize(self, **kwargs):
        """All arguments supplied to this method must be keyword arguments.

:arg order_id: Order id. It will be used to indentify the
               order later in Braspag.
:arg customer_id: Must be user's CPF/CNPJ.
:arg customer_name: User's full name.
:arg customer_email: User's email address.
:arg amount: Amount to charge.

:arg card_holder: Name printed on card.
:arg card_number: Card number.
:arg card_security_code: Card security code.
:arg card_exp_date: Card expiration date.
:arg save_card: Flag that tell to Braspag to store card number.
                If set to True Reponse will return a card token.
                *Default: False*.
:arg card_token: Card token returned by Braspag. When used it
                 should replace *card_holder*, *card_exp_date*,
                 *card_number* and *card_security_code*.
:arg number_of_payments: Number of payments that the amount will
                         be devided (number of months). *Default: 1*.
:arg currency: Currency of the given amount. *Default: BRL*.
:arg country: User's country. *Default: BRA*.
:arg transaction_type: An integer representing one of the
                       :ref:`transaction_types`. *Default: 2*.
:arg payment_plan: An integer representing how multiple payments should
                   be handled. *Default: 0*. See :ref:`payment_plans`.
:arg payment_method: Integer representing one of the
                     available :ref:`payment_methods`.

:returns: :class:`~braspag.BraspagResponse`

"""

        assert any((kwargs.get('card_number'),
                    kwargs.get('card_token'))),\
                    'card_number ou card_token devem ser fornecidos'

        if kwargs.get('card_number'):
            card_keys = (
                'card_holder',
                'card_security_code',
                'card_exp_date',
                'card_number',
            )
            assert all(kwargs.has_key(key) for key in card_keys), \
                (u'Transações com Cartão de Crédito exigem os '
                u'parametros: {0}'.format(' ,'.join(card_keys)))

        if not kwargs.get('number_of_payments'):
            kwargs['number_of_payments'] = 1

        try:
            number_of_payments = int(kwargs.get('number_of_payments'))
        except ValueError:
            raise BraspagException('Number of payments must be int.')

        if not kwargs.get('payment_plan'):

            if number_of_payments > 1:
                # 2 = parcelado pelo emissor do cartão
                kwargs['payment_plan'] = 2
            else:
                # 0 = a vista
                kwargs['payment_plan'] = 0

        if not kwargs.get('currency'):
            kwargs['currency'] = 'BRL'

        if not kwargs.get('country'):
            kwargs['country'] = 'BRA'

        if not kwargs.get('transaction_type'):
            # 2 = captura automatica
            kwargs['transaction_type'] = 2

        if kwargs.get('save_card', False):
            kwargs['save_card'] = 'true'

        xml_request = self._render_template('authorize.xml', kwargs)

        return self._request(xml_request)

    def _base_transaction(self, transaction_id, amount, type=None):
        assert type in ('Refund', 'Void', 'Capture')
        assert is_valid_guid(transaction_id), 'Transaction ID invalido'

        data_dict = {
            'amount': amount,
            'type': type,
            'transaction_id': transaction_id,
        }
        xml_request = self._render_template('base.xml', data_dict)
        return self._request(xml_request)

    def void(self, transaction_id, amount=0):
        """Void the given amount for the given transaction_id.

This method should be used to return funds to customers
for transactions that happened within less than 23h and
59 minutes ago. For other transactions use
:meth:`~braspag.BraspagRequest.refund`.

If the amount is 0 (zero) the full transaction will be
voided.

:returns: :class:`~braspag.BraspagResponse`

        """
        return self._base_transaction(transaction_id, amount, 'Void')

    def refund(self, transaction_id, amount=0):
        """Refund the given amount for the given transaction_id.

This method should be used to return funds to customers
for transactions that happened at least 24 hours ago.
For transactions that happended within 24 hours use
:meth:`~braspag.BraspagRequest.void`.

If the amount is 0 (zero) the full transaction will be
refunded.

:returns: :class:`~braspag.BraspagResponse`

        """
        return self._base_transaction(transaction_id, amount, 'Refund')

    def capture(self, transaction_id, amount=0):
        """Capture the given `amount` from the given transaction_id.

This method should only be called after pre-authorizing the
transaction by calling :meth:`~braspag.BraspagRequest.authorize`
with `transaction_types` 1 or 3.

:returns: :class:`~braspag.BraspagResponse`

        """
        return self._base_transaction(transaction_id, amount, 'Capture')

    def _render_template(self, template_name, data_dict):
        if self.merchant_id:
            data_dict['merchant_id'] = self.merchant_id

        if not data_dict.has_key('request_id'):
            data_dict['request_id'] = unicode(uuid.uuid4())

        template = self.jinja_env.get_template(template_name)
        xml_request = template.render(data_dict)
        logging.debug(xml_request)
        return xml_request


class BraspagResponse(object):
    """ TODO:

.. attribute:: correlation_id
.. attribute:: errors
.. attribute:: success
.. attribute:: order_id
.. attribute:: braspag_order_id
.. attribute:: transaction_id
.. attribute:: payment_method
.. attribute:: amount
.. attribute:: acquirer_transaction_id
.. attribute:: authorization_code
.. attribute:: return_code
.. attribute:: return_message
.. attribute:: card_token
.. attribute:: status

    """

    _STATUS = [
        (0, 'Captured'),
        (1, 'Authorized'),
        (2, 'Not Authorized'),
        (3, 'Disqualifying Error'),
        (4, 'Waiting for Answer'),
    ]

    _NAMESPACE = 'https://www.pagador.com.br/webservice/pagador'

    def __init__(self, http_reponse):
        if http_reponse.status != 200:
            raise BraspagHttpResponseException(http_reponse.status,
                                               http_reponse.reason)

        # Ensure all attributes are set before returning
        self.order_id = None
        self.braspag_order_id = None
        self.transaction_id = None
        self.payment_method = None
        self.amount = None
        self.acquirer_transaction_id = None
        self.authorization_code = None
        self.return_code = None
        self.return_message = None
        self.card_token = None
        self.status = None

        xml_response = http_reponse.read()
        self.root = ElementTree.fromstring(xml_response)

        logging.debug(minidom.parseString(xml_response).\
                                                    toprettyxml(indent='  '))

        self.correlation_id = self._get_text('CorrelationId')
        self.errors = self._get_errors()

        if self._get_text('Success') == 'true':
            self.success = True
        else:
            self.success = False
            return

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
        self.status = BraspagResponse._STATUS[self._get_int('Status')]

    def _get_text(self, field, node=None):
        if node is None:
            node = self.root
        xml_tag = node.find('.//{{{0}}}{1}'.format(
                                            BraspagResponse._NAMESPACE, field))
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
                                             format(BraspagResponse._NAMESPACE))
        for error_node in xml_errors:
            code = self._get_text('ErrorCode', error_node)
            msg = self._get_text('ErrorMessage', error_node)
            errors.append((int(code), msg))

        return errors


