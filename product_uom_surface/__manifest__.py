# -*- coding: utf-8 -*-
# © 2017 Tobias Zehntner
# © 2017 Niboo SPRL (https://www.niboo.be/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Product - UoM - Surface',
    'category': 'Product',
    'summary': 'Adds Surface UoM to Products',
    'website': 'https://www.niboo.be',
    'version': '10.0.1.0',
    'license': 'AGPL-3',
    'description': """
Add surface Unit of Measures to Products:
- square meter (m2)
- square centimeter (cm2)
- square milimeter (mm2)
- square yard (sq yd)
- square foot (sq ft)
- square inch (sq in)
        """,
    'author': 'Niboo',
    'depends': [
        'product',
    ],
    'data': [
        'data/product_data.xml',
    ],
    'qweb' : [
    ],
    'demo': [
    ],
    'installable': True,
    'application': False,
}
