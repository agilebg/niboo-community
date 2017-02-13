# -*- coding: utf-8 -*-
# © 2017 Tobias Zehntner
# © 2017 Niboo SPRL (https://www.niboo.be/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import random
import string

from datetime import date
from dateutil.relativedelta import relativedelta
from odoo.tests.common import TransactionCase


# TODO implement logger so erros can be tracked specifically (with which user, partner etc)
# _logger = logging.getLogger(__name__)


class TestCreditLimit(TransactionCase):
    def setUp(self):
        super(TestCreditLimit, self).setUp()

        self.company = self.get_company()
        self.employee = self.get_employee(self.company, None)
        self.employee.user_id.write({'groups_id': [
            (4, self.ref('sales_team.group_sale_manager'))]})
        manager = self.get_manager(self.employee)
        self.sale_manager_user = self.create_user('SaleManagerUser')
        self.sale_manager_user.write({'groups_id': [
            (4, self.ref('sales_team.group_sale_manager'))]})
        self.customer = self.get_credit_free_customer(
            [self.employee.user_id.partner_id.id,
             manager.user_id.partner_id.id,
             self.sale_manager_user.partner_id.id])
        portal_user = self.create_portal_user(self.customer)
        self.product = self.get_product()
        currency1 = self.get_currency([self.company.currency_id.id])
        amount = 1000
        overdue_invoice = self.create_overdue_invoice(self.product,
                                                      self.customer,
                                                      currency1, amount, True)

        # TODO check that customer.credit is above 0
        print 'test'

    ### TESTS ###
    def test_default_credit_limit(self):
        """
        Test Credit Limit: Check if default credit limit is set
        """
        settings = self.env['sale.config.settings'].search([], limit=1)
        settings.default_credit_limit = 500
        new_partner = self.create_partner()
        self.assertEqual(new_partner.credit_limit, 500)

    def test_sale_flow(self):
        """
        Test Credit Limit: Normal flow
        """
        SaleOrder = self.env['sale.order']
        amount = 500
        currency = self.company.currency_id
        sale_order = self.create_sale_order()

        # The customer has no open invoices > should not trigger
        self.assertEqual(self.customer.credit, 0)

        normal_invoice = self.create_overdue_invoice(self.product,
                                                     self.customer,
                                                     currency, amount)
        # The customer has an open invoice which is not yet due > should not trigger

        overdue_invoice = self.create_overdue_invoice(self.product,
                                                      self.customer,
                                                      currency, amount, True)

        #

        # Employee can't approve
        # Set back to draft
        # Approve

        # Overdue invoice by payment terms
        # Overdue invoice by none term defined (immediate)

        # Check message sent
        pass

    def test_multi_currency(self):
        pass

    def test_webshop(self):
        pass

    ### SETUP ###
    def create_sale_order(self):
        SaleOrder = self.env['sale.order']
        line_vals = {
            'product_id': self.product.id,
            'product_uom_qty': 1,
            'product_uom': self.env.ref('product.product_uom_unit'),
            'price_unit': 500,
        }
        order_vals = {
            'partner_id': self.customer.id,
            'date_order': date.today(),
            'order_line': [line_vals],
            'picking_policy': 'direct',
        }
        sale_order = SaleOrder.sudo(self.employee.id).create(order_vals)
        return sale_order

    def create_user(self, name):
        return self.env['res.users'].create({'name': name,
                                             'login': name,
                                             'company_ids': [self.company.id],
                                             'company_id': self.company.id})

    def create_portal_user(self, customer):
        portal_user = self.create_user('PortalUser')
        portal_user.write({'groups_id': [
            (6, 0, [self.ref('base.group_portal')])]})
        portal_user.partner_id = customer.id
        return portal_user

    def get_company(self):
        ResCompany = self.env['res.company']
        company_ids = ResCompany.search([])
        return company_ids[random.randint(0, len(company_ids) - 1)]

    def get_parents(self, emp):
        parents = []
        if emp.parent_id:
            parents.append(emp.parent_id)
            parents.extend(self.get_parents(emp.parent_id))
        return parents

    def get_employee(self, company, ignore_ids=None):
        HREmployee = self.env['hr.employee']
        if ignore_ids:
            parents = self.get_parents(HREmployee.browse(ignore_ids))
            ignore_ids.extend([parent.id for parent in parents])
        else:
            ignore_ids = []
        employee_ids = HREmployee.search([
            ('id', 'not in', ignore_ids),
            ('parent_id', 'not in', ignore_ids),
            ('user_id', '!=', False),
            ('user_id', '!=', 1),
            ('company_id', '=', company.id)])
        if employee_ids:
            return employee_ids[random.randint(0, len(employee_ids) - 1)]
        else:
            name = ''.join(
                random.choice(string.ascii_lowercase) for _ in range(6))
            user = self.create_user(name)
            return HREmployee.create({'name': user.name,
                                      'user_id': user.id})

    def get_manager(self, employee):
        if employee.parent_id:
            return employee.parent_id
        else:
            manager = self.get_employee(self.company, [employee.id])
            employee.parent_id = manager
            return manager

    def get_credit_free_customer(self, ignore_ids=None):
        customer = self.get_customer(ignore_ids)
        while customer.credit != 0:
            customer = self.get_customer(ignore_ids)
        return customer

    def get_customer(self, ignore_ids=None):
        ResPartner = self.env['res.partner']
        if ignore_ids is None:
            ignore_ids = []
        customer_ids = ResPartner.search([
            ('id', 'not in', ignore_ids),
            ('customer', '=', True)])
        if customer_ids:
            return customer_ids[random.randint(0, len(customer_ids) - 1)]
        else:
            customer = self.create_partner()
            customer.customer = True
            return customer

    def create_partner(self):
        ResPartner = self.env['res.partner']
        name = ''.join(
            random.choice(string.ascii_lowercase) for _ in range(6))
        return ResPartner.create({'name': name,
                                  'customer': True})

    def create_overdue_invoice(self, product, partner, currency, amount,
                               overdue=False):
        account_receivable = self.env['account.account'].search([(
            'user_type_id', '=', self.env.ref(
                'account.data_account_type_receivable').id)], limit=1)
        account_revenue = self.env['account.account'].search([(
            'user_type_id', '=', self.env.ref(
                'account.data_account_type_revenue').id)], limit=1)
        payment_terms = self.env.ref('account.account_payment_term_15days')

        invoice = self.env['account.invoice'].create({
            'partner_id': partner.id,
            'reference_type': 'none',
            'name': "Supplier Invoice",
            'type': "in_invoice",
            'account_id': account_receivable.id,
            'date_invoice': date.today() if not overdue
            else date.today() - relativedelta(
                months=3),
            'payment_term_id': payment_terms.id,
            'currency_id': currency.id,
        })
        self.env['account.invoice.line'].create({
            'product_id': product.id,
            'quantity': 1,
            'price_unit': amount,
            'invoice_id': invoice.id,
            'name': 'something',
            'account_id': account_revenue.id,
        })
        invoice.action_invoice_open()
        return invoice

    def get_product(self, ignore_ids=None):
        ProductProduct = self.env['product.product']
        if ignore_ids is None:
            ignore_ids = []
        product_ids = ProductProduct.search([
            ('id', 'not in', ignore_ids),
            ('list_price', '>', 0),
            ('sale_ok', '=', True)
        ])
        if product_ids:
            return product_ids[random.randint(0, len(product_ids) - 1)]
        else:
            uom = self.env['product.uom'].search([], limit=1)
            name = ''.join(
                random.choice(string.ascii_lowercase) for _ in range(6))
            vals = {
                'name': name,
                'type': 'consu',
                'uom_id': uom.id,
                'uom_po_id': uom.id,
                'list_price': 1000,
                'sale_ok': True,
            }
            return ProductProduct.create(vals)

    def get_currency(self, ignore_ids=None):
        ResCurrency = self.env['res.currency']
        if ignore_ids is None:
            ignore_ids = []
        currency_ids = ResCurrency.search([
            ('id', 'not in', ignore_ids), ])
        if currency_ids:
            return currency_ids[random.randint(0, len(currency_ids) - 1)]
        else:
            inactive_ids = ResCurrency.search([
                ('id', 'not in', ignore_ids),
                ('active', '=', False)
            ])
            return inactive_ids[random.randint(0, len(inactive_ids) - 1)]
