# -*- coding: utf-8 -*-
# © 2017 Tobias Zehntner
# © 2017 Niboo SPRL (https://www.niboo.be/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SaleConfiguration(models.TransientModel):
    _inherit = 'sale.config.settings'

    default_credit_limit = fields.Float('Default Customer Credit Limit',
                                        default_model='res.partner')


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
            open_credit = order.partner_id.credit
            order_amount = order.amount_total
            exceeded_credit = (open_credit + order_amount) - credit_limit
            currency = order.company_id.currency_id

            context = {'credit': {'sale_order': order.id,
                                  'customer': customer.id,
                                  'currency': currency.id,
                                  'credit_limit': credit_limit,
                                  'open_credit': open_credit,
                                  'order_amount': order_amount,
                                  'exceeded_credit': exceeded_credit}}

            if open_credit > 0 and exceeded_credit > 0:
                return {
                    'context': context,
                    'type': 'ir.actions.act_window',
                    'name': 'Above Customer Credit Limit',
                    'res_model': 'sale.customer.credit.limit.wizard',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'view_id': self.env.ref(
                        'sale_customer_credit_limit.credit_limit_wizard_form').id,
                    'target': 'new',
                }
            else:
                super(SaleOrder, self).action_confirm()
        return True
