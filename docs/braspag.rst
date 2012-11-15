Python Braspag Lib
===================

Request Object
---------------

.. autoclass:: braspag.BraspagRequest
    :members:
    :exclude-members: authorize
    :undoc-members:

    .. automethod:: braspag.core.BraspagRequest.authorize(order_id, customer_id, customer_name, customer_email, amount, card_holder, card_number, card_security_code, card_exp_date, save_card, card_token, number_of_payments, payment_method, payment_plan, transaction_type=2, currency='BRL', country='BRA')


Examples
.........


Creditcard example
+++++++++++++++++++++

The example bellow shows how to authorize a credit card transation::

    from braspag import BraspagRequest

    ORDER_ID = u'84765421-5435-85C2-3F41-85A72BE2433E'
    MERCHANT_ID = u'12345678-1234-1234-1234-1234567890AB'

    request = BraspagRequest(merchant_id=MERCHANT_ID, homologation=True)
    response = request.authorize(
        order_id=ORDER_ID,
        customer_id=u'12345678900',
        customer_name=u'José da Silva',
        customer_email='jose123@dasilva.com.br',
        payment_method=997, #simulated BRL
        amount=10000,
        card_holder=u'Jose da Silva',
        card_number=u'0000000000000001',
        card_security_code='123',
        card_exp_date='05/2018',
    )

The argument `order_id` should be an GUID valid string which
indentifies this transaction on your system. The argument
`customer_id` must be a valid CPF or CNPJ for the user.

The `amount` given should be an integer where the 2 last digits
will represent the decimal places.


Response Object
-----------------

.. autoclass:: braspag.BraspagResponse
    :members:
    :undoc-members:


Exceptions
-----------

.. automodule:: braspag.exceptions
    :members:
    :undoc-members:
    :show-inheritance:

Utils
------

.. automodule:: braspag.utils
    :members:
    :undoc-members:
    :show-inheritance:
