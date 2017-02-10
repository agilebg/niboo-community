# -*- coding: utf-8 -*-
# © 2017 Tobias Zehntner
# © 2017 Niboo SPRL (https://www.niboo.be/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import datetime, dateutil, logging, random, string
from dateutil.relativedelta import relativedelta
from odoo.tests.common import TransactionCase

# TODO implement logger so erros can be tracked specifically (with which user, partner etc)
# _logger = logging.getLogger(__name__)


class TestCreditLimit(TransactionCase):
    def setUp(self):
        super(TestCreditLimit, self).setUp()

        employee = self.get_employee()
        manager = self.get_manager(employee)
        sales_manager_user = self.create_user('SaleManagerUser')
        sales_manager_user.write({'groups_id': [
            (4, self.ref('sales_team.group_sale_manager'))]})
        customer = self.get_customer([employee.user_id.partner_id.id,
                                      manager.user_id.partner_id.id,
                                      sales_manager_user.partner_id.id])
        portal_user = self.create_portal_user(customer)
        product = self.get_product()
        overdue_invoice = self.create_invoice(product, customer)

        overdue_invoice.date = datetime.date.today() - relativedelta(months=1)

        # TODO check that customer.credit is above 0
        print 'test'




        # AccountInvoice = self.env['account.invoice']
        # overdue_invoice = AccountInvoice.with_context(
        #     employee_id=employee.id).create({})

    ### TESTS ###
    def test_sale_flow(self):
        """
        Test Credit Limit: Happy flow
        """
        print 'happy flow'
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
    def create_user(self, name):
        return self.env['res.users'].create({'name': name,
                                             'login': name})

    def create_portal_user(self, customer):
        portal_user = self.create_user('PortalUser')
        portal_user.write({'groups_id': [
            (6, 0, [self.ref('base.group_portal')])]})
        portal_user.partner_id = customer.id
        return portal_user

    def get_parents(self, emp):
        parents = []
        if emp.parent_id:
            parents.append(emp.parent_id)
            parents.extend(self.get_parents(emp.parent_id))
        return parents

    def get_employee(self, ignore_ids=None):
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
            ('user_id', '!=', 1)])
        if employee_ids:
            return employee_ids[random.randint(0, len(employee_ids)-1)]
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
            manager = self.get_employee([employee.id])
            employee.parent_id = manager
            return manager

    def get_customer(self, ignore_ids=None):
        ResPartner = self.env['res.partner']
        if ignore_ids is None:
            ignore_ids = []
        customer_ids = ResPartner.search([
            ('id', 'not in', ignore_ids),
            ('customer', '=', True)])
        if customer_ids:
            return customer_ids[random.randint(0, len(customer_ids)-1)]
        else:
            name = ''.join(
                random.choice(string.ascii_lowercase) for _ in range(6))
            return ResPartner.create({'name': name,
                                      'customer': True})

    def create_invoice(self, product, partner):
        account_payable = self.env['account.account'].search([(
            'user_type_id', '=', self.env.ref(
                'account.data_account_type_payable').id)], limit=1)
        account_expenses = self.env['account.account'].search([(
            'user_type_id', '=', self.env.ref(
                'account.data_account_type_expenses').id)], limit=1)

        invoice = self.env['account.invoice'].create({
            'partner_id': partner.id,
            'reference_type': 'none',
            'name': "Supplier Invoice",
            'type': "in_invoice",
            'account_id': account_payable.id,
        })
        self.env['account.invoice.line'].create({
            'product_temp_id': product.id,
            'quantity': 1,
            'price_unit': 100,
            'invoice_id': invoice.id,
            'name': 'something',
            'account_id': account_expenses.id,
        })
        invoice.action_invoice_open()
        return invoice

    def get_product(self, ignore_ids=None):
        ProductTemplate = self.env['product.template']
        if ignore_ids is None:
            ignore_ids = []
        product_ids = ProductTemplate.search([
            ('id', 'not in', ignore_ids),
            ('list_price', '>', 0),
            ('sale_ok', '=', True)
        ])
        if product_ids:
            return product_ids[random.randint(0, len(product_ids)-1)]
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
            return ProductTemplate.create(vals)
