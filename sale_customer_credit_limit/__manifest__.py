# -*- coding: utf-8 -*-
# © 2016 Tobias Zehntner
# © 2016 Niboo SPRL (https://www.niboo.be/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Sale - Limit customer credit',
    'category': 'Sale',
    'summary': 'Define credit limits for each customer',
    'website': '',
    'version': '10.0.1.0',
    'description': """
- Define a credit limit on the partner
- On the SaleOrder, if the amount + open invoices exceeds credit limit, the
Order will need approval from the Sales Manager
- On the webshop, customers will not be able to purchase further products via
wire transfer, if the open invoices plus the current order exceed the
pre-defined credit limit for this customer.
        """,
    'author': 'Niboo',
    'depends': [
        'account',
        'website_sale',
        'hr',
    ],
    'data': [
        'views/partner_view.xml',
        'views/sale_view.xml',
        'wizards/credit_limit_wizard.xml',
        'templates/assets.xml',
    ],
    'qweb' : [
    ],
    'demo': [
    ],
    'installable': True,
    'application': False,
}
