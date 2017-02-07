# -*- coding: utf-8 -*-
# © 2017 Tobias Zehntner
# © 2017 Niboo SPRL (https://www.niboo.be/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, exceptions, fields, models


class SaleCustomerCreditLimitWizard(models.TransientModel):
    _name = 'sale.customer.credit.limit.wizard'

    sale_order = fields.Many2one('sale.order', compute='get_vals')
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  compute='get_vals')
    customer_id = fields.Many2one('res.partner', 'Customer', compute='get_vals')
    credit_limit = fields.Monetary('Credit Limit', compute='get_vals',
                                   currency_field='currency_id')
    open_credit = fields.Monetary('Unpaid Invoices', compute='get_vals',
                                  currency_field='currency_id')
    order_amount = fields.Monetary('Order Amount', compute='get_vals',
                                   currency_field='currency_id')
    exceeded_credit = fields.Monetary('Exceeded Credit', compute='get_vals',
                                      currency_field='currency_id')

    @api.multi
    @api.depends('currency_id')
    def get_vals(self):
        self.ensure_one()
        vals = self._context.get('credit')
        self.sale_order = vals.get('sale_order')
        self.customer_id = vals.get('customer')
        self.currency_id = vals.get('currency')
        self.credit_limit = vals.get('credit_limit')
        self.open_credit = vals.get('open_credit')
        self.order_amount = vals.get('order_amount')
        self.exceeded_credit = vals.get('exceeded_credit')

    @api.multi
    def action_exceed_limit(self):
        self.ensure_one()
        order = self.sale_order
        is_manager = self.env.user.has_group('sales_team.group_sale_manager')
        if is_manager:
            # Skip approval process for Sale Managers
            order.state = 'sale'
        else:
            # Set order 'To Approve' and notify manager
            order.state = 'approve'

            employee = self.env['hr.employee'].search([('user_id', '=', order.user_id.id)], limit=1)

            if not employee.parent_id:
                raise exceptions.ValidationError('The employee %s has no manager defined.' % employee.name)
            order.message_subscribe([employee.parent_id.id])
            subject = '%s needs approval' % order.name
            message = '''
            The Sale Order %s exceeds the customer credit limit and needs approval by %s:\n
            Customer: %s\n
            Currency: %s\n
            Credit Limit: %s\n
            Order Amount: %s\n
            Exceeded Credit: %s\n
            ''' % (order.name, employee.parent_id.name, self.customer_id.name, self.currency_id.name, self.credit_limit,
                   self.order_amount, self.exceeded_credit)

            order.message_post(message, subject=subject, subtype='mail.mt_comment',
                                       type='comment')

