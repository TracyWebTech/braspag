# -*- encoding: utf-8 -*-

import uuid
import logging

from pprint import pformat
from braspag.core import BraspagRequest

MERCHANT_ID = u'12345678-1234-1234-1234-1234567890AB'

logging.root.setLevel(logging.DEBUG)

request = BraspagRequest(merchant_id=MERCHANT_ID, homologation=True)

response = request.authorize(
    order_id=uuid.uuid4(),
    customer_id=u'12345678900',
    customer_name=u'José da Silva',
    customer_email='jose123@dasilva.com.br',
    payment_method=BraspagRequest._PAYMENT_METHODS['Simulated']['BRL'],
    amount=10000,
    card_token=u'0202448c-3b90-4395-b562-b98be24687f9',
)

logging.debug(pformat(response.__dict__))

