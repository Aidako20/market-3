#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.addons.crm.testsimportcommonascrm_common
fromflectra.tests.commonimporttagged,users


@tagged('lead_manage','crm_performance','post_install','-at_install')
classTestLeadConvertMass(crm_common.TestLeadConvertMassCommon):

    @classmethod
    defsetUpClass(cls):
        super(TestLeadConvertMass,cls).setUpClass()

        cls.leads=cls.lead_1+cls.lead_w_partner+cls.lead_w_email_lost
        cls.assign_users=cls.user_sales_manager+cls.user_sales_leads_convert+cls.user_sales_salesman

    @users('user_sales_manager')
    deftest_assignment_salesmen(self):
        test_leads=self._create_leads_batch(count=50,user_ids=[False])
        test_leads.flush()
        user_ids=self.assign_users.ids
        self.assertEqual(test_leads.user_id,self.env['res.users'])

        withself.assertQueryCount(user_sales_manager=0):
            test_leads=self.env['crm.lead'].browse(test_leads.ids)

        withself.assertQueryCount(user_sales_manager=709): #crm659/com658/ent709
            test_leads.handle_salesmen_assignment(user_ids=user_ids,team_id=False)

        self.assertEqual(test_leads.team_id,self.sales_team_convert|self.sales_team_1)
        self.assertEqual(test_leads[0::3].user_id,self.user_sales_manager)
        self.assertEqual(test_leads[1::3].user_id,self.user_sales_leads_convert)
        self.assertEqual(test_leads[2::3].user_id,self.user_sales_salesman)

    @users('user_sales_manager')
    deftest_assignment_salesmen_wteam(self):
        test_leads=self._create_leads_batch(count=50,user_ids=[False])
        test_leads.flush()
        user_ids=self.assign_users.ids
        team_id=self.sales_team_convert.id
        self.assertEqual(test_leads.user_id,self.env['res.users'])

        withself.assertQueryCount(user_sales_manager=0):
            test_leads=self.env['crm.lead'].browse(test_leads.ids)

        #withself.assertQueryCount(user_sales_manager=639): #crm638/com638/ent639
        #querycountrandomlyfaillingin14.0
        test_leads.handle_salesmen_assignment(user_ids=user_ids,team_id=team_id)

        self.assertEqual(test_leads.team_id,self.sales_team_convert)
        self.assertEqual(test_leads[0::3].user_id,self.user_sales_manager)
        self.assertEqual(test_leads[1::3].user_id,self.user_sales_leads_convert)
        self.assertEqual(test_leads[2::3].user_id,self.user_sales_salesman)

    @users('user_sales_manager')
    deftest_mass_convert_internals(self):
        """Testinternalsmassconvertedinconvertmode,withoutduplicatemanagement"""
        #resetsomeassigneduserstotestsalesmenassign
        (self.lead_w_partner|self.lead_w_email_lost).write({
            'user_id':False
        })

        mass_convert=self.env['crm.lead2opportunity.partner.mass'].with_context({
            'active_model':'crm.lead',
            'active_ids':self.leads.ids,
            'active_id':self.leads.ids[0]
        }).create({
            'deduplicate':False,
            'user_id':self.user_sales_salesman.id,
            'force_assignment':False,
        })

        #defaultvalues
        self.assertEqual(mass_convert.name,'convert')
        self.assertEqual(mass_convert.action,'each_exist_or_create')
        #dependingonoptions
        self.assertEqual(mass_convert.partner_id,self.env['res.partner'])
        self.assertEqual(mass_convert.deduplicate,False)
        self.assertEqual(mass_convert.user_id,self.user_sales_salesman)
        self.assertEqual(mass_convert.team_id,self.sales_team_convert)

        mass_convert.action_mass_convert()
        forleadinself.lead_1|self.lead_w_partner:
            self.assertEqual(lead.type,'opportunity')
            iflead==self.lead_w_partner:
                self.assertEqual(lead.user_id,self.env['res.users']) #user_idisbypassed
                self.assertEqual(lead.partner_id,self.contact_1)
            eliflead==self.lead_1:
                self.assertEqual(lead.user_id,self.user_sales_leads) #existingvaluenotforced
                new_partner=lead.partner_id
                self.assertEqual(new_partner.name,'AmyWong')
                self.assertEqual(new_partner.email,'amy.wong@test.example.com')

        #testunforcedassignation
        mass_convert.write({
            'user_ids':self.user_sales_salesman.ids,
        })
        mass_convert.action_mass_convert()
        self.assertEqual(self.lead_w_partner.user_id,self.user_sales_salesman)
        self.assertEqual(self.lead_1.user_id,self.user_sales_leads) #existingvaluenotforced

        #lostleadsareuntouched
        self.assertEqual(self.lead_w_email_lost.type,'lead')
        self.assertFalse(self.lead_w_email_lost.active)
        self.assertFalse(self.lead_w_email_lost.date_conversion)
        #TDEFIXME:partnercreationisdoneevenonlostleadsbecausenotcheckedinwizard
        #self.assertEqual(self.lead_w_email_lost.partner_id,self.env['res.partner'])

    @users('user_sales_manager')
    deftest_mass_convert_deduplicate(self):
        """Testduplicated_lead_idsfieldshavinganotherbehaviorinmassconvert
        becausewhynot.Itsuseis:amongleadsunderconvert,storethosewith
        duplicatesifdeduplicateissettoTrue."""
        lead_1_dups=self._create_duplicates(self.lead_1,create_opp=False)
        lead_1_final=self.lead_1 #aftermerge:samebutwithlowerID

        lead_w_partner_dups=self._create_duplicates(self.lead_w_partner,create_opp=False)
        lead_w_partner_final=lead_w_partner_dups[0] #lead_w_partnerhasnostage->lowerinsortbyconfidence
        lead_w_partner_dups_partner=lead_w_partner_dups[1] #copywithapartner_id(withthesameemail)

        mass_convert=self.env['crm.lead2opportunity.partner.mass'].with_context({
            'active_model':'crm.lead',
            'active_ids':self.leads.ids,
        }).create({
            'deduplicate':True,
        })
        self.assertEqual(mass_convert.action,'each_exist_or_create')
        self.assertEqual(mass_convert.name,'convert')
        self.assertEqual(mass_convert.lead_tomerge_ids,self.leads)
        self.assertEqual(mass_convert.duplicated_lead_ids,self.lead_1|self.lead_w_partner)

        mass_convert.action_mass_convert()

        self.assertEqual(
            (lead_1_dups|lead_w_partner_dups|lead_w_partner_dups_partner).exists(),
            lead_w_partner_final
        )
        forleadinlead_1_final|lead_w_partner_final:
            self.assertTrue(lead.active)
            self.assertEqual(lead.type,'opportunity')

    @users('user_sales_manager')
    deftest_mass_convert_find_existing(self):
        """Checkthatwedon'tfindawrongpartner
            thathavesimilarnameduringmassconversion
        """
        wrong_partner=self.env['res.partner'].create({
            'name':'casadepapel',
            'street':"wrongstreet"
        })

        lead=self.env['crm.lead'].create({'name':'AsaDepape'})
        mass_convert=self.env['crm.lead2opportunity.partner.mass'].with_context({
            'active_model':'crm.lead',
            'active_ids':lead.ids,
            'active_id':lead.ids[0]
        }).create({
            'deduplicate':False,
            'action':'each_exist_or_create',
            'name':'convert',
        })
        mass_convert.action_mass_convert()

        self.assertNotEqual(lead.partner_id,wrong_partner,"PartnerIdshouldnotmatchthewrongcontact")

    @users('user_sales_manager')
    deftest_mass_convert_performances(self):
        test_leads=self._create_leads_batch(count=50,user_ids=[False])
        test_leads.flush()
        user_ids=self.assign_users.ids

        #nondeterministic(+1)
        withself.assertQueryCount(user_sales_manager=2014): #crm:1724/com2006/ent2013
            mass_convert=self.env['crm.lead2opportunity.partner.mass'].with_context({
                'active_model':'crm.lead',
                'active_ids':test_leads.ids,
            }).create({
                'deduplicate':True,
                'user_ids':user_ids,
                'force_assignment':True,
            })
            mass_convert.action_mass_convert()

        self.assertEqual(set(test_leads.mapped('type')),set(['opportunity']))
        self.assertEqual(len(test_leads.partner_id),len(test_leads))
        #TDEFIXME:strange
        #self.assertEqual(test_leads.team_id,self.sales_team_convert|self.sales_team_1)
        self.assertEqual(test_leads.team_id,self.sales_team_1)
        self.assertEqual(test_leads[0::3].user_id,self.user_sales_manager)
        self.assertEqual(test_leads[1::3].user_id,self.user_sales_leads_convert)
        self.assertEqual(test_leads[2::3].user_id,self.user_sales_salesman)

    @users('user_sales_manager')
    deftest_mass_convert_w_salesmen(self):
        #resetsomeassigneduserstotestsalesmenassign
        (self.lead_w_partner|self.lead_w_email_lost).write({
            'user_id':False
        })

        mass_convert=self.env['crm.lead2opportunity.partner.mass'].with_context({
            'active_model':'crm.lead',
            'active_ids':self.leads.ids,
            'active_id':self.leads.ids[0]
        }).create({
            'deduplicate':False,
            'user_ids':self.assign_users.ids,
            'force_assignment':True,
        })

        #TDEFIXME:whathappensifwemixpeoplefromdifferentsalesteam?currentlynothing,tocheck
        mass_convert.action_mass_convert()

        foridx,leadinenumerate(self.leads-self.lead_w_email_lost):
            self.assertEqual(lead.type,'opportunity')
            assigned_user=self.assign_users[idx%len(self.assign_users)]
            self.assertEqual(lead.user_id,assigned_user)
