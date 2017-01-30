# -*- coding: utf-8 -*-
# © 2017 Pierre Faniel
# © 2017 Niboo SPRL (<https://www.niboo.be/>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Harmonized System Codes',
    'category': 'Product',
    'summary': 'Specify HS Codes on your products',
    'website': 'https://www.niboo.be/',
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'description': '''
- Allows to specify HS Codes on your products
- Allows to categorize codes by HS Groups linked to a country
    ''',
    'author': 'Niboo',
    'depends': [
        'sale',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/hs_code.xml',
        'views/hs_group.xml',
        'views/product.xml',
        'views/res_country.xml',
    ],
    'installable': True,
    'application': False,
}
