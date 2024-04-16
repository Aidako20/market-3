#-*-coding:utf-8-*-
fromflectra.addons.account.tests.commonimportAccountTestInvoicingCommon
fromflectra.testsimporttagged
fromflectra.exceptionsimportUserError


@tagged('post_install','-at_install')
classTestAccountTax(AccountTestInvoicingCommon):

    deftest_changing_tax_company(self):
        '''Ensureyoucan'tchangethecompanyofanaccount.taxiftherearesomejournalentries'''

        #Avoidduplicatekeyvalueviolatesuniqueconstraint"account_tax_name_company_uniq".
        self.company_data['default_tax_sale'].name='test_changing_account_company'

        self.env['account.move'].create({
            'move_type':'out_invoice',
            'date':'2019-01-01',
            'invoice_line_ids':[
                (0,0,{
                    'name':'invoice_line',
                    'quantity':1.0,
                    'price_unit':100.0,
                    'tax_ids':[(6,0,self.company_data['default_tax_sale'].ids)],
                }),
            ],
        })

        withself.assertRaises(UserError),self.cr.savepoint():
            self.company_data['default_tax_sale'].company_id=self.company_data_2['company']
