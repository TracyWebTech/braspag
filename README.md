# Braspag

[![Build Status](https://secure.travis-ci.org/TracyWebTech/braspag.png?branch=master)](https://travis-ci.org/TracyWebTech/braspag)

## Getting Started

### Dependencies

The following dependencies are automaticatly installed by the setup.py:

* Jinja2

### Installation

1. Clone the repository to your machine.
2. Run `python setup.py install` from the root of your local clone.

### Authorizing a transaction

The following example shows how to process a credit card request:

    from braspag import BraspagRequest

    data_dict = {
        'request_id': '3c3069d1-ae46-409a-94ec-4034cc6d2a0d',
        'merchant_id': 'ba645db1-75c3-4892-837a-7aecf57c48b6',
        'order_id': 'd53dab0e-2245-4b91-b73c-f051637aa577',
        'customer_id': '12345678900',
        'customer_name': 'Jose da Silva',
        'customer_email': 'jose123@dasilva.com.br',
        'payment_method': BraspagRequest.PAYMENT_METHODS['Simulated']['BRL'],
        'amount': 10000, # R$100,00
        'card_holder': 'Jose da Silva',
        'card_number': '0000000000000001',
        'card_security_code': '123',
        'card_exp_date': '05/2018',
    }
    request = BraspagRequest()
    response = request.authorize_transaction(data_dict)

    if response.success:
        print "Nice!!"

# Documentation


## Object `BraspagRequest`

`BraspagRequest` instances have the following methods and attributes:

### Attributes

 * `BraspagRequest.PAYMENT_METHODS`

### Methods

#### `authorize_transaction(data_dict)`

Valid `data_dict` stuff:

 * request\_id:
 * merchant\_id:
 * order\_id:
 * customer\_id:
 * customer\_name:
 * customer\_email:
 * payment\_method:
 * amount:
 * card\_holder:
 * card\_number:
 * card\_security_code:
 * card\_exp_date:
 * card\_token:
 * save\_card:
 * number\_of\_payments:
 * payment\_plan:
 * currency:
 * country:
 * transaction\_type:


#### `void_transaction(data_dict)`

 * request\_id:
 * merchant\_id:
 * braspag\_transaction\_id:
 * amount


## Object `BraspagResponse`

`BraspagResponse` instances have the following methods and attributes:

### Attributes

 * `BraspagResponse.success`:
 * `BraspagResponse.order_id`:
 * `BraspagResponse.braspag_order_id`:
 * `BraspagResponse.transaction_id`:
 * `BraspagResponse.payment_method`:
 * `BraspagResponse.amount`:
 * `BraspagResponse.acquirer_transaction_id`:
 * `BraspagResponse.authorization_code`:
 * `BraspagResponse.return_code`:
 * `BraspagResponse.return_message`:
 * `BraspagResponse.status`:
 * `BraspagResponse.errors`:

# Payment methods available:

* __Cielo__: Visa, MasterCard, Amex, Diners, Elo
* __Banorte__: Visa, MasterCard, Diners, Amex
* __Redecard__: Visa, MasterCard, Diners
* __PagosOnLine__: Visa, MasterCard, Amex, Diners
* __Payvision__: Visa, MasterCard, Diners, Amex
* __Banorte Cargos Automaticos__: Visa, MasterCard, Diners
* __Amex__: 2P
* __SITEF__: Visa, MasterCard, Amex, Diners, HiperCard, Leader, Aura, Santander Visa, Santander MasterCard
* __Simulated__: USD, EUR, BRL

# LICENSE

All source code here is available under the [LGPL Version 3][] license, unless
otherwise indicated.

  [LGPL Version 3]: http://www.gnu.org/licenses/lgpl.txt
