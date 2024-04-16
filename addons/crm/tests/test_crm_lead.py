#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromdatetimeimportdatetime
fromfreezegunimportfreeze_time

fromflectra.addons.crm.models.crm_leadimportPARTNER_FIELDS_TO_SYNC,PARTNER_ADDRESS_FIELDS_TO_SYNC
fromflectra.addons.crm.tests.commonimportTestCrmCommon,INCOMING_EMAIL
fromflectra.addons.phone_validation.tools.phone_validationimportphone_format
fromflectra.exceptionsimportUserError
fromflectra.tests.commonimportForm,users
fromflectra.toolsimportmute_logger


classTestCRMLead(TestCrmCommon):

    @classmethod
    defsetUpClass(cls):
        super(TestCRMLead,cls).setUpClass()
        cls.country_ref=cls.env.ref('base.be')
        cls.test_email='"TestEmail"<test.email@example.com>'
        cls.test_phone='0485112233'

    defassertLeadAddress(self,lead,street,street2,city,lead_zip,state,country):
        self.assertEqual(lead.street,street)
        self.assertEqual(lead.street2,street2)
        self.assertEqual(lead.city,city)
        self.assertEqual(lead.zip,lead_zip)
        self.assertEqual(lead.state_id,state)
        self.assertEqual(lead.country_id,country)

    @users('user_sales_leads')
    deftest_crm_lead_contact_fields_mixed(self):
        """Testmixedconfigurationfrompartner:bothuserinputandcoming
        frompartner,inordertoensurewedonotlooseinformationormake
        itincoherent."""
        lead_data={
            'name':'TestMixed',
            'partner_id':self.contact_1.id,
            #address
            'country_id':self.country_ref.id,
            #othercontactfields
            'function':'ParmesanRappeur',
            'lang_id':False,
            #specificcontactfields
            'email_from':self.test_email,
            'phone':self.test_phone,
        }
        lead=self.env['crm.lead'].create(lead_data)
        #classic
        self.assertEqual(lead.name,"TestMixed")
        #address
        self.assertLeadAddress(lead,False,False,False,False,self.env['res.country.state'],self.country_ref)
        #othercontactfields
        forfnameinset(PARTNER_FIELDS_TO_SYNC)-set(['function']):
            self.assertEqual(lead[fname],self.contact_1[fname],'Nouserinput->takefromcontactforfield%s'%fname)
        self.assertEqual(lead.function,'ParmesanRappeur','Userinputshouldtakeoverpartnervalue')
        self.assertFalse(lead.lang_id)
        #specificcontactfields
        self.assertEqual(lead.partner_name,self.contact_company_1.name)
        self.assertEqual(lead.contact_name,self.contact_1.name)
        self.assertEqual(lead.email_from,self.test_email)
        self.assertEqual(lead.phone,self.test_phone)

        #updateasingleaddressfields->onlythoseareupdated
        lead.write({'street':'SuperStreet','city':'SuperCity'})
        self.assertLeadAddress(lead,'SuperStreet',False,'SuperCity',False,self.env['res.country.state'],self.country_ref)

        #changepartner->wholeaddressupdated
        lead.write({'partner_id':self.contact_company_1.id})
        forfnameinPARTNER_ADDRESS_FIELDS_TO_SYNC:
            self.assertEqual(lead[fname],self.contact_company_1[fname])
            self.assertEqual(self.contact_company_1.lang,self.lang_en.code)
            self.assertEqual(lead.lang_id,self.lang_en)

    @users('user_sales_leads')
    deftest_crm_lead_creation_no_partner(self):
        lead_data={
            'name':'Test',
            'country_id':self.country_ref.id,
            'email_from':self.test_email,
            'phone':self.test_phone,
        }
        lead=self.env['crm.lead'].new(lead_data)
        #getthestreetshouldnottriggercachemiss
        lead.street
        #Createtheleadandthewritepartner_id=False:countryshouldremain
        lead=self.env['crm.lead'].create(lead_data)
        self.assertEqual(lead.country_id,self.country_ref,"Countryshouldbesetonthelead")
        self.assertEqual(lead.email_from,self.test_email)
        self.assertEqual(lead.phone,self.test_phone)
        lead.partner_id=False
        self.assertEqual(lead.country_id,self.country_ref,"Countryshouldstillbesetonthelead")
        self.assertEqual(lead.email_from,self.test_email)
        self.assertEqual(lead.phone,self.test_phone)

    @users('user_sales_manager')
    deftest_crm_lead_creation_partner(self):
        lead=self.env['crm.lead'].create({
            'name':'TestLead',
            'contact_name':'RaouletteTestContact',
            'email_from':'"RaouletteTestContact"<raoulette@test.example.com>',
        })
        self.assertEqual(lead.type,'lead')
        self.assertEqual(lead.user_id,self.user_sales_manager)
        self.assertEqual(lead.team_id,self.sales_team_1)
        self.assertEqual(lead.stage_id,self.stage_team1_1)
        self.assertEqual(lead.contact_name,'RaouletteTestContact')
        self.assertEqual(lead.email_from,'"RaouletteTestContact"<raoulette@test.example.com>')

        #updatetoapartner,shouldudpateaddress
        lead.write({'partner_id':self.contact_1.id})
        self.assertEqual(lead.partner_name,self.contact_company_1.name)
        self.assertEqual(lead.contact_name,self.contact_1.name)
        self.assertEqual(lead.email_from,self.contact_1.email)
        self.assertEqual(lead.street,self.contact_1.street)
        self.assertEqual(lead.city,self.contact_1.city)
        self.assertEqual(lead.zip,self.contact_1.zip)
        self.assertEqual(lead.country_id,self.contact_1.country_id)

    @users('user_sales_manager')
    deftest_crm_lead_creation_partner_address(self):
        """Testthatanaddresserasesallleadaddressfields(avoidmixedaddresses)"""
        other_country=self.env.ref('base.fr')
        empty_partner=self.env['res.partner'].create({
            'name':'Emptypartner',
            'country_id':other_country.id,
        })
        lead_data={
            'name':'Test',
            'street':'Mystreet',
            'street2':'Mystreet',
            'city':'Mycity',
            'zip':'test@flectrahq.com',
            'state_id':self.env['res.country.state'].create({
                'name':'Mystate',
                'country_id':self.country_ref.id,
                'code':'MST',
            }).id,
            'country_id':self.country_ref.id,
        }
        lead=self.env['crm.lead'].create(lead_data)
        lead.partner_id=empty_partner
        #PARTNER_ADDRESS_FIELDS_TO_SYNC
        self.assertEqual(lead.street,empty_partner.street,"StreetshouldbesyncfromthePartner")
        self.assertEqual(lead.street2,empty_partner.street2,"Street2shouldbesyncfromthePartner")
        self.assertEqual(lead.city,empty_partner.city,"CityshouldbesyncfromthePartner")
        self.assertEqual(lead.zip,empty_partner.zip,"ZipshouldbesyncfromthePartner")
        self.assertEqual(lead.state_id,empty_partner.state_id,"StateshouldbesyncfromthePartner")
        self.assertEqual(lead.country_id,empty_partner.country_id,"CountryshouldbesyncfromthePartner")

    @users('user_sales_manager')
    deftest_crm_lead_creation_partner_no_address(self):
        """Testthatanemptyaddressonpartnerdoesnotvoiditsleadvalues"""
        empty_partner=self.env['res.partner'].create({
            'name':'Emptypartner',
            'is_company':True,
            'mobile':'123456789',
            'title':self.env.ref('base.res_partner_title_mister').id,
            'function':'Myfunction',
        })
        lead_data={
            'name':'Test',
            'contact_name':'Test',
            'street':'Mystreet',
            'country_id':self.country_ref.id,
            'email_from':self.test_email,
            'phone':self.test_phone,
            'mobile':'987654321',
            'website':'http://mywebsite.org',
        }
        lead=self.env['crm.lead'].create(lead_data)
        lead.partner_id=empty_partner
        #SPECIFICFIELDS
        self.assertEqual(lead.contact_name,lead_data['contact_name'],"Contactshouldremain")
        self.assertEqual(lead.email_from,lead_data['email_from'],"EmailFromshouldkeepitsinitialvalue")
        self.assertEqual(lead.partner_name,empty_partner.name,"Partnernameshouldbesetascontactisacompany")
        #PARTNER_ADDRESS_FIELDS_TO_SYNC
        self.assertEqual(lead.street,lead_data['street'],"Streetshouldremainsincepartnerhasnoaddressfieldset")
        self.assertEqual(lead.street2,False,"Street2shouldremainsincepartnerhasnoaddressfieldset")
        self.assertEqual(lead.country_id,self.country_ref,"Countryshouldremainsincepartnerhasnoaddressfieldset")
        self.assertEqual(lead.city,False,"Cityshouldremainsincepartnerhasnoaddressfieldset")
        self.assertEqual(lead.zip,False,"Zipshouldremainsincepartnerhasnoaddressfieldset")
        self.assertEqual(lead.state_id,self.env['res.country.state'],"Stateshouldremainsincepartnerhasnoaddressfieldset")
        #PARTNER_FIELDS_TO_SYNC
        self.assertEqual(lead.phone,lead_data['phone'],"Phoneshouldkeepitsinitialvalue")
        self.assertEqual(lead.mobile,empty_partner.mobile,"Mobilefrompartnershouldbesetonthelead")
        self.assertEqual(lead.title,empty_partner.title,"Titlefrompartnershouldbesetonthelead")
        self.assertEqual(lead.function,empty_partner.function,"Functionfrompartnershouldbesetonthelead")
        self.assertEqual(lead.website,lead_data['website'],"Websiteshouldkeepitsinitialvalue")

    @users('user_sales_manager')
    deftest_crm_lead_date_closed(self):
        #Testforonewonlead
        stage_team1_won2=self.env['crm.stage'].create({
            'name':'Won2',
            'sequence':75,
            'team_id':self.sales_team_1.id,
            'is_won':True,
        })
        won_lead=self.lead_team_1_won.with_env(self.env)
        other_lead=self.lead_1.with_env(self.env)
        old_date_closed=won_lead.date_closed
        self.assertTrue(won_lead.date_closed)
        self.assertFalse(other_lead.date_closed)

        #multiupdate
        leads=won_lead+other_lead
        withfreeze_time('2020-02-0218:00'):
            leads.stage_id=stage_team1_won2
        self.assertEqual(won_lead.date_closed,old_date_closed,'Shouldnotchangedate')
        self.assertEqual(other_lead.date_closed,datetime(2020,2,2,18,0,0))

        #backtoopenstage
        leads.write({'stage_id':self.stage_team1_2.id})
        self.assertFalse(won_lead.date_closed)
        self.assertFalse(other_lead.date_closed)

        #closewithlost
        withfreeze_time('2020-02-0218:00'):
            leads.action_set_lost()
        self.assertEqual(won_lead.date_closed,datetime(2020,2,2,18,0,0))
        self.assertEqual(other_lead.date_closed,datetime(2020,2,2,18,0,0))

    @users('user_sales_leads')
    @freeze_time("2012-01-14")
    deftest_crm_lead_lost_date_closed(self):
        lead=self.lead_1.with_env(self.env)
        self.assertFalse(lead.date_closed,"Initially,closeddateisnotset")
        #Marktheleadaslost
        lead.action_set_lost()
        self.assertEqual(lead.date_closed,datetime.now(),"Closeddateisupdatedaftermarkingleadaslost")

    @users('user_sales_manager')
    deftest_crm_lead_partner_sync(self):
        lead,partner=self.lead_1.with_user(self.env.user),self.contact_2
        partner_email,partner_phone=self.contact_2.email,self.contact_2.phone
        lead.partner_id=partner

        #email&phonemustbeautomaticallysetonthelead
        lead.partner_id=partner
        self.assertEqual(lead.email_from,partner_email)
        self.assertEqual(lead.phone,partner_phone)

        #writingontheleadfieldmustchangethepartnerfield
        lead.email_from='"JohnZoidberg"<john.zoidberg@test.example.com>'
        lead.phone='+12025557799'
        self.assertEqual(partner.email,'"JohnZoidberg"<john.zoidberg@test.example.com>')
        self.assertEqual(partner.email_normalized,'john.zoidberg@test.example.com')
        self.assertEqual(partner.phone,'+12025557799')

        #writingonthepartnermustchangetheleadvalues
        partner.email=partner_email
        partner.phone='+12025556666'
        self.assertEqual(lead.email_from,partner_email)
        self.assertEqual(lead.phone,'+12025556666')

        #resettingleadvaluesalsoresetspartner
        lead.email_from,lead.phone=False,False
        self.assertFalse(partner.email)
        self.assertFalse(partner.email_normalized)
        self.assertFalse(partner.phone)

    @users('user_sales_manager')
    deftest_crm_lead_partner_sync_email_phone(self):
        """Specificallytestsynchronizebetweenaleadanditspartnerabout
        phoneandemailfields.Phoneespeciallyhassomecornercasesdueto
        automaticformatting(notablywithonchangeinformview)."""
        lead,partner=self.lead_1.with_user(self.env.user),self.contact_2
        lead_form=Form(lead)

        #resetpartnerphonetoalocalnumberandprepareformatted/sanitizedvalues
        partner_phone,partner_mobile=self.test_phone_data[2],self.test_phone_data[1]
        partner_phone_formatted=phone_format(partner_phone,'US','1')
        partner_phone_sanitized=phone_format(partner_phone,'US','1',force_format='E164')
        partner_mobile_formatted=phone_format(partner_mobile,'US','1')
        partner_mobile_sanitized=phone_format(partner_mobile,'US','1',force_format='E164')
        partner_email,partner_email_normalized=self.test_email_data[2],self.test_email_data_normalized[2]
        self.assertEqual(partner_phone_formatted,'+1202-555-0888')
        self.assertEqual(partner_phone_sanitized,self.test_phone_data_sanitized[2])
        self.assertEqual(partner_mobile_formatted,'+1202-555-0999')
        self.assertEqual(partner_mobile_sanitized,self.test_phone_data_sanitized[1])
        #ensureinitialdata
        self.assertEqual(partner.phone,partner_phone)
        self.assertEqual(partner.mobile,partner_mobile)
        self.assertEqual(partner.email,partner_email)

        #LEAD/PARTNERSYNC:emailandphonearepropagatedtolead
        #aswellasmobile(whodoesnottriggerthereversesync)
        lead_form.partner_id=partner
        self.assertEqual(lead_form.email_from,partner_email)
        self.assertEqual(lead_form.phone,partner_phone_formatted,
                         'Lead:formautomaticallyformatsnumbers')
        self.assertEqual(lead_form.mobile,partner_mobile_formatted,
                         'Lead:formautomaticallyformatsnumbers')
        self.assertFalse(lead_form.ribbon_message)

        lead_form.save()
        self.assertEqual(partner.phone,partner_phone,
                         'Lead/Partner:partnervaluessenttolead')
        self.assertEqual(lead.email_from,partner_email,
                         'Lead/Partner:partnervaluessenttolead')
        self.assertEqual(lead.email_normalized,partner_email_normalized,
                         'Lead/Partner:equalemailsshouldleadtoequalnormalizedemails')
        self.assertEqual(lead.phone,partner_phone_formatted,
                         'Lead/Partner:partnervalues(formatted)senttolead')
        self.assertEqual(lead.mobile,partner_mobile_formatted,
                         'Lead/Partner:partnervalues(formatted)senttolead')
        self.assertEqual(lead.phone_sanitized,partner_mobile_sanitized,
                         'Lead:phone_sanitizedcomputedfieldonmobile')

        #foremail_from,ifonlyformattingdiffers,warningribbonshould
        #notappearandemailonpartnershouldnotbeupdated
        lead_form.email_from='"HermesConrad"<%s>'%partner_email_normalized
        self.assertFalse(lead_form.ribbon_message)
        lead_form.save()
        self.assertEqual(lead_form.partner_id.email,partner_email)

        #LEAD/PARTNERSYNC:leadupdatespartner
        new_email='"JohnZoidberg"<john.zoidberg@test.example.com>'
        new_email_normalized='john.zoidberg@test.example.com'
        lead_form.email_from=new_email
        self.assertIn('thecustomeremailwill',lead_form.ribbon_message)
        new_phone='+12025557799'
        new_phone_formatted=phone_format(new_phone,'US','1')
        lead_form.phone=new_phone
        self.assertEqual(lead_form.phone,new_phone_formatted)
        self.assertIn('thecustomeremailandphonenumberwill',lead_form.ribbon_message)

        lead_form.save()
        self.assertEqual(partner.email,new_email)
        self.assertEqual(partner.email_normalized,new_email_normalized)
        self.assertEqual(partner.phone,new_phone_formatted)

        #LEAD/PARTNERSYNC:mobiledoesnotupdatepartner
        new_mobile='+12025556543'
        new_mobile_formatted=phone_format(new_mobile,'US','1')
        lead_form.mobile=new_mobile
        lead_form.save()
        self.assertEqual(lead.mobile,new_mobile_formatted)
        self.assertEqual(partner.mobile,partner_mobile)

        #LEAD/PARTNERSYNC:resetingleadvaluesalsoresetspartnerforemail
        #andphone,butnotformobile
        lead_form.email_from,lead_form.phone,lead.mobile=False,False,False
        self.assertIn('thecustomeremailandphonenumberwill',lead_form.ribbon_message)
        lead_form.save()
        self.assertFalse(partner.email)
        self.assertFalse(partner.email_normalized)
        self.assertFalse(partner.phone)
        self.assertFalse(lead.phone)
        self.assertFalse(lead.mobile)
        self.assertFalse(lead.phone_sanitized)
        self.assertEqual(partner.mobile,partner_mobile)
        self.assertEqual(partner.phone_sanitized,partner_mobile_sanitized,
                         'Partnersanitizedshouldbecomputedonmobile')

    @users('user_sales_manager')
    deftest_crm_lead_partner_sync_email_phone_corner_cases(self):
        """Testcornercasesofemailandphonesync(Falseversus'',formatting
        differences,wronginput,...)"""
        test_email='amy.wong@test.example.com'
        lead=self.lead_1.with_user(self.env.user)
        contact=self.env['res.partner'].create({
            'name':'NoContactPartner',
            'phone':'',
            'email':'',
            'mobile':'',
        })

        lead_form=Form(lead)
        self.assertEqual(lead_form.email_from,test_email)
        self.assertFalse(lead_form.ribbon_message)

        #email:Falseversusemptystring
        lead_form.partner_id=contact
        self.assertIn('thecustomeremail',lead_form.ribbon_message)
        lead_form.email_from=''
        self.assertFalse(lead_form.ribbon_message)
        lead_form.email_from=False
        self.assertFalse(lead_form.ribbon_message)

        #phone:Falseversusemptystring
        lead_form.phone='+1202-555-0888'
        self.assertIn('thecustomerphone',lead_form.ribbon_message)
        lead_form.phone=''
        self.assertFalse(lead_form.ribbon_message)
        lead_form.phone=False
        self.assertFalse(lead_form.ribbon_message)

        #email/phone:formattingshouldnottriggerribbon
        lead.write({
            'email_from':'"MyName"<%s>'%test_email,
            'phone':'+1202-555-0888',
        })
        contact.write({
            'email':'"MyName"<%s>'%test_email,
            'phone':'+1202-555-0888',
        })

        lead_form=Form(lead)
        self.assertFalse(lead_form.ribbon_message)
        lead_form.partner_id=contact
        self.assertFalse(lead_form.ribbon_message)
        lead_form.email_from='"AnotherName"<%s>'%test_email #sameemailnormalized
        self.assertFalse(lead_form.ribbon_message,'Formatting-onlychangeshouldnottriggerwrite')
        lead_form.phone='2025550888' #samenumberbutanotherformat
        self.assertFalse(lead_form.ribbon_message,'Formatting-onlychangeshouldnottriggerwrite')

        #wrongvaluearealsopropagated
        lead_form.phone='666789456789456789456'
        self.assertIn('thecustomerphone',lead_form.ribbon_message)

    @users('user_sales_manager')
    deftest_crm_lead_stages(self):
        lead=self.lead_1.with_user(self.env.user)
        self.assertEqual(lead.team_id,self.sales_team_1)

        lead.convert_opportunity(self.contact_1.id)
        self.assertEqual(lead.team_id,self.sales_team_1)

        lead.action_set_won()
        self.assertEqual(lead.probability,100.0)
        self.assertEqual(lead.stage_id,self.stage_gen_won) #genericwonstagehaslowersequencethanteamwonstage

    @users('user_sales_manager')
    deftest_crm_lead_unlink_calendar_event(self):
        """Testres_id/res_modelisreset(andhidedocumentbuttonincalendar
        eventformview)whenleadisunlinked"""
        lead=self.env['crm.lead'].create({'name':'LeadWithMeetings'})
        meetings=self.env['calendar.event'].create([
            {
                'name':'Meeting1ofLead',
                'res_id':lead.id,
                'res_model_id':self.env['ir.model']._get_id(lead._name),
                'start':'2022-07-1208:00:00',
                'stop':'2022-07-1210:00:00',
            },{
                'name':'Meeting2ofLead',
                'opportunity_id':lead.id,
                'res_id':lead.id,
                'res_model_id':self.env['ir.model']._get_id(lead._name),
                'start':'2022-07-1308:00:00',
                'stop':'2022-07-1310:00:00',
            }
        ])
        self.assertEqual(lead.meeting_count,1)
        self.assertEqual(meetings.opportunity_id,lead)
        self.assertEqual(meetings.mapped('res_id'),[lead.id,lead.id])
        self.assertEqual(meetings.mapped('res_model'),['crm.lead','crm.lead'])
        lead.unlink()
        self.assertEqual(meetings.exists(),meetings)
        self.assertFalse(meetings.opportunity_id)
        self.assertEqual(set(meetings.mapped('res_id')),set([0]))
        self.assertEqual(set(meetings.mapped('res_model')),set([False]))

    @users('user_sales_leads')
    deftest_crm_lead_update_contact(self):
        #ensureinitialdata,especiallyforcornercases
        self.assertFalse(self.contact_company_1.phone)
        self.assertEqual(self.contact_company_1.country_id.code,"US")
        lead=self.env['crm.lead'].create({
            'name':'Test',
            'country_id':self.country_ref.id,
            'email_from':self.test_email,
            'phone':self.test_phone,
        })
        self.assertEqual(lead.country_id,self.country_ref,"Countryshouldbesetonthelead")
        lead.partner_id=False
        self.assertEqual(lead.country_id,self.country_ref,"Countryshouldstillbesetonthelead")
        self.assertEqual(lead.email_from,self.test_email)
        self.assertEqual(lead.phone,self.test_phone)
        self.assertEqual(lead.email_state,'correct')
        self.assertEqual(lead.phone_state,'correct')

        lead.partner_id=self.contact_company_1
        self.assertEqual(lead.country_id,self.contact_company_1.country_id,"Countryshouldstillbetheonesetonpartner")
        self.assertEqual(lead.email_from,self.contact_company_1.email)
        self.assertEqual(lead.phone,self.test_phone)
        self.assertEqual(lead.email_state,'correct')
        #currentlywekeepphoneaspartnerasavoidone->mayleadtoinconsistencies
        self.assertEqual(lead.phone_state,'incorrect',"BelgianphonewithUScountry->consideredasincorrect")

        lead.email_from='broken'
        lead.phone='alsobroken'
        self.assertEqual(lead.email_state,'incorrect')
        self.assertEqual(lead.phone_state,'incorrect')
        self.assertEqual(self.contact_company_1.email,'broken')
        self.assertEqual(self.contact_company_1.phone,'alsobroken')

    @users('user_sales_manager')
    deftest_crm_team_alias(self):
        new_team=self.env['crm.team'].create({
            'name':'TestAlias',
            'use_leads':True,
            'use_opportunities':True,
            'alias_name':'test.alias'
        })
        self.assertEqual(new_team.alias_id.alias_name,'test.alias')
        self.assertEqual(new_team.alias_name,'test.alias')

        new_team.write({
            'use_leads':False,
            'use_opportunities':False,
        })
        #self.assertFalse(new_team.alias_id.alias_name)
        #self.assertFalse(new_team.alias_name)

    @mute_logger('flectra.addons.mail.models.mail_thread')
    deftest_mailgateway(self):
        new_lead=self.format_and_process(
            INCOMING_EMAIL,
            'unknown.sender@test.example.com',
            '%s@%s'%(self.sales_team_1.alias_name,self.alias_domain),
            subject='Deliverycostinquiry',
            target_model='crm.lead',
        )
        self.assertEqual(new_lead.email_from,'unknown.sender@test.example.com')
        self.assertFalse(new_lead.partner_id)
        self.assertEqual(new_lead.name,'Deliverycostinquiry')

        message=new_lead.with_user(self.user_sales_manager).message_post(
            body='Hereismyoffer!',
            subtype_xmlid='mail.mt_comment')
        self.assertEqual(message.author_id,self.user_sales_manager.partner_id)

        new_lead.handle_partner_assignment(create_missing=True)
        self.assertEqual(new_lead.partner_id.email,'unknown.sender@test.example.com')
        self.assertEqual(new_lead.partner_id.team_id,self.sales_team_1)

    @users('user_sales_manager')
    deftest_phone_mobile_update(self):
        lead=self.env['crm.lead'].create({
            'name':'Lead1',
            'country_id':self.env.ref('base.us').id,
            'phone':self.test_phone_data[0],
        })
        self.assertEqual(lead.phone,self.test_phone_data[0])
        self.assertFalse(lead.mobile)
        self.assertEqual(lead.phone_sanitized,self.test_phone_data_sanitized[0])

        lead.write({'phone':False,'mobile':self.test_phone_data[1]})
        self.assertFalse(lead.phone)
        self.assertEqual(lead.mobile,self.test_phone_data[1])
        self.assertEqual(lead.phone_sanitized,self.test_phone_data_sanitized[1])

        lead.write({'phone':self.test_phone_data[1],'mobile':self.test_phone_data[2]})
        self.assertEqual(lead.phone,self.test_phone_data[1])
        self.assertEqual(lead.mobile,self.test_phone_data[2])
        self.assertEqual(lead.phone_sanitized,self.test_phone_data_sanitized[2])

        #updatingcountryshouldtriggersanitizecomputation
        lead.write({'country_id':self.env.ref('base.be').id})
        self.assertEqual(lead.phone,self.test_phone_data[1])
        self.assertEqual(lead.mobile,self.test_phone_data[2])
        self.assertFalse(lead.phone_sanitized)

    @users('user_sales_manager')
    deftest_phone_mobile_search(self):
        lead_1=self.env['crm.lead'].create({
            'name':'Lead1',
            'country_id':self.env.ref('base.be').id,
            'phone':'+32485001122',
        })
        _lead_2=self.env['crm.lead'].create({
            'name':'Lead2',
            'country_id':self.env.ref('base.be').id,
            'phone':'+32485112233',
        })
        self.assertEqual(lead_1,self.env['crm.lead'].search([
            ('phone_mobile_search','like','+32485001122')
        ]))

        withself.assertRaises(UserError):
            self.env['crm.lead'].search([
                ('phone_mobile_search','like','tests@example.com')
            ])
