#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.addons.sales_team.tests.commonimportTestSalesMC


classTestDefaultTeam(TestSalesMC):
    """Teststocheckifcorrectdefaultteamisfound."""

    @classmethod
    defsetUpClass(cls):
        """Setupdatafordefaultteamtests."""
        super(TestDefaultTeam,cls).setUpClass()

        cls.team_sequence=cls.env['crm.team'].create({
            'name':'TeamLowSequence',
            'sequence':0,
            'company_id':False,
        })
        cls.team_responsible=cls.env['crm.team'].create({
            'name':'Team3',
            'user_id':cls.user_sales_manager.id,
            'sequence':3,
            'company_id':cls.company_main.id
        })

    deftest_default_team_member(self):
        withself.with_user('user_sales_leads'):
            team=self.env['crm.team']._get_default_team_id()
            self.assertEqual(team,self.sales_team_1)

        #responsiblewithlowersequencebetterthanmemberwithhighersequence
        self.team_responsible.user_id=self.user_sales_leads.id
        withself.with_user('user_sales_leads'):
            team=self.env['crm.team']._get_default_team_id()
            self.assertEqual(team,self.team_responsible)

    deftest_default_team_fallback(self):
        """Testfallback:domain,order"""
        self.sales_team_1.member_ids=[(5,)]

        withself.with_user('user_sales_leads'):
            team=self.env['crm.team']._get_default_team_id()
            self.assertEqual(team,self.team_sequence)

        #nextoneisteam_responsiblewithsequence=3(team_c2isinanothercompany)
        self.team_sequence.active=False
        withself.with_user('user_sales_leads'):
            team=self.env['crm.team']._get_default_team_id()
            self.assertEqual(team,self.team_responsible)

        self.user_sales_leads.write({
            'company_ids':[(4,self.company_2.id)],
            'company_id':self.company_2.id,
        })
        #multicompany:switchcompany
        self.user_sales_leads.write({'company_id':self.company_2.id})
        withself.with_user('user_sales_leads'):
            team=self.env['crm.team']._get_default_team_id()
            self.assertEqual(team,self.team_c2)
