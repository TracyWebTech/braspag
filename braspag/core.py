# -*- encoding: utf-8 -*-

from __future__ import absolute_import

import uuid
import httplib
import logging

import jinja2

from .utils import spaceless, is_valid_guid
from .exceptions import BraspagHttpResponseException
from .response import CreditCardAuthorizationResponse, BilletResponse, \
                      BilletDataResponse, CreditCardCancelResponse
from xml.dom import minidom
from xml.etree import ElementTree
from decimal import Decimal, InvalidOperation


class BraspagRequest(object):
    """Implements Braspag Pagador API (manual version 1.9).

Billet generation is not yet implemented.

    """

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

    def _request(self, xml, query=False):
        if query:
            uri = '/services/pagadorQuery.asmx'
        else:
            uri = '/webservice/pagadorTransaction.asmx'

        if isinstance(xml, unicode):
            xml = xml.encode('utf-8')

        http = httplib.HTTPSConnection(self.url)
        http.request("POST", uri, body=xml, headers = {
            "Host": "localhost",
            "Content-Type": "text/xml; charset=UTF-8",
        })
        response = http.getresponse()
        xmlresponse = response.read()
        logging.debug(minidom.parseString(xmlresponse).toprettyxml(indent='  '))
        return xmlresponse

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
                If set to True Response will return a card token.
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

        xml_request = self._render_template('authorize_creditcard.xml', kwargs)
        response = self._request(spaceless(xml_request))
        return CreditCardAuthorizationResponse(response)

    def _base_transaction(self, transaction_id, amount, type=None):
        assert type in ('Refund', 'Void', 'Capture')
        assert is_valid_guid(transaction_id), 'Transaction ID invalido'

        data_dict = {
            'amount': amount,
            'type': type,
            'transaction_id': transaction_id,
        }
        xml_request = self._render_template('base.xml', data_dict)
        xml_response = self._request(xml_request)

        if type in ('Void', 'Refund'):
            return CreditCardCancelResponse(xml_response)
        else:
            return CreditCardAuthorizationResponse(xml_response)


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

    def issue_billet(self, **kwargs):
        """All arguments supplied to this method must be keyword arguments.

:arg order_id: Order id. It will be used to indentify the
               order later in Braspag.
:arg customer_id: Must be user's CPF/CNPJ.
:arg customer_name: User's full name.
:arg customer_email: User's email address.
:arg amount: Amount to charge.
:arg currency: Currency of the given amount. *Default: BRL*.
:arg country: User's country. *Default: BRA*.
:arg payment_method: Payment method code

:returns: :class:`~braspag.BraspagResponse`

"""
        if not kwargs.get('currency'):
            kwargs['currency'] = 'BRL'

        if not kwargs.get('country'):
            kwargs['country'] = 'BRA'

        kwargs['is_billet'] = True

        xml_request = self._render_template('authorize_billet.xml', kwargs)
        return BilletResponse(self._request(spaceless(xml_request)))

    def get_billet_data(self, transaction_id):
        """All arguments supplied to this method must be keyword arguments.

:arg transaction_id: The id of the transaction generated previously by
*issue_billet*

:returns: :class:`~braspag.BilletResponse`

"""
        assert is_valid_guid(transaction_id), 'Invalid Transaction ID'

        context = {'transaction_id': transaction_id}
        xml_request = self._render_template('get_billet_data.xml', context)
        xml_response = self._request(spaceless(xml_request), query=True)
        return BilletDataResponse(xml_response)
