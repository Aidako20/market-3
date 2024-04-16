#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportSUPERUSER_ID
fromflectra.addons.crm.testsimportcommonascrm_common
fromflectra.fieldsimportDatetime
fromflectra.tests.commonimporttagged,users
fromflectra.tests.commonimportForm

@tagged('lead_manage')
classTestLeadConvertForm(crm_common.TestLeadConvertCommon):

    @users('user_sales_manager')
    deftest_form_action_default(self):
        """TestLead._find_matching_partner()"""
        lead=self.env['crm.lead'].browse(self.lead_1.ids)
        customer=self.env['res.partner'].create({
            "name":"AmyWong",
            "email":'"Amy,PhDStudent,Wong"Tiny<AMY.WONG@test.example.com>'
        })

        wizard=Form(self.env['crm.lead2opportunity.partner'].with_context({
            'active_model':'crm.lead',
            'active_id':lead.id,
            'active_ids':lead.ids,
        }))

        self.assertEqual(wizard.name,'convert')
        self.assertEqual(wizard.action,'exist')
        self.assertEqual(wizard.partner_id,customer)

    @users('user_sales_manager')
    deftest_form_name_onchange(self):
        """TestLead._find_matching_partner()"""
        lead=self.env['crm.lead'].browse(self.lead_1.ids)
        lead_dup=lead.copy({'name':'Duplicate'})
        customer=self.env['res.partner'].create({
            "name":"AmyWong",
            "email":'"Amy,PhDStudent,Wong"Tiny<AMY.WONG@test.example.com>'
        })

        wizard=Form(self.env['crm.lead2opportunity.partner'].with_context({
            'active_model':'crm.lead',
            'active_id':lead.id,
            'active_ids':lead.ids,
        }))

        self.assertEqual(wizard.name,'merge')
        self.assertEqual(wizard.action,'exist')
        self.assertEqual(wizard.partner_id,customer)
        self.assertEqual(wizard.duplicated_lead_ids[:],lead+lead_dup)

        wizard.name='convert'
        wizard.action='create'
        self.assertEqual(wizard.action,'create','Shouldkeepuserinput')
        self.assertEqual(wizard.name,'convert','Shouldkeepuserinput')


@tagged('lead_manage')
classTestLeadConvert(crm_common.TestLeadConvertCommon):
    """
    TODO:createdpartner(handleassignation)hasteamoflead
    TODO:createpartnerhasuser_id comingfromwizard
    """

    @classmethod
    defsetUpClass(cls):
        super(TestLeadConvert,cls).setUpClass()
        date=Datetime.from_string('2020-01-2016:00:00')
        cls.crm_lead_dt_mock.now.return_value=date

    deftest_initial_data(self):
        """Ensureinitialdatatoavoidspaghettitestupdateafterwards"""
        self.assertFalse(self.lead_1.date_conversion)
        self.assertEqual(self.lead_1.date_open,Datetime.from_string('2020-01-1511:30:00'))
        self.assertEqual(self.lead_1.user_id,self.user_sales_leads)
        self.assertEqual(self.lead_1.team_id,self.sales_team_1)
        self.assertEqual(self.lead_1.stage_id,self.stage_team1_1)

    @users('user_sales_manager')
    deftest_lead_convert_base(self):
        """Testbasemethod``convert_opportunity``orcrm.leadmodel"""
        self.contact_2.phone=False #forceFalsytocomparewithmobile
        self.assertFalse(self.contact_2.phone)
        lead=self.lead_1.with_user(self.env.user)
        lead.write({
            'phone':'123456789',
        })
        self.assertEqual(lead.team_id,self.sales_team_1)
        self.assertEqual(lead.stage_id,self.stage_team1_1)
        self.assertEqual(lead.email_from,'amy.wong@test.example.com')
        lead.convert_opportunity(self.contact_2.id)

        self.assertEqual(lead.type,'opportunity')
        self.assertEqual(lead.partner_id,self.contact_2)
        self.assertEqual(lead.email_from,self.contact_2.email)
        self.assertEqual(lead.mobile,self.contact_2.mobile)
        self.assertEqual(lead.phone,'123456789')
        self.assertEqual(lead.team_id,self.sales_team_1)
        self.assertEqual(lead.stage_id,self.stage_team1_1)

    @users('user_sales_manager')
    deftest_lead_convert_base_corner_cases(self):
        """Testbasemethod``convert_opportunity``orcrm.leadmodelwithcorner
        cases:inactive,won,stageupdate,..."""
        #inactiveleadsarenotconverted
        lead=self.lead_1.with_user(self.env.user)
        lead.action_archive()
        self.assertFalse(lead.active)
        lead.convert_opportunity(self.contact_2.id)

        self.assertEqual(lead.type,'lead')
        self.assertEqual(lead.partner_id,self.env['res.partner'])

        lead.action_unarchive()
        self.assertTrue(lead.active)

        #wonleadsarenotconverted
        lead.action_set_won()
        #TDEFIXME:setwondoesnottakeintoaccountsalesteamwhenfetchingawonstage
        #self.assertEqual(lead.stage_id,self.stage_team1_won)
        self.assertEqual(lead.stage_id,self.stage_gen_won)
        self.assertEqual(lead.probability,100)

        lead.convert_opportunity(self.contact_2.id)
        self.assertEqual(lead.type,'lead')
        self.assertEqual(lead.partner_id,self.env['res.partner'])

    @users('user_sales_manager')
    deftest_lead_convert_base_w_salesmen(self):
        """Testbasemethod``convert_opportunity``whileforcingsalesmen,asit
        shouldalsoforcesalesteam"""
        lead=self.lead_1.with_user(self.env.user)
        self.assertEqual(lead.team_id,self.sales_team_1)
        lead.convert_opportunity(False,user_ids=self.user_sales_salesman.ids)
        self.assertEqual(lead.user_id,self.user_sales_salesman)
        self.assertEqual(lead.team_id,self.sales_team_convert)
        #TDEFIXME:convertdoesnotrecomputestagebasedonupdatedteamofassigneduser
        #self.assertEqual(lead.stage_id,self.stage_team_convert_1)

    @users('user_sales_manager')
    deftest_lead_convert_base_w_team(self):
        """Testbasemethod``convert_opportunity``whileforcingteam"""
        lead=self.lead_1.with_user(self.env.user)
        lead.convert_opportunity(False,team_id=self.sales_team_convert.id)
        self.assertEqual(lead.team_id,self.sales_team_convert)
        self.assertEqual(lead.user_id,self.user_sales_leads)
        #TDEFIXME:convertdoesnotrecomputestagebasedonteam
        #self.assertEqual(lead.stage_id,self.stage_team_convert_1)

    @users('user_sales_manager')
    deftest_lead_convert_corner_cases_crud(self):
        """TestLead._find_matching_partner()"""
        #emailformatting
        other_lead=self.lead_1.copy()
        other_lead.write({'partner_id':self.contact_1.id})

        convert=self.env['crm.lead2opportunity.partner'].with_context({
            'default_lead_id':other_lead.id,
        }).create({})
        self.assertEqual(convert.lead_id,other_lead)
        self.assertEqual(convert.partner_id,self.contact_1)
        self.assertEqual(convert.action,'exist')

        convert=self.env['crm.lead2opportunity.partner'].with_context({
            'default_lead_id':other_lead.id,
            'active_model':'crm.lead',
            'active_id':self.lead_1.id,
        }).create({})
        self.assertEqual(convert.lead_id,other_lead)
        self.assertEqual(convert.partner_id,self.contact_1)
        self.assertEqual(convert.action,'exist')

    @users('user_sales_manager')
    deftest_lead_convert_corner_cases_matching(self):
        """TestLead._find_matching_partner()"""
        #emailformatting
        self.lead_1.write({
            'email_from':'AmyWong<amy.wong@test.example.com>'
        })
        customer=self.env['res.partner'].create({
            'name':'DifferentName',
            'email':'WongAMY<AMY.WONG@test.example.com>'
        })

        convert=self.env['crm.lead2opportunity.partner'].with_context({
            'active_model':'crm.lead',
            'active_id':self.lead_1.id,
            'active_ids':self.lead_1.ids,
        }).create({})
        #TDEFIXME:shouldtakeintoaccountnormalizedemailversion,notencodedone
        #self.assertEqual(convert.partner_id,customer)

    @users('user_sales_manager')
    deftest_lead_convert_internals(self):
        """Testinternalsofconvertwizard"""
        convert=self.env['crm.lead2opportunity.partner'].with_context({
            'active_model':'crm.lead',
            'active_id':self.lead_1.id,
            'active_ids':self.lead_1.ids,
        }).create({})

        #testinternalsofconvertwizard
        self.assertEqual(convert.lead_id,self.lead_1)
        self.assertEqual(convert.user_id,self.lead_1.user_id)
        self.assertEqual(convert.team_id,self.lead_1.team_id)
        self.assertFalse(convert.partner_id)
        self.assertEqual(convert.name,'convert')
        self.assertEqual(convert.action,'create')

        convert.write({'user_id':self.user_sales_salesman.id})
        self.assertEqual(convert.user_id,self.user_sales_salesman)
        self.assertEqual(convert.team_id,self.sales_team_convert)

        convert.action_apply()
        #converttest
        self.assertEqual(self.lead_1.type,'opportunity')
        self.assertEqual(self.lead_1.user_id,self.user_sales_salesman)
        self.assertEqual(self.lead_1.team_id,self.sales_team_convert)
        #TDEFIXME:stageislinkedtotheoldsalesteamandisnotupdatedwhenconverting,couldbeimproved
        #self.assertEqual(self.lead_1.stage_id,self.stage_gen_1)
        #partnercreationtest
        new_partner=self.lead_1.partner_id
        self.assertEqual(new_partner.name,'AmyWong')
        self.assertEqual(new_partner.email,'amy.wong@test.example.com')

    @users('user_sales_manager')
    deftest_lead_convert_action_exist(self):
        """Testspecificusecaseof'exist'actioninconverwizard"""
        self.lead_1.write({'partner_id':self.contact_1.id})

        convert=self.env['crm.lead2opportunity.partner'].with_context({
            'active_model':'crm.lead',
            'active_id':self.lead_1.id,
            'active_ids':self.lead_1.ids,
        }).create({})
        self.assertEqual(convert.action,'exist')
        convert.action_apply()
        self.assertEqual(self.lead_1.type,'opportunity')
        self.assertEqual(self.lead_1.partner_id,self.contact_1)

    @users('user_sales_manager')
    deftest_lead_convert_action_nothing(self):
        """Testspecificusecaseof'nothing'actioninconverwizard"""
        self.lead_1.write({'contact_name':False})

        convert=self.env['crm.lead2opportunity.partner'].with_context({
            'active_model':'crm.lead',
            'active_id':self.lead_1.id,
            'active_ids':self.lead_1.ids,
        }).create({})
        self.assertEqual(convert.action,'nothing')
        convert.action_apply()
        self.assertEqual(self.lead_1.type,'opportunity')
        self.assertEqual(self.lead_1.user_id,self.user_sales_leads)
        self.assertEqual(self.lead_1.team_id,self.sales_team_1)
        self.assertEqual(self.lead_1.stage_id,self.stage_team1_1)
        self.assertEqual(self.lead_1.partner_id,self.env['res.partner'])

    @users('user_sales_manager')
    deftest_lead_convert_contact_mutlicompany(self):
        """Checkthewizardconverttooppdon'tfindcontact
        Youarenotabletoseebecausetheybelongtoanothercompany"""
        #Usesuperuser_idbecausecreatingacompanywithauseradddirectly
        #thecompanyincompany_idsoftheuser.
        company_2=self.env['res.company'].with_user(SUPERUSER_ID).create({'name':'Company2'})
        partner_company_2=self.env['res.partner'].with_user(SUPERUSER_ID).create({
            'name':'Contactinothercompany',
            'email':'test@company2.com',
            'company_id':company_2.id,
        })
        lead=self.env['crm.lead'].create({
            'name':'LEAD',
            'type':'lead',
            'email_from':'test@company2.com',
        })
        convert=self.env['crm.lead2opportunity.partner'].with_context({
            'active_model':'crm.lead',
            'active_id':lead.id,
            'active_ids':lead.ids,
        }).create({'name':'convert','action':'exist'})
        self.assertNotEqual(convert.partner_id,partner_company_2,
            "Conversionwizardshouldnotbeabletofindthepartnerfromanothercompany")

    @users('user_sales_manager')
    deftest_lead_convert_same_partner(self):
        """Checkthatwedon'teraseleadinformation
        withexistingpartnerinfoifthepartnerisalreadyset
        """
        partner=self.env['res.partner'].create({
            'name':'Emptypartner',
        })
        lead=self.env['crm.lead'].create({
            'name':'LEAD',
            'partner_id':partner.id,
            'type':'lead',
            'email_from':'demo@test.com',
            'street':'mystreet',
            'city':'mycity',
        })
        lead.convert_opportunity(partner.id)
        self.assertEqual(lead.email_from,'demo@test.com','EmailFromshouldbepreservedduringconversion')
        self.assertEqual(lead.street,'mystreet','Streetshouldbepreservedduringconversion')
        self.assertEqual(lead.city,'mycity','Cityshouldbepreservedduringconversion')

    @users('user_sales_manager')
    deftest_lead_merge(self):
        """Testconvertwizardworkinginmergemode"""
        date=Datetime.from_string('2020-01-2016:00:00')
        self.crm_lead_dt_mock.now.return_value=date

        leads=self.env['crm.lead']
        forxinrange(2):
            leads|=self.env['crm.lead'].create({
                'name':'Dup-%02d-%s'%(x+1,self.lead_1.name),
                'type':'lead','user_id':False,'team_id':self.lead_1.team_id.id,
                'contact_name':'Duplicate%02dof%s'%(x+1,self.lead_1.contact_name),
                'email_from':self.lead_1.email_from,
            })

        convert=self.env['crm.lead2opportunity.partner'].with_context({
            'active_model':'crm.lead',
            'active_id':self.lead_1.id,
            'active_ids':self.lead_1.ids,
        }).create({})

        #testinternalsofconvertwizard
        self.assertEqual(convert.duplicated_lead_ids,self.lead_1|leads)
        self.assertEqual(convert.user_id,self.lead_1.user_id)
        self.assertEqual(convert.team_id,self.lead_1.team_id)
        self.assertFalse(convert.partner_id)
        self.assertEqual(convert.name,'merge')
        self.assertEqual(convert.action,'create')

        convert.write({'user_id':self.user_sales_salesman.id})
        self.assertEqual(convert.user_id,self.user_sales_salesman)
        self.assertEqual(convert.team_id,self.sales_team_convert)

        convert.action_apply()
        self.assertEqual(self.lead_1.type,'opportunity')

    @users('user_sales_manager')
    deftest_lead_merge_duplicates(self):
        """TestLead._get_lead_duplicates()"""

        #Check:partner/emailfallbacks
        self._create_duplicates(self.lead_1)
        self.lead_1.write({
            'partner_id':self.customer.id,
        })
        convert=self.env['crm.lead2opportunity.partner'].with_context({
            'active_model':'crm.lead',
            'active_id':self.lead_1.id,
            'active_ids':self.lead_1.ids,
        }).create({})
        self.assertEqual(convert.partner_id,self.customer)
        #self.assertEqual(convert.duplicated_lead_ids,self.lead_1|self.lead_email_from|self.lead_email_normalized|self.lead_partner|self.opp_lost)
        self.assertEqual(convert.duplicated_lead_ids,self.lead_1|self.lead_email_from|self.lead_partner|self.opp_lost)

        #Check:partnerfallbacks
        self.lead_1.write({
            'email_from':False,
            'partner_id':self.customer.id,
        })
        self.customer.write({'email':False})
        convert=self.env['crm.lead2opportunity.partner'].with_context({
            'active_model':'crm.lead',
            'active_id':self.lead_1.id,
            'active_ids':self.lead_1.ids,
        }).create({})
        self.assertEqual(convert.partner_id,self.customer)
        self.assertEqual(convert.duplicated_lead_ids,self.lead_1|self.lead_partner)

    @users('user_sales_manager')
    deftest_lead_merge_duplicates_flow(self):
        """TestLead._get_lead_duplicates()+mergewithactive_test"""

        #Check:emailformatting
        self.lead_1.write({
            'email_from':'AmyWong<amy.wong@test.example.com>'
        })
        self._create_duplicates(self.lead_1)

        convert=self.env['crm.lead2opportunity.partner'].with_context({
            'active_model':'crm.lead',
            'active_id':self.lead_1.id,
            'active_ids':self.lead_1.ids,
        }).create({})
        self.assertEqual(convert.partner_id,self.customer)
        #TDEFIXME:shouldcheckforemail_normalized->lead_email_normalizednotcorrectlyfound
        #self.assertEqual(convert.duplicated_lead_ids,self.lead_1|lead_email_from|lead_email_normalized|lead_partner|opp_lost)
        self.assertEqual(convert.duplicated_lead_ids,self.lead_1|self.lead_email_from|self.lead_partner|self.opp_lost)

        convert.action_apply()
        self.assertEqual(
            #(self.lead_1|self.lead_email_from|self.lead_email_normalized|self.lead_partner|self.opp_lost).exists(),
            (self.lead_1|self.lead_email_from|self.lead_partner|self.opp_lost).exists(),
            self.opp_lost)


@tagged('lead_manage')
classTestLeadConvertBatch(crm_common.TestLeadConvertMassCommon):

    deftest_initial_data(self):
        """Ensureinitialdatatoavoidspaghettitestupdateafterwards"""
        self.assertFalse(self.lead_1.date_conversion)
        self.assertEqual(self.lead_1.date_open,Datetime.from_string('2020-01-1511:30:00'))
        self.assertEqual(self.lead_1.user_id,self.user_sales_leads)
        self.assertEqual(self.lead_1.team_id,self.sales_team_1)
        self.assertEqual(self.lead_1.stage_id,self.stage_team1_1)

        self.assertEqual(self.lead_w_partner.stage_id,self.env['crm.stage'])
        self.assertEqual(self.lead_w_partner.user_id,self.user_sales_manager)
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
        self.assertEqual(self.lead_w_email_lost.user_id,self.user_sales_leads)
        self.assertEqual(self.lead_w_email_lost.team_id,self.sales_team_1)

    @users('user_sales_manager')
    deftest_lead_convert_batch_internals(self):
        """Testinternalsofconvertwizard,workinginbatchmode"""
        date=Datetime.from_string('2020-01-2016:00:00')
        self.crm_lead_dt_mock.now.return_value=date

        lead_w_partner=self.lead_w_partner
        lead_w_contact=self.lead_w_contact
        lead_w_email_lost=self.lead_w_email_lost
        lead_w_email_lost.action_set_lost()
        self.assertEqual(lead_w_email_lost.active,False)

        convert=self.env['crm.lead2opportunity.partner'].with_context({
            'active_model':'crm.lead',
            'active_id':self.lead_1.id,
            'active_ids':(self.lead_1|lead_w_partner|lead_w_contact|lead_w_email_lost).ids,
        }).create({})

        #testinternalsofconvertwizard
        #self.assertEqual(convert.lead_id,self.lead_1)
        self.assertEqual(convert.user_id,self.lead_1.user_id)
        self.assertEqual(convert.team_id,self.lead_1.team_id)
        self.assertFalse(convert.partner_id)
        self.assertEqual(convert.name,'convert')
        self.assertEqual(convert.action,'create')

        convert.action_apply()
        self.assertEqual(convert.user_id,self.user_sales_leads)
        self.assertEqual(convert.team_id,self.sales_team_1)
        #lostleadsarenotconverted(seecrm_lead.convert_opportunity())
        self.assertFalse(lead_w_email_lost.active)
        self.assertFalse(lead_w_email_lost.date_conversion)
        self.assertEqual(lead_w_email_lost.partner_id,self.env['res.partner'])
        self.assertEqual(lead_w_email_lost.stage_id,self.stage_team1_2) #didnotchange
        #otherleadsareconvertedintoopportunities
        foroppin(self.lead_1|lead_w_partner|lead_w_contact):
            #teammanagementupdate:opportunitylinkedtochosenwizardvalues
            self.assertEqual(opp.type,'opportunity')
            self.assertTrue(opp.active)
            self.assertEqual(opp.user_id,convert.user_id)
            self.assertEqual(opp.team_id,convert.team_id)
            #datesupdate:convertsetthemtonow
            self.assertEqual(opp.date_open,date)
            self.assertEqual(opp.date_conversion,date)
            #stageupdate(dependsonpreviousvalue)
            ifopp==self.lead_1:
                self.assertEqual(opp.stage_id,self.stage_team1_1) #didnotchange
            elifopp==lead_w_partner:
                self.assertEqual(opp.stage_id,self.stage_team1_1) #issettodefaultstageofsales_team_1
            elifopp==lead_w_contact:
                self.assertEqual(opp.stage_id,self.stage_gen_1) #didnotchange
            else:
                self.assertFalse(True)
