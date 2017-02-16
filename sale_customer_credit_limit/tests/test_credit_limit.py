# -*- coding: utf-8 -*-
# © 2017 Tobias Zehntner
# © 2017 Niboo SPRL (https://www.niboo.be/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import random
import string

from datetime import date
from dateutil.relativedelta import relativedelta
from odoo.tests.common import TransactionCase

USE_EXISTING_RECS = True


# TODO implement logger so erros can be tracked specifically (with which user, partner etc)
# _logger = logging.getLogger(__name__)


class TestCreditLimit(TransactionCase):
    def setUp(self):
        super(TestCreditLimit, self).setUp()

        self.admin = self.env.user
        self.company = self.admin.company_id
        self.employee = self.get_employee(self.company, None)
        self.employee.user_id.write({'groups_id': [
            (4, self.ref('sales_team.group_sale_salesman'))]})
        self.manager = self.get_manager(self.employee)
        self.sale_manager_user = self.create_user('SaleManagerUser')
        self.sale_manager_user.write({'groups_id': [
            (4, self.ref('sales_team.group_sale_manager'))]})
        self.customer = self.get_credit_free_customer(
            [self.employee.user_id.partner_id.id,
             self.manager.user_id.partner_id.id,
             self.sale_manager_user.partner_id.id])
        self.portal_user = self.create_portal_user(self.customer)
        self.product = self.get_product()
        self.sale_order = self.create_sale_order()

        # In the setup, the customer should have no credit
        self.assertEqual(self.customer.credit, 0)

    ### TESTS ###
    def test_default_credit_limit(self):
        """
        Test Credit Limit: Check if default credit limit is set
        """
        amount = 300
        settings = self.env['sale.config.settings'].search([], limit=1)
        settings.default_credit_limit = amount
        new_partner = self.create_partner()
        self.assertEqual(new_partner.credit_limit, amount)

    def test_no_credit(self):
        """
        Test Credit Limit: Customer has no credit -> SO should be confirmed
        """
        # SO should be confirmed
        self.sale_order.sudo(self.employee.user_id.id).action_confirm()
        self.assertEqual(self.sale_order.state, 'sale')

    def test_no_overdue_credit(self):
        """
        Test Credit Limit: Customer has no overdue credit -> SO should be confirmed
        """
        amount = 300
        self.customer.credit_limit = 200
        currency = self.company.currency_id
        normal_invoice = self.create_invoice(self.product,
                                             self.customer,
                                             currency, amount)
        # Credit limit should be set
        self.assertEqual(self.customer.credit_limit, 200)
        # Customer should have credit
        self.assertEqual(self.customer.credit, amount)

        # Since credit is not overdue, SO should be confirmed
        self.sale_order.sudo(self.employee.user_id.id).action_confirm()
        self.assertEqual(self.sale_order.state, 'sale')

    def test_overdue_by_payment_terms(self):
        pass

    def test_overdue_by_no_payment_term_defined(self):
        pass

    def test_overdue_credit_employee(self):
        """
        Test Credit Limit: Overdue credit -> exceed credit approval flow
        """
        amount = 300
        credit_limit = self.customer.credit_limit = 200
        currency = self.company.currency_id
        overdue_invoice = self.create_invoice(self.product,
                                              self.customer,
                                              currency, amount, True)
        # Credit limit should be set
        self.assertEqual(self.customer.credit_limit, 200)
        # Customer should have credit
        self.assertEqual(self.customer.credit, amount)

        wizard_vals = self.sale_order.sudo(
            self.employee.user_id.id).action_confirm()

        # Since credit is overdue, SO should not be confirmed
        self.assertEqual(self.sale_order.state, 'draft')

        context = wizard_vals['context']
        context['active_id'] = self.sale_order.id
        context['active_model'] = 'sale.order'
        wizard = self.env['sale.customer.credit.limit.wizard'].with_context(
            context).create({})
        exceeded_credit = self.sale_order.amount_total + amount - credit_limit

        # Wizard should show the correct exceeded credit
        self.assertEqual(wizard.exceeded_credit, exceeded_credit)

        wizard.sudo(self.employee.user_id.id).action_exceed_limit()

        # Sale Order should be in approve state
        self.assertEqual(self.sale_order.state, 'approve')

        # Check if message to manager has been sent

        # Check that employee can't approve SO

        # Check employee can set it back to draft

        # Re-send for approval

        # Check that manager can approve SO

    def test_overdue_credit_manager(self):
        """
        Test Credit Limit: Manager can exceed credit directly
        """
        # Check that manager can approve SO directly
        pass

    def test_multi_currency(self):
        pass

    def test_webshop(self):
        pass


    ### SETUP GET RECORDS FROM DATABASE ###

    def get_company(self):
        if USE_EXISTING_RECS:
            ResCompany = self.env['res.company']
            company_ids = ResCompany.search([])
            return company_ids[random.randint(0, len(company_ids) - 1)]
        else:
            return self.create_company()

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
        if employee_ids and USE_EXISTING_RECS:
            return employee_ids[random.randint(0, len(employee_ids) - 1)]
        else:
            name = ''.join(
                random.choice(string.ascii_lowercase) for _ in range(6))
            return self.create_employee(self.create_user(name))

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
            ('customer', '=', True),
            ('company_type', '=', 'company'),
            ('company_id', '=', self.company.id)])
        if customer_ids and USE_EXISTING_RECS:
            return customer_ids[random.randint(0, len(customer_ids) - 1)]
        else:
            customer = self.create_partner()
            customer.write({'customer': True,
                            'company_id': self.company.id,
                            'company_type': 'company'})
            return customer

    def get_product(self, ignore_ids=None):
        ProductProduct = self.env['product.product']
        if ignore_ids is None:
            ignore_ids = []
        product_ids = ProductProduct.search([
            ('id', 'not in', ignore_ids),
            ('list_price', '>', 0),
            ('sale_ok', '=', True)
        ])
        if product_ids and USE_EXISTING_RECS:
            return product_ids[random.randint(0, len(product_ids) - 1)]
        else:
            return self.create_product()

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

    def get_warehouse(self):
        warehouse = self.env['stock.warehouse'].search([
            ('company_id', '=', self.company.id)], limit=1)
        if warehouse and USE_EXISTING_RECS:
            return warehouse
        else:
            return self.create_warehouse()

    def get_pricelist(self):
        pricelist = self.env['product.pricelist'].search(
            [('currency_id', '=', self.company.currency_id.id)], limit=1)
        if pricelist and USE_EXISTING_RECS:
            return pricelist
        else:
            return self.create_pricelist()


    ### SETUP CREATE RECORDS ###

    def create_company(self):
        currency = self.get_currency()
        name = ''.join(
            random.choice(string.ascii_lowercase) for _ in range(6))
        partner = self.env['res.partner'].create({'name': name})
        company = self.env['res.company'].create({'name': name,
                                                  'currency_id': currency.id,
                                                  'partner_id': partner.id,
                                                  'manufacturing_lead': 5.0,
                                                  })
        return company

    def create_product(self):
        ProductProduct = self.env['product.product']
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
            'company_id': self.company.id,
        }
        return ProductProduct.create(vals)

    def create_warehouse(self):
        Warehouse = self.env['stock.warehouse']
        return Warehouse.create({'name': 'testWarehouse',
                                 'code': 'tw',
                                 'company_id': self.company.id})

    def create_sale_order(self):
        SaleOrder = self.env['sale.order']
        line_vals = {
            'product_id': self.product.id,
            'product_uom_qty': 1,
            'product_uom': self.product.uom_id.id,
            'price_unit': 500,
        }
        order_vals = {
            'partner_id': self.customer.id,
            'user_id': self.employee.user_id.id,
            'date_order': date.today(),
            'order_line': [(0, 0, line_vals)],
            'picking_policy': 'direct',
            'warehouse_id': self.get_warehouse().id,
            'company_id': self.company.id,
            'pricelist_id': self.get_pricelist().id,
        }
        sale_order = SaleOrder.sudo(self.employee.user_id.id).create(order_vals)
        return sale_order

    def create_pricelist(self):
        name = ''.join(
            random.choice(string.ascii_lowercase) for _ in range(6))
        return self.env['product.pricelist'].create({
            'name': name,
            'company_id': self.company.id,
            'currency_id': self.company.currency_id.id})

    def create_user(self, name):
        user = self.env['res.users'].create({'name': name,
                                             'login': '%s@test.com' % name,
                                             'email': '%s@test.com' % name,
                                             'company_ids': [
                                                 (4, self.company.id)],
                                             'company_id': self.company.id})
        user.write({'groups_id': [
            (4, self.ref('sales_team.group_sale_salesman'))]})
        return user

    def create_portal_user(self, customer):
        portal_user = self.create_user('PortalUser')
        portal_user.write({'groups_id': [
            (6, 0, [self.ref('base.group_portal')])]})
        portal_user.partner_id = customer.id
        return portal_user

    def create_employee(self, user):
        HREmployee = self.env['hr.employee']
        return HREmployee.create({'name': user.name,
                                  'user_id': user.id,
                                  'company_id': self.company.id})

    def create_partner(self):
        ResPartner = self.env['res.partner']
        name = ''.join(
            random.choice(string.ascii_lowercase) for _ in range(6))
        return ResPartner.create({'name': name})

    def create_invoice(self, product, partner, currency, amount,
                       overdue=False):
        account_revenue = self.env['account.account'].search([(
            'user_type_id', '=', self.env.ref(
                'account.data_account_type_revenue').id)], limit=1)
        payment_terms = self.env.ref('account.account_payment_term_15days')

        invoice = self.env['account.invoice'].create({
            'partner_id': partner.id,
            'reference_type': 'none',
            'name': "Supplier Invoice",
            'type': "out_invoice",
            'account_id': partner.property_account_receivable_id.id,
            'date_invoice': date.today() if not overdue
            else date.today() - relativedelta(months=3),
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
