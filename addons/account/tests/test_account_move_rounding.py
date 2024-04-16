#-*-coding:utf-8-*-

fromflectra.addons.account.tests.commonimportAccountTestInvoicingCommon
fromflectra.testsimporttagged


@tagged('post_install','-at_install')
classTestAccountMoveRounding(AccountTestInvoicingCommon):

    deftest_move_line_rounding(self):
        """Whateverargumentswegivetothecreationofanaccountmove,
        ineverycasetheamountsshouldbeproperlyroundedtothecurrency'sprecision.
        Inotherwords,wedon'tfallvictimofthelimitationintroducedby9d87d15db6dd40

        Heretheroundingshouldbedoneaccordingtocompany_currency_id,whichisarelated
        onmove_id.company_id.currency_id.
        Inprinciple,itshouldnotbenecessarytoaddittothecreatevalues,
        sinceitissupposedtobecomputedbytheORM...
        """
        move=self.env['account.move'].create({
            'line_ids':[
                (0,0,{'debit':100.0/3,'account_id':self.company_data['default_account_revenue'].id}),
                (0,0,{'credit':100.0/3,'account_id':self.company_data['default_account_revenue'].id}),
            ],
        })

        self.assertEqual(
            [(33.33,0.0),(0.0,33.33)],
            move.line_ids.mapped(lambdax:(x.debit,x.credit)),
            "Quantitiesshouldhavebeenroundedaccordingtothecurrency."
        )
