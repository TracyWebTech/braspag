# -*- encoding: utf-8 -*-

import sys
import uuid
import logging

from pprint import pformat
from braspag.core import BraspagRequest

if len(sys.argv) > 1:
    MERCHANT_ID = sys.argv[1]
else:
    MERCHANT_ID = u'12345678-1234-1234-1234-1234567890AB'

logging.root.setLevel(logging.INFO)

# Create request object
request = BraspagRequest(merchant_id=MERCHANT_ID, homologation=True)

# Authorize
response = request.authorize(
    order_id=uuid.uuid4(),
    customer_id=u'12345678900',
    customer_name=u'José da Silva',
    customer_email='jose123@dasilva.com.br',
    payment_method=997, # Simulated BRL
    amount=10000,
    transaction_type=1,
    card_holder=u'Jose da Silva',
    card_number=u'0000000000000001',
    card_security_code='123',
    card_exp_date='05/2018',
)
logging.info(pformat(response.__dict__))

# Capture
response2 = request.capture(transaction_id=response.transaction_id)
logging.info(pformat(response2.__dict__))

# Void
response3 = request.void(transaction_id=response.transaction_id)
logging.info(pformat(response3.__dict__))
