# -*- coding: utf-8 -*-
# © 2017 Pierre Faniel
# © 2017 Niboo SPRL (<https://www.niboo.be/>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import re
from odoo import api, exceptions, fields, models

HS_CODE_FORMAT = r'\d+(\.\d+)?(?=$| )'


class HSCode(models.Model):
    _name = 'hs.code'
    _description = 'Harmonized System Code'

    name = fields.Char('Code', required=True, index=True)
    description = fields.Char('Description', required=True)
    hs_group_id = fields.Many2one('hs.group', 'HS Group', required=True)
    product_id = fields.Many2one('product.template', 'Product', required=True)

    @api.multi
    @api.onchange('name')
    def _check_name(self):
        for hs_code in self:
            if hs_code.name:
                if not re.match(HS_CODE_FORMAT, hs_code.name):
                    raise exceptions.ValidationError('Invalid HS Code format')

    @api.onchange('product_id')
    def onchange_product(self):
        if self.product_id and not self.description:
            self.description = self.product_id.name

    _sql_constraints = [
        ('hs_code_unique', 'unique (name)', 'HS Code already exists'),
    ]
