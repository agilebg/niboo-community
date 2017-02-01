# -*- coding: utf-8 -*-
# © 2017 Pierre Faniel
# © 2017 Niboo SPRL (<https://www.niboo.be/>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class HSGroup(models.Model):
    _name = 'hs.group'
    _description = 'Harmonized System Group'

    name = fields.Char('Name', required=True)
    hs_code_ids = fields.One2many('hs.code', 'hs_group_id', 'HS Codes')
    country_ids = fields.Many2many('res.country', 'hs_group_country_rel',
                                   'group_id', 'country_id', 'Countries')
