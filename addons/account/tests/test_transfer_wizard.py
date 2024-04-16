#-*-coding:utf-8-*-
fromflectra.addons.account.tests.commonimportAccountTestInvoicingCommon
fromflectra.testsimporttagged,Form
importtime

@tagged('post_install','-at_install')
classTestTransferWizard(AccountTestInvoicingCommon):

    @classmethod
    defsetUpClass(cls,chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

        cls.company=cls.company_data['company']
        cls.receivable_account=cls.company_data['default_account_receivable']
        cls.payable_account=cls.company_data['default_account_payable']
        cls.accounts=cls.env['account.account'].search([('reconcile','=',False),('company_id','=',cls.company.id)],limit=5)
        cls.journal=cls.company_data['default_journal_misc']

        #Setrateforbasecurrencyto1
        cls.env['res.currency.rate'].search([('company_id','=',cls.company.id),('currency_id','=',cls.company.currency_id.id)]).write({'rate':1})

        #Createtestcurrencies
        cls.test_currency_1=cls.env['res.currency'].create({
            'name':"PMK",
            'symbol':'P',
        })

        cls.test_currency_2=cls.env['res.currency'].create({
            'name':"toto",
            'symbol':'To',
        })

        cls.test_currency_3=cls.env['res.currency'].create({
            'name':"titi",
            'symbol':'Ti',
        })

        #Createtestrates
        cls.env['res.currency.rate'].create({
            'name':time.strftime('%Y')+'-'+'01'+'-01',
            'rate':0.5,
            'currency_id':cls.test_currency_1.id,
            'company_id':cls.company.id
        })

        cls.env['res.currency.rate'].create({
            'name':time.strftime('%Y')+'-'+'01'+'-01',
            'rate':2,
            'currency_id':cls.test_currency_2.id,
            'company_id':cls.company.id
        })

        cls.env['res.currency.rate'].create({
            'name':time.strftime('%Y')+'-'+'01'+'-01',
            'rate':10,
            'currency_id':cls.test_currency_3.id,
            'company_id':cls.company.id
        })

        #Createanaccountusingaforeigncurrency
        cls.test_currency_account=cls.env['account.account'].create({
            'name':'testdestinationaccount',
            'code':'test_dest_acc',
            'user_type_id':cls.env['ir.model.data'].xmlid_to_res_id('account.data_account_type_current_assets'),
            'currency_id':cls.test_currency_3.id,
        })

        #Createtestaccount.move
        cls.move_1=cls.env['account.move'].create({
            'journal_id':cls.journal.id,
            'line_ids':[
                (0,0,{
                    'name':"test1_1",
                    'account_id':cls.receivable_account.id,
                    'debit':500,
                }),
                (0,0,{
                    'name':"test1_2",
                    'account_id':cls.accounts[0].id,
                    'credit':500,
                }),
                (0,0,{
                    'name':"test1_3",
                    'account_id':cls.accounts[0].id,
                    'debit':800,
                    'partner_id':cls.partner_a.id,
                }),
                (0,0,{
                    'name':"test1_4",
                    'account_id':cls.accounts[1].id,
                    'credit':500,
                }),
                (0,0,{
                    'name':"test1_5",
                    'account_id':cls.accounts[2].id,
                    'credit':300,
                    'partner_id':cls.partner_a.id,
                }),
                (0,0,{
                    'name':"test1_6",
                    'account_id':cls.accounts[0].id,
                    'debit':270,
                    'currency_id':cls.test_currency_1.id,
                    'amount_currency':540,
                }),
                (0,0,{
                    'name':"test1_7",
                    'account_id':cls.accounts[1].id,
                    'credit':140,
                }),
                (0,0,{
                    'name':"test1_8",
                    'account_id':cls.accounts[2].id,
                    'credit':160,
                }),
                (0,0,{
                    'name':"test1_9",
                    'account_id':cls.accounts[2].id,
                    'debit':30,
                    'currency_id':cls.test_currency_2.id,
                    'amount_currency':15,
                }),
            ]
        })
        cls.move_1.action_post()

        cls.move_2=cls.env['account.move'].create({
            'journal_id':cls.journal.id,
            'line_ids':[
                (0,0,{
                    'name':"test2_1",
                    'account_id':cls.accounts[1].id,
                    'debit':400,
                }),
                (0,0,{
                    'name':"test2_2",
                    'account_id':cls.payable_account.id,
                    'credit':400,
                }),
                (0,0,{
                    'name':"test2_3",
                    'account_id':cls.accounts[3].id,
                    'debit':250,
                    'partner_id':cls.partner_a.id,
                }),
                (0,0,{
                    'name':"test2_4",
                    'account_id':cls.accounts[1].id,
                    'debit':480,
                    'partner_id':cls.partner_b.id,
                }),
                (0,0,{
                    'name':"test2_5",
                    'account_id':cls.accounts[2].id,
                    'credit':730,
                    'partner_id':cls.partner_a.id,
                }),
                (0,0,{
                    'name':"test2_6",
                    'account_id':cls.accounts[2].id,
                    'credit':412,
                    'partner_id':cls.partner_a.id,
                    'currency_id':cls.test_currency_2.id,
                    'amount_currency':-633,
                }),
                (0,0,{
                    'name':"test2_7",
                    'account_id':cls.accounts[1].id,
                    'debit':572,
                }),
                (0,0,{
                    'name':"test2_8",
                    'account_id':cls.accounts[2].id,
                    'credit':100,
                    'partner_id':cls.partner_a.id,
                    'currency_id':cls.test_currency_2.id,
                    'amount_currency':-123,
                }),
                (0,0,{
                    'name':"test2_9",
                    'account_id':cls.accounts[2].id,
                    'credit':60,
                    'partner_id':cls.partner_a.id,
                    'currency_id':cls.test_currency_1.id,
                    'amount_currency':-10,
                }),
            ]
        })
        cls.move_2.action_post()


    deftest_transfer_wizard_reconcile(self):
        """Testsreconciliationwhendoingatransferwiththewizard
        """
        active_move_lines=(self.move_1+self.move_2).mapped('line_ids').filtered(lambdax:x.account_id.user_type_id.typein('receivable','payable'))

        #Weuseaformtopassthecontextproperlytothedepends_contextmove_line_idsfield
        context={'active_model':'account.move.line','active_ids':active_move_lines.ids}
        withForm(self.env['account.automatic.entry.wizard'].with_context(context))aswizard_form:
            wizard_form.action='change_account'
            wizard_form.destination_account_id=self.receivable_account
            wizard_form.journal_id=self.journal
        wizard=wizard_form.save()

        transfer_move_id=wizard.do_action()['res_id']
        transfer_move=self.env['account.move'].browse(transfer_move_id)

        payable_transfer=transfer_move.line_ids.filtered(lambdax:x.account_id==self.payable_account)
        receivable_transfer=transfer_move.line_ids.filtered(lambdax:x.account_id==self.receivable_account)

        self.assertTrue(payable_transfer.reconciled,"Payablelineofthetransfermoveshouldbefullyreconciled")
        self.assertAlmostEqual(self.move_1.line_ids.filtered(lambdax:x.account_id==self.receivable_account).amount_residual,100,self.company.currency_id.decimal_places,"Receivablelineoftheoriginalmoveshouldbepartiallyreconciled,andstillhavearesidualamountof100(500-400frompayableaccount)")
        self.assertTrue(self.move_2.line_ids.filtered(lambdax:x.account_id==self.payable_account).reconciled,"Payablelineoftheoriginalmoveshouldbefullyreconciled")
        self.assertAlmostEqual(receivable_transfer.amount_residual,0,self.company.currency_id.decimal_places,"Receivablelinefromthetransfermoveshouldhavenothinglefttoreconcile")
        self.assertAlmostEqual(payable_transfer.debit,400,self.company.currency_id.decimal_places,"400shouldhavebeendebitedfrompayableaccounttoapplythetransfer")
        self.assertAlmostEqual(receivable_transfer.credit,400,self.company.currency_id.decimal_places,"400shouldhavebeencreditedtoreceivableaccounttoapplythetransfer")

    deftest_transfer_wizard_grouping(self):
        """Testsgrouping(byaccountandpartner)whendoingatransferwiththewizard
        """
        active_move_lines=(self.move_1+self.move_2).mapped('line_ids').filtered(lambdax:x.namein('test1_3','test1_4','test1_5','test2_3','test2_4','test2_5','test2_6','test2_8'))

        #Weuseaformtopassthecontextproperlytothedepends_contextmove_line_idsfield
        context={'active_model':'account.move.line','active_ids':active_move_lines.ids}
        withForm(self.env['account.automatic.entry.wizard'].with_context(context))aswizard_form:
            wizard_form.action='change_account'
            wizard_form.destination_account_id=self.accounts[4]
            wizard_form.journal_id=self.journal
        wizard=wizard_form.save()

        transfer_move_id=wizard.do_action()['res_id']
        transfer_move=self.env['account.move'].browse(transfer_move_id)

        groups={}
        forlineintransfer_move.line_ids:
            key=(line.account_id,line.partner_idorNone,line.currency_id)
            self.assertFalse(groups.get(key),"Thereshouldbeonlyonelineper(account,partner,currency)groupinthetransfermove.")
            groups[key]=line

        self.assertAlmostEqual(groups[(self.accounts[0],self.partner_a,self.company_data['currency'])].balance,-800,self.company.currency_id.decimal_places)
        self.assertAlmostEqual(groups[(self.accounts[1],None,self.company_data['currency'])].balance,500,self.company.currency_id.decimal_places)
        self.assertAlmostEqual(groups[(self.accounts[1],self.partner_b,self.company_data['currency'])].balance,-480,self.company.currency_id.decimal_places)
        self.assertAlmostEqual(groups[(self.accounts[2],self.partner_a,self.company_data['currency'])].balance,1030,self.company.currency_id.decimal_places)
        self.assertAlmostEqual(groups[(self.accounts[2],self.partner_a,self.test_currency_2)].balance,512,self.company.currency_id.decimal_places)
        self.assertAlmostEqual(groups[(self.accounts[3],self.partner_a,self.company_data['currency'])].balance,-250,self.company.currency_id.decimal_places)


    deftest_transfer_wizard_currency_conversion(self):
        """Testsmulticurrencyuseofthetransferwizard,checkingtheconversion
        ispropperlydonewhenusingadestinationaccountwithacurrency_idset.
        """
        active_move_lines=self.move_1.mapped('line_ids').filtered(lambdax:x.namein('test1_6','test1_9'))

        #Weuseaformtopassthecontextproperlytothedepends_contextmove_line_idsfield
        context={'active_model':'account.move.line','active_ids':active_move_lines.ids}
        withForm(self.env['account.automatic.entry.wizard'].with_context(context))aswizard_form:
            wizard_form.action='change_account'
            wizard_form.destination_account_id=self.test_currency_account
            wizard_form.journal_id=self.journal
        wizard=wizard_form.save()

        transfer_move_id=wizard.do_action()['res_id']
        transfer_move=self.env['account.move'].browse(transfer_move_id)

        destination_line=transfer_move.line_ids.filtered(lambdax:x.account_id==self.test_currency_account)
        self.assertEqual(destination_line.currency_id,self.test_currency_3,"Transferringtoanaccountwithacurrencysetshouldkeepthiscurrencyonthetransferline.")
        self.assertAlmostEqual(destination_line.amount_currency,3000,self.company.currency_id.decimal_places,"Transferringtwolineswithdifferentcurrencies(andthesamepartner)onanaccountwithacurrencysetshouldconvertthebalanceoftheselinesintothisaccount'scurrency(here(270+30)*10=3000)")


    deftest_transfer_wizard_no_currency_conversion(self):
        """Testsmulticurrencyuseofthetransferwizard,verifyingthat
        currencyamountsarekeptondistinctlineswhentransferringtoan
        accountwithoutanycurrencyspecified.
        """
        active_move_lines=self.move_2.mapped('line_ids').filtered(lambdax:x.namein('test2_9','test2_6','test2_8'))

        #Weuseaformtopassthecontextproperlytothedepends_contextmove_line_idsfield
        context={'active_model':'account.move.line','active_ids':active_move_lines.ids}
        withForm(self.env['account.automatic.entry.wizard'].with_context(context))aswizard_form:
            wizard_form.action='change_account'
            wizard_form.destination_account_id=self.receivable_account
            wizard_form.journal_id=self.journal
        wizard=wizard_form.save()

        transfer_move_id=wizard.do_action()['res_id']
        transfer_move=self.env['account.move'].browse(transfer_move_id)

        destination_lines=transfer_move.line_ids.filtered(lambdax:x.account_id==self.receivable_account)
        self.assertEqual(len(destination_lines),2,"Twolinesshouldhavebeencreatedondestinationaccount:oneforeachcurrency(thelineswithsamepartnerandcurrencyshouldhavebeenaggregated)")
        self.assertAlmostEqual(destination_lines.filtered(lambdax:x.currency_id==self.test_currency_1).amount_currency,-10,self.test_currency_1.decimal_places)
        self.assertAlmostEqual(destination_lines.filtered(lambdax:x.currency_id==self.test_currency_2).amount_currency,-756,self.test_currency_2.decimal_places)
