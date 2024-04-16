#-*-coding:utf-8-*-
fromflectra.addons.account.tests.commonimportAccountTestInvoicingCommon
fromflectra.testsimporttagged


@tagged('post_install','-at_install')
classTestSettings(AccountTestInvoicingCommon):

    deftest_switch_taxB2B_taxB2C(self):
        """
        SincehavingusersbothinthetaxB2BandtaxB2Cgroupsraise,
        modificationsofthesettingsmustbedoneintherightorder;
        otherwiseitisimpossibletochangethesettings.
        """
        #ateachsettingchange,allusersshouldberemovedfromonegroupandaddedtotheother
        #sopickinganarbitrarywitnessshouldbeequivalenttocheckingthateverythingworked.
        config=self.env['res.config.settings'].create({})
        self.switch_tax_settings(config)

    defswitch_tax_settings(self,config):
        config.show_line_subtotals_tax_selection="tax_excluded"
        config._onchange_sale_tax()
        config.flush()
        config.execute()
        self.assertEqual(self.env.user.has_group('account.group_show_line_subtotals_tax_excluded'),True)
        self.assertEqual(self.env.user.has_group('account.group_show_line_subtotals_tax_included'),False)

        config.show_line_subtotals_tax_selection="tax_included"
        config._onchange_sale_tax()
        config.flush()
        config.execute()
        self.assertEqual(self.env.user.has_group('account.group_show_line_subtotals_tax_excluded'),False)
        self.assertEqual(self.env.user.has_group('account.group_show_line_subtotals_tax_included'),True)

        config.show_line_subtotals_tax_selection="tax_excluded"
        config._onchange_sale_tax()
        config.flush()
        config.execute()
        self.assertEqual(self.env.user.has_group('account.group_show_line_subtotals_tax_excluded'),True)
        self.assertEqual(self.env.user.has_group('account.group_show_line_subtotals_tax_included'),False)

    deftest_switch_taxB2B_taxB2C_multicompany(self):
        """
           Contrarilytothe(apparentlyreasonable)assumptionthataddingusers
           togroupandremovingthemwassymmetrical,itmaynotbethecase
           ifoneisdoneinSQLandtheotherviatheORM.
           Becausethelatterautomaticallytakesintoaccountrecordrulesthat
           mightmakesomeusersinvisible.

           Thisoneisidenticaltotheprevious,exceptthatwedotheactions
           withanon-superuseruser,andinanewcompanywithoneuserincommon
           withanothercompanywhichhasadifferenttaxB2Xsetting.
        """
        user=self.env.ref('base.user_admin')
        company=self.env['res.company'].create({'name':'oobO'})
        user.write({'company_ids':[(4,company.id)],'company_id':company.id})
        Settings=self.env['res.config.settings'].with_user(user.id)
        config=Settings.create({})

        self.switch_tax_settings(config)
