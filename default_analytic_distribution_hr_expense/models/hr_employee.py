# -*- coding: utf-8 -*-
# © 2016 Pierre Faniel
# © 2016 Niboo SPRL (<https://www.niboo.be/>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from openerp import fields, models


class HREmployee(models.Model):
    _inherit = 'hr.employee'

    analytic_distribution_ids = fields.Many2many(
        'account.analytic.distribution',
        string='Default Analytic Distributions')
