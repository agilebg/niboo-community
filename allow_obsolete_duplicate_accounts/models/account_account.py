# -*- coding: utf-8 -*-
# © 2017 Pierre Faniel
# © 2017 Niboo SPRL (<https://www.niboo.be/>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp import api, exceptions, models


class AccountAccount(models.Model):
    _inherit = 'account.account'

    _sql_constraints = [
        ('code_company_uniq', 'check(1 = 1)', '')
    ]

    @api.multi
    @api.constrains('code', 'name', 'company_id', 'deprecated')
    def check_unique_code(self):
        for account in self.filtered(lambda a: not a.deprecated):
            if self.env['account.account'].search([
                ('code', '=', account.code),
                ('company_id', '=', account.company_id.id),
                ('id', '!=', account.id),
                ('deprecated', '=', False),
            ]):
                raise exceptions.ValidationError(
                    'The code of the account must be unique per company !')
