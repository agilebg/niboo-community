# -*- coding: utf-8 -*-
# © 2016 Pierre Faniel
# © 2016 Niboo SPRL (<https://www.niboo.be/>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp import models


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    def _get_sale_order_line(self, vals=None):
        result = dict(vals or {})
        if self.is_timesheet:
            if result.get('so_line'):
                sol = self.env['sale.order.line'].browse([result['so_line']])
            else:
                sol = self.so_line

            if sol and sol.product_id != self.product_id:
                sol = False

            if not sol and self.account_id and self.product_id:
                domain = [
                    ('order_id.project_id', '=', self.account_id.id),
                    ('state', '=', 'sale'),
                    ('product_id.track_service', '=', 'timesheet'),
                    ('product_id.type', '=', 'service'),
                    ('product_id','=',self.product_id.id)]
                sol = self.env['sale.order.line'].search(domain, limit=1)
            if sol:
                result.update({
                    'so_line': sol.id,
                    'product_id': sol.product_id.id,
                })
                result = self._get_timesheet_cost(result)

        return super(AccountAnalyticLine, self)._get_sale_order_line(
            vals=result)
