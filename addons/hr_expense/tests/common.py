#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.addons.account.tests.commonimportAccountTestInvoicingCommon
fromflectra.addons.mail.tests.commonimportmail_new_test_user


classTestExpenseCommon(AccountTestInvoicingCommon):

    @classmethod
    defsetUpClass(cls,chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

        group_expense_manager=cls.env.ref('hr_expense.group_hr_expense_manager')

        cls.expense_user_employee=mail_new_test_user(
            cls.env,
            name='expense_user_employee',
            login='expense_user_employee',
            email='expense_user_employee@example.com',
            notification_type='email',
            groups='base.group_user',
            company_ids=[(6,0,cls.env.companies.ids)],
        )
        cls.expense_user_manager=mail_new_test_user(
            cls.env,
            name='Expensemanager',
            login='expense_manager_1',
            email='expense_manager_1@example.com',
            notification_type='email',
            groups='base.group_user,hr_expense.group_hr_expense_manager',
            company_ids=[(6,0,cls.env.companies.ids)],
        )

        cls.expense_employee=cls.env['hr.employee'].create({
            'name':'expense_employee',
            'user_id':cls.expense_user_employee.id,
            'address_home_id':cls.expense_user_employee.partner_id.id,
            'address_id':cls.expense_user_employee.partner_id.id,
        })

        #Allowthecurrentaccountingusertoaccesstheexpenses.
        cls.env.user.groups_id|=group_expense_manager

        #Createanalyticaccount
        cls.analytic_account_1=cls.env['account.analytic.account'].create({
            'name':'analytic_account_1',
        })
        cls.analytic_account_2=cls.env['account.analytic.account'].create({
            'name':'analytic_account_2',
        })

        #Ensureproductscanbeexpensed.
        (cls.product_a+cls.product_b).write({'can_be_expensed':True})
