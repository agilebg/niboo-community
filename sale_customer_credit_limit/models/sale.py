# -*- coding: utf-8 -*-
# © 2017 Tobias Zehntner
# © 2017 Niboo SPRL (https://www.niboo.be/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import date
from odoo import api, fields, models


class SaleConfiguration(models.TransientModel):
    _inherit = 'sale.config.settings'

    company_currency_id = fields.Many2one('res.currency',
                                          compute='get_currency')
    default_credit_limit = fields.Monetary(
        'Default Customer Credit Limit *',
        related='company_id.default_credit_limit',
        currency_field='company_currency_id')

    def get_currency(self):
        self.company_currency_id = self.env.user.company_id.currency_id


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Add 'To Approve' to Sale Order states
    state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('approve', 'To Approve'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')])

    @api.multi
    def action_confirm(self):
        for order in self:
            customer = order.partner_id
            credit_limit = order.partner_id.credit_limit
            company_currency = order.company_id.currency_id
            order_amount = order.currency_id.compute(order.amount_total,
                                                     company_currency)
            open_credit = 0

            past_due_invoices = self.env['account.invoice'].search([
                ('type', '=', 'out_invoice'),
                ('company_id', '=', order.company_id.id),
                ('partner_id', '=', customer.id),
                ('state', 'in', ['open']),
                '|', ('payment_term_id', '=', False),
                ('date_due', '<', date.today()),
            ])
            for invoice in past_due_invoices:
                # TODO test with db that contains a full res_currency_rate table
                amount = invoice.currency_id.compute(invoice.residual,
                                                     company_currency)
                open_credit += amount

            exceeded_credit = (open_credit + order_amount) - credit_limit

            if (open_credit > 0 and exceeded_credit > 0) \
                    and not self._context.get('exceed_credit_limit', False):
                context = {'credit': {'open_credit': open_credit,
                                      'exceeded_credit': exceeded_credit}}
                return {
                    'context': context,
                    'type': 'ir.actions.act_window',
                    'name': 'Above Customer Credit Limit',
                    'res_model': 'sale.customer.credit.limit.wizard',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'view_id': self.env.ref(
                        'sale_customer_credit_limit.credit_limit_wizard').id,
                    'target': 'new',
                }
            else:
                super(SaleOrder, self).action_confirm()
        return True
