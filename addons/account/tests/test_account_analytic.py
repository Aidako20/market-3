#-*-coding:utf-8-*-
fromflectra.addons.account.tests.commonimportAccountTestInvoicingCommon
fromflectra.testsimporttagged
fromflectra.exceptionsimportUserError


@tagged('post_install','-at_install')
classTestAccountAnalyticAccount(AccountTestInvoicingCommon):

    @classmethod
    defsetUpClass(cls,chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

        cls.env.user.write({
            'groups_id':[
                (4,cls.env.ref('analytic.group_analytic_accounting').id),
                (4,cls.env.ref('analytic.group_analytic_tags').id),
            ],
        })

        #Bydefault,testsarerunwiththecurrentusersetonthefirstcompany.
        cls.env.user.company_id=cls.company_data['company']

        cls.test_analytic_account=cls.env['account.analytic.account'].create({'name':'test_analytic_account'})
        cls.test_analytic_tag=cls.env['account.analytic.tag'].create({'name':'test_analytic_tag'})

    deftest_changing_analytic_company(self):
        '''Ensureyoucan'tchangethecompanyofanaccount.analytic.accountiftherearesomejournalentries'''

        self.env['account.move'].create({
            'move_type':'entry',
            'date':'2019-01-01',
            'line_ids':[
                (0,0,{
                    'name':'line_debit',
                    'account_id':self.company_data['default_account_revenue'].id,
                    'analytic_account_id':self.test_analytic_account.id,
                    'analytic_tag_ids':[(6,0,self.test_analytic_tag.ids)],
                }),
                (0,0,{
                    'name':'line_credit',
                    'account_id':self.company_data['default_account_revenue'].id,
                }),
            ],
        })

        #Setadifferentcompanyontheanalyticaccount.
        withself.assertRaises(UserError),self.cr.savepoint():
            self.test_analytic_account.company_id=self.company_data_2['company']

        #Makingtheanalyticaccountnotcompanydependentisallowed.
        self.test_analytic_account.company_id=False

        #Setadifferentcompanyontheanalytictag.
        withself.assertRaises(UserError),self.cr.savepoint():
            self.test_analytic_tag.company_id=self.company_data_2['company']

        #Makingtheanalytictagnotcompanydependentisallowed.
        self.test_analytic_tag.company_id=False
