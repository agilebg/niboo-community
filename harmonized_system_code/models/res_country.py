# -*- coding: utf-8 -*-
# © 2017 Pierre Faniel
# © 2017 Niboo SPRL (<https://www.niboo.be/>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class ResCountry(models.Model):
    _inherit = 'res.country'

    hs_group_id = fields.Many2one('hs.group', 'HS Group')
