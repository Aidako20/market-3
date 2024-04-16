#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromunittest.mockimportpatch

fromflectra.addons.mail.tests.commonimportMailCase,mail_new_test_user
fromflectra.addons.sales_team.tests.commonimportTestSalesCommon
fromflectra.fieldsimportDatetime
fromflectraimporttools

INCOMING_EMAIL="""Return-Path:{return_path}
X-Original-To:{to}
Delivered-To:{to}
Received:bymail.my.com(Postfix,fromuseridxxx)
    id822ECBFB67;Mon,24Oct201107:36:51+0200(CEST)
X-Spam-Checker-Version:SpamAssassin3.3.1(2010-03-16)onmail.my.com
X-Spam-Level:
X-Spam-Status:No,score=-1.0required=5.0tests=ALL_TRUSTEDautolearn=ham
    version=3.3.1
Received:from[192.168.1.146]
    (Authenticatedsender:{email_from})
    bymail.customer.com(Postfix)withESMTPSAid07A30BFAB4
    for<{to}>;Mon,24Oct201107:36:50+0200(CEST)
Message-ID:{msg_id}
Date:Mon,24Oct201111:06:29+0530
From:{email_from}
User-Agent:Mozilla/5.0(X11;U;Linuxi686;en-US;rv:1.9.2.14)Gecko/20110223Lightning/1.0b2Thunderbird/3.1.8
MIME-Version:1.0
To:{to}
Subject:{subject}
Content-Type:text/plain;charset=ISO-8859-1;format=flowed
Content-Transfer-Encoding:8bit

Thisisanexampleemail.Allsensitivecontenthasbeenstrippedout.

ALLGLORYTOTHEHYPNOTOAD!

Cheers,

Somebody."""


classTestCrmCommon(TestSalesCommon,MailCase):

    @classmethod
    defsetUpClass(cls):
        super(TestCrmCommon,cls).setUpClass()
        cls._init_mail_gateway()

        cls.sales_team_1.write({
            'alias_name':'sales.test',
            'use_leads':True,
            'use_opportunities':True,
        })

        (cls.user_sales_manager|cls.user_sales_leads|cls.user_sales_salesman).write({
            'groups_id':[(4,cls.env.ref('crm.group_use_lead').id)]
        })

        cls.env['crm.stage'].search([]).write({'sequence':9999}) #ensuresearchwillfindtestdatafirst
        cls.stage_team1_1=cls.env['crm.stage'].create({
            'name':'New',
            'sequence':1,
            'team_id':cls.sales_team_1.id,
        })
        cls.stage_team1_2=cls.env['crm.stage'].create({
            'name':'Proposition',
            'sequence':5,
            'team_id':cls.sales_team_1.id,
        })
        cls.stage_team1_won=cls.env['crm.stage'].create({
            'name':'Won',
            'sequence':70,
            'team_id':cls.sales_team_1.id,
            'is_won':True,
        })
        cls.stage_gen_1=cls.env['crm.stage'].create({
            'name':'Genericstage',
            'sequence':3,
            'team_id':False,
        })
        cls.stage_gen_won=cls.env['crm.stage'].create({
            'name':'GenericWon',
            'sequence':30,
            'team_id':False,
            'is_won':True,
        })

        #countriesandlangs
        cls.lang_en=cls.env['res.lang']._lang_get('en_US')

        #leads
        cls.lead_1=cls.env['crm.lead'].create({
            'name':'NibblerSpacecraftRequest',
            'type':'lead',
            'user_id':cls.user_sales_leads.id,
            'team_id':cls.sales_team_1.id,
            'partner_id':False,
            'contact_name':'AmyWong',
            'email_from':'amy.wong@test.example.com',
            'country_id':cls.env.ref('base.us').id,
        })
        #updatelead_1:stage_idisnotcomputedanymorebydefaultforleads
        cls.lead_1.write({
            'stage_id':cls.stage_team1_1.id,
        })

        #createanhistoryfornewteam
        cls.lead_team_1_won=cls.env['crm.lead'].create({
            'name':'AlreadyWon',
            'type':'lead',
            'user_id':cls.user_sales_leads.id,
            'team_id':cls.sales_team_1.id,
        })
        cls.lead_team_1_won.action_set_won()
        cls.lead_team_1_lost=cls.env['crm.lead'].create({
            'name':'AlreadyWon',
            'type':'lead',
            'user_id':cls.user_sales_leads.id,
            'team_id':cls.sales_team_1.id,
        })
        cls.lead_team_1_lost.action_set_lost()
        (cls.lead_team_1_won|cls.lead_team_1_lost).flush()

        #email/phonedata
        cls.test_email_data=[
            '"PlanetExpress"<planet.express@test.example.com>',
            '"Philip,J.Fry"<philip.j.fry@test.example.com>',
            '"TurangaLeela"<turanga.leela@test.example.com>',
        ]
        cls.test_email_data_normalized=[
            'planet.express@test.example.com',
            'philip.j.fry@test.example.com',
            'turanga.leela@test.example.com',
        ]
        cls.test_phone_data=[
            '+12025550122', #formattedUSnumber
            '2025550999', #localUSnumber
            '2025550888', #localUSnumber
        ]
        cls.test_phone_data_sanitized=[
            '+12025550122',
            '+12025550999',
            '+12025550888',
        ]

        #createsometestcontactandcompanies
        cls.contact_company_1=cls.env['res.partner'].create({
            'name':'PlanetExpress',
            'email':cls.test_email_data[0],
            'is_company':True,
            'street':'57thStreet',
            'city':'NewNewYork',
            'country_id':cls.env.ref('base.us').id,
            'zip':'12345',
        })
        cls.contact_1=cls.env['res.partner'].create({
            'name':'PhilipJFry',
            'email':cls.test_email_data[1],
            'mobile':cls.test_phone_data[0],
            'title':cls.env.ref('base.res_partner_title_mister').id,
            'function':'DeliveryBoy',
            'phone':False,
            'parent_id':cls.contact_company_1.id,
            'is_company':False,
            'street':'Actuallythesewers',
            'city':'NewYork',
            'country_id':cls.env.ref('base.us').id,
            'zip':'54321',
        })
        cls.contact_2=cls.env['res.partner'].create({
            'name':'TurangaLeela',
            'email':cls.test_email_data[2],
            'mobile':cls.test_phone_data[1],
            'phone':cls.test_phone_data[2],
            'parent_id':False,
            'is_company':False,
            'street':'CookievilleMinimum-SecurityOrphanarium',
            'city':'NewNewYork',
            'country_id':cls.env.ref('base.us').id,
            'zip':'97648',
        })

    def_create_leads_batch(self,lead_type='lead',count=10,partner_ids=None,user_ids=None):
        """Helpertoolmethodcreatingabatchofleads,usefulwhendealing
        withbatchprocesses.Pleaseupdateme.

        :paramstringtype:'lead','opportunity','mixed'(leadthenopp),
          None(dependsonconfiguration);
        """
        types=['lead','opportunity']
        leads_data=[{
            'name':'TestLead_%02d'%(x),
            'type':lead_typeiflead_typeelsetypes[x%2],
            'priority':'%s'%(x%3),
        }forxinrange(count)]

        #customerinformation
        ifpartner_ids:
            foridx,lead_datainenumerate(leads_data):
                lead_data['partner_id']=partner_ids[idx%len(partner_ids)]
        else:
            foridx,lead_datainenumerate(leads_data):
                lead_data['email_from']=tools.formataddr((
                    'TestCustomer_%02d'%(idx),
                    'customer_email_%02d@example.com'%(idx)
                ))

        #salesteaminformation
        ifuser_ids:
            foridx,lead_datainenumerate(leads_data):
                lead_data['user_id']=user_ids[idx%len(user_ids)]

        returnself.env['crm.lead'].create(leads_data)

    def_create_duplicates(self,lead,create_opp=True):
        """Helpertoolmethodcreating,basedonagivenlead

          *acustomer(res.partner)basedonleademail(totestpartnerfinding)
            ->FIXME:usingsamenormalizedemaildoesnotworkcurrently,onlyexactemailworks
          *aleadwithsameemail_from
          *aleadwithsameemail_normalized(otheremail_from)
          *aleadwithcustomerbutanotheremail
          *alostopportunitywithsameemail_from
        """
        self.customer=self.env['res.partner'].create({
            'name':'Lead1EmailCustomer',
            'email':lead.email_from,
        })
        self.lead_email_from=self.env['crm.lead'].create({
            'name':'Duplicate:sameemail_from',
            'type':'lead',
            'team_id':lead.team_id.id,
            'email_from':lead.email_from,
        })
        #self.lead_email_normalized=self.env['crm.lead'].create({
        #    'name':'Duplicate:email_normalizecomparison',
        #    'type':'lead',
        #    'team_id':lead.team_id.id,
        #    'stage_id':lead.stage_id.id,
        #    'email_from':'CUSTOMERWITHNAME<%s>'%lead.email_normalized.upper(),
        #})
        self.lead_partner=self.env['crm.lead'].create({
            'name':'Duplicate:customerID',
            'type':'lead',
            'team_id':lead.team_id.id,
            'partner_id':self.customer.id,
        })
        ifcreate_opp:
            self.opp_lost=self.env['crm.lead'].create({
                'name':'Duplicate:lostopportunity',
                'type':'opportunity',
                'team_id':lead.team_id.id,
                'stage_id':lead.stage_id.id,
                'email_from':lead.email_from,
            })
            self.opp_lost.action_set_lost()
        else:
            self.opp_lost=self.env['crm.lead']

        #self.assertEqual(self.lead_email_from.email_normalized,self.lead_email_normalized.email_normalized)
        #self.assertTrue(lead.email_from!=self.lead_email_normalized.email_from)
        #self.assertFalse(self.opp_lost.active)

        #new_lead=self.lead_email_from|self.lead_email_normalized|self.lead_partner|self.opp_lost
        new_leads=self.lead_email_from|self.lead_partner|self.opp_lost
        new_leads.flush() #computenotablyprobability
        returnnew_leads


classTestLeadConvertCommon(TestCrmCommon):

    @classmethod
    defsetUpClass(cls):
        super(TestLeadConvertCommon,cls).setUpClass()
        #SalesTeamorganization
        #Role:M(teammember)R(teammanager)
        #SALESMAN---------------sales_team_1-----sales_team_convert
        #admin------------------M----------------/
        #user_sales_manager-----R----------------R
        #user_sales_leads-------M----------------/
        #user_sales_salesman----/----------------M

        #StagesTeamorganization
        #Name-------------------ST-------------------Sequ
        #stage_team1_1----------sales_team_1---------1
        #stage_team1_2----------sales_team_1---------5
        #stage_team1_won--------sales_team_1---------70
        #stage_gen_1------------/--------------------3
        #stage_gen_won----------/--------------------30
        #stage_team_convert_1---sales_team_convert---1

        cls.sales_team_convert=cls.env['crm.team'].create({
            'name':'ConvertSalesTeam',
            'sequence':10,
            'alias_name':False,
            'use_leads':True,
            'use_opportunities':True,
            'company_id':False,
            'user_id':cls.user_sales_manager.id,
            'member_ids':[(4,cls.user_sales_salesman.id)],
        })
        cls.stage_team_convert_1=cls.env['crm.stage'].create({
            'name':'New',
            'sequence':1,
            'team_id':cls.sales_team_convert.id,
        })

        cls.lead_1.write({'date_open':Datetime.from_string('2020-01-1511:30:00')})

        cls.crm_lead_dt_patcher=patch('flectra.addons.crm.models.crm_lead.fields.Datetime',wraps=Datetime)
        cls.crm_lead_dt_mock=cls.crm_lead_dt_patcher.start()

    @classmethod
    deftearDownClass(cls):
        cls.crm_lead_dt_patcher.stop()
        super(TestLeadConvertCommon,cls).tearDownClass()


classTestLeadConvertMassCommon(TestLeadConvertCommon):

    @classmethod
    defsetUpClass(cls):
        super(TestLeadConvertMassCommon,cls).setUpClass()
        #SalesTeamorganization
        #Role:M(teammember)R(teammanager)
        #SALESMAN-------------------sales_team_1-----sales_team_convert
        #admin----------------------M----------------/
        #user_sales_manager---------R----------------R
        #user_sales_leads-----------M----------------/
        #user_sales_leads_convert---/----------------M <--NEW
        #user_sales_salesman--------/----------------M

        cls.user_sales_leads_convert=mail_new_test_user(
            cls.env,login='user_sales_leads_convert',
            name='LucienSalesLeadsConvert',email='crm_leads_2@test.example.com',
            company_id=cls.env.ref("base.main_company").id,
            notification_type='inbox',
            groups='sales_team.group_sale_salesman_all_leads,base.group_partner_manager,crm.group_use_lead',
        )
        cls.sales_team_convert.write({
            'member_ids':[(4,cls.user_sales_leads_convert.id)]
        })

        cls.lead_w_partner=cls.env['crm.lead'].create({
            'name':'New1',
            'type':'lead',
            'probability':10,
            'user_id':cls.user_sales_manager.id,
            'stage_id':False,
            'partner_id':cls.contact_1.id,
        })
        cls.lead_w_partner.write({'stage_id':False})
        cls.lead_w_partner_company=cls.env['crm.lead'].create({
            'name':'New1',
            'type':'lead',
            'probability':15,
            'user_id':cls.user_sales_manager.id,
            'stage_id':cls.stage_team1_1.id,
            'partner_id':cls.contact_company_1.id,
            'contact_name':'HermesConrad',
            'email_from':'hermes.conrad@test.example.com',
        })
        cls.lead_w_contact=cls.env['crm.lead'].create({
            'name':'LeadContact',
            'type':'lead',
            'probability':15,
            'contact_name':'TestContact',
            'user_id':cls.user_sales_salesman.id,
            'stage_id':cls.stage_gen_1.id,
        })
        cls.lead_w_email=cls.env['crm.lead'].create({
            'name':'LeadEmailAsContact',
            'type':'lead',
            'probability':15,
            'email_from':'contact.email@test.example.com',
            'user_id':cls.user_sales_salesman.id,
            'stage_id':cls.stage_gen_1.id,
        })
        cls.lead_w_email_lost=cls.env['crm.lead'].create({
            'name':'Lost',
            'type':'lead',
            'probability':15,
            'email_from':'strange.from@test.example.com',
            'user_id':cls.user_sales_leads.id,
            'stage_id':cls.stage_team1_2.id,
            'active':False,
        })
        (cls.lead_w_partner|cls.lead_w_partner_company|cls.lead_w_contact|cls.lead_w_email|cls.lead_w_email_lost).flush()
