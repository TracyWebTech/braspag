# -*- encoding: utf-8 -*-
from braspag.core import BraspagRequest
import uuid

data_dict = {
    'request_id': uuid.uuid1(),
    'merchant_id':'12345678-1234-1234-1234-1234567890AB',
    'order_id': uuid.uuid1(),
    'customer_id': '12345678900',
    'customer_name': u'José da Silva',
    'customer_email': 'jose123@dasilva.com.br',
    'payment_method': BraspagRequest.PAYMENT_METHODS['Simulated']['BRL'],
    'amount': 10000,
    'card_token': '0202448c-3b90-4395-b562-b98be24687f9',
}

import logging
logging.root.setLevel(logging.DEBUG)
request = BraspagRequest(production=False)
response = request.authorize_transaction(data_dict)

import pprint
pprint.pprint(response.__dict__)
