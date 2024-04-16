#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.addons.crm.tests.commonimportTestLeadConvertMassCommon
fromflectra.fieldsimportDatetime
fromflectra.tests.commonimporttagged,users


@tagged('lead_manage')
classTestLeadMerge(TestLeadConvertMassCommon):
    """Duringamixedmerge(involvingleadsandopps),datashouldbehandledacertainwayfollowingtheirtype
    (m2o,m2m,text,...)."""

    @classmethod
    defsetUpClass(cls):
        super(TestLeadMerge,cls).setUpClass()

        cls.leads=cls.lead_1+cls.lead_w_partner+cls.lead_w_contact+cls.lead_w_email+cls.lead_w_partner_company+cls.lead_w_email_lost
        #resetsomeassigneduserstotestsalesmenassign
        (cls.lead_w_partner|cls.lead_w_email_lost).write({
            'user_id':False,
        })
        cls.lead_w_partner.write({'stage_id':False})

        cls.lead_w_contact.write({'description':'lead_w_contact'})
        cls.lead_w_email.write({'description':'lead_w_email'})
        cls.lead_1.write({'description':'lead_1'})
        cls.lead_w_partner.write({'description':'lead_w_partner'})

        cls.assign_users=cls.user_sales_manager+cls.user_sales_leads_convert+cls.user_sales_salesman

    deftest_initial_data(self):
        """Ensureinitialdatatoavoidspaghettitestupdateafterwards"""
        self.assertFalse(self.lead_1.date_conversion)
        self.assertEqual(self.lead_1.date_open,Datetime.from_string('2020-01-1511:30:00'))
        self.assertEqual(self.lead_1.user_id,self.user_sales_leads)
        self.assertEqual(self.lead_1.team_id,self.sales_team_1)
        self.assertEqual(self.lead_1.stage_id,self.stage_team1_1)

        self.assertEqual(self.lead_w_partner.stage_id,self.env['crm.stage'])
        self.assertEqual(self.lead_w_partner.user_id,self.env['res.users'])
        self.assertEqual(self.lead_w_partner.team_id,self.sales_team_1)

        self.assertEqual(self.lead_w_partner_company.stage_id,self.stage_team1_1)
        self.assertEqual(self.lead_w_partner_company.user_id,self.user_sales_manager)
        self.assertEqual(self.lead_w_partner_company.team_id,self.sales_team_1)

        self.assertEqual(self.lead_w_contact.stage_id,self.stage_gen_1)
        self.assertEqual(self.lead_w_contact.user_id,self.user_sales_salesman)
        self.assertEqual(self.lead_w_contact.team_id,self.sales_team_convert)

        self.assertEqual(self.lead_w_email.stage_id,self.stage_gen_1)
        self.assertEqual(self.lead_w_email.user_id,self.user_sales_salesman)
        self.assertEqual(self.lead_w_email.team_id,self.sales_team_convert)

        self.assertEqual(self.lead_w_email_lost.stage_id,self.stage_team1_2)
        self.assertEqual(self.lead_w_email_lost.user_id,self.env['res.users'])
        self.assertEqual(self.lead_w_email_lost.team_id,self.sales_team_1)

    @users('user_sales_manager')
    deftest_lead_merge_internals(self):
        """Testinternalsofmergewizard.Inthistestleadsareorderedas

        lead_w_contact--lead---seq=30
        lead_w_email----lead---seq=3
        lead_1----------lead---seq=1
        lead_w_partner--lead---seq=False
        """
        #ensureinitialdata
        self.lead_w_partner_company.action_set_won() #wonoppsshouldbeexcluded

        merge=self.env['crm.merge.opportunity'].with_context({
            'active_model':'crm.lead',
            'active_ids':self.leads.ids,
            'active_id':False,
        }).create({
            'user_id':self.user_sales_leads_convert.id,
        })
        self.assertEqual(merge.team_id,self.sales_team_convert)

        #TDEFIXME:notsurethebrowseindefaultgetofwizardintendedtoexludelost,asitbrowseids
        #andexcludeinactiveleads,butthat'snotwrittenanywhere...intended??
        self.assertEqual(merge.opportunity_ids,self.leads-self.lead_w_partner_company-self.lead_w_email_lost)
        ordered_merge=self.lead_w_contact+self.lead_w_email+self.lead_1+self.lead_w_partner
        ordered_merge_description='\n\n'.join(l.descriptionforlinordered_merge)

        #mergedopportunity:inthistest,allinputareleads.Confidenceisbasedonstage
        #sequence->lead_w_contacthasastagesequenceof30
        result=merge.action_merge()
        merge_opportunity=self.env['crm.lead'].browse(result['res_id'])
        self.assertFalse((ordered_merge-merge_opportunity).exists())
        self.assertEqual(merge_opportunity,self.lead_w_contact)
        self.assertEqual(merge_opportunity.type,'lead')
        self.assertEqual(merge_opportunity.description,ordered_merge_description)
        #mergedopportunityhasupdatedsalesman/team/stageisokasgeneric
        self.assertEqual(merge_opportunity.user_id,self.user_sales_leads_convert)
        self.assertEqual(merge_opportunity.team_id,self.sales_team_convert)
        self.assertEqual(merge_opportunity.stage_id,self.stage_gen_1)

    @users('user_sales_manager')
    deftest_lead_merge_mixed(self):
        """Incaseofmix,opportunitiesareontop,andresultisanopportunity

        lead_1-------------------opp----seq=1
        lead_w_partner_company---opp----seq=1(IDgreater)
        lead_w_contact-----------lead---seq=30
        lead_w_email-------------lead---seq=3
        lead_w_partner-----------lead---seq=False
        """
        #ensureinitialdata
        (self.lead_w_partner_company|self.lead_1).write({'type':'opportunity'})
        self.assertEqual(self.lead_w_partner_company.stage_id.sequence,1)
        self.assertEqual(self.lead_1.stage_id.sequence,1)

        merge=self.env['crm.merge.opportunity'].with_context({
            'active_model':'crm.lead',
            'active_ids':self.leads.ids,
            'active_id':False,
        }).create({
            'team_id':self.sales_team_convert.id,
            'user_id':False,
        })
        #TDEFIXME:seeaa44700dccdc2618e0b8bc94252789264104047c->nouser,noteam->strange
        merge.write({'team_id':self.sales_team_convert.id})

        #TDEFIXME:notsurethebrowseindefaultgetofwizardintendedtoexludelost,asitbrowseids
        #andexcludeinactiveleads,butthat'snotwrittenanywhere...intended??
        self.assertEqual(merge.opportunity_ids,self.leads-self.lead_w_email_lost)
        ordered_merge=self.lead_w_partner_company+self.lead_w_contact+self.lead_w_email+self.lead_w_partner

        result=merge.action_merge()
        merge_opportunity=self.env['crm.lead'].browse(result['res_id'])
        self.assertFalse((ordered_merge-merge_opportunity).exists())
        self.assertEqual(merge_opportunity,self.lead_1)
        self.assertEqual(merge_opportunity.type,'opportunity')

        #mergedopportunityhassamesalesman(notupdatedinwizard)
        self.assertEqual(merge_opportunity.user_id,self.user_sales_leads)
        #TDEFIXME:assameuer_idisenforced,teamisupdatedthroughonchangeandthereforestage
        self.assertEqual(merge_opportunity.team_id,self.sales_team_convert)
        #self.assertEqual(merge_opportunity.team_id,self.sales_team_1)
        #TDEFIXME:BUTteam_idiscomputedaftercheckingstage,basedonwizard'steam_id
        self.assertEqual(merge_opportunity.stage_id,self.stage_team_convert_1)
