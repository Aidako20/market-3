#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.addons.event_crm.tests.commonimportTestEventCrmCommon
fromflectra.tests.commonimportusers
fromflectra.toolsimportmute_logger


classTestEventCrmFlow(TestEventCrmCommon):

    @classmethod
    defsetUpClass(cls):
        super(TestEventCrmFlow,cls).setUpClass()

        cls.registration_values=[
            dict(customer_data,event_id=cls.event_0.id)
            forcustomer_dataincls.batch_customer_data
        ]
        cls.registration_values[-1]['email']='"JohnDoe"<invalid@not.example.com>'

    deftest_assert_initial_data(self):
        """Ensurebasetestvaluestoeasetestunderstandingandmaintenance"""
        self.assertEqual(len(self.registration_values),5)

        self.assertEqual(self.event_customer.country_id,self.env.ref('base.be'))
        self.assertEqual(self.event_customer.email_normalized,'constantin@test.example.com')
        self.assertFalse(self.event_customer.mobile)
        self.assertEqual(self.event_customer.phone,'0485112233')

    @users('user_eventmanager')
    deftest_event_crm_flow_batch_create(self):
        """Testattendee-andorder-basedregistrationscreation.Event-based
        creationmimicsasimplifiedwebsite_eventflowwheregroupingisdone
        atcreate."""
        new_registrations=self.env['event.registration'].create(self.registration_values)
        self.assertEqual(len(self.event_0.registration_ids),5)

        #per-attendeerule:oneleadforeachregistration
        self.assertEqual(len(self.test_rule_attendee.lead_ids),4)
        forregistrationinnew_registrations:
            lead=self.test_rule_attendee.lead_ids.filtered(lambdalead:registrationinlead.registration_ids)
            #testfilteringoutbasedondomain
            ifregistration.email=='"JohnDoe"<invalid@not.example.com>':
                self.assertEqual(lead,self.env['crm.lead'])
                continue

            #onlypartnerwithmatchingemail/phoneiskeptinmonoattendeemodetoavoid
            #loosingregistration-specificemail/phoneinformationsduetoleadsynchronization
            expected_partner=registration.partner_idifregistration.partner_id==self.event_customerelseNone
            self.assertTrue(bool(lead))
            self.assertLeadConvertion(self.test_rule_attendee,registration,partner=expected_partner)

        #per-orderrule:oneleadforallregistrations(sameevent->samebatch,website_eventstyle)
        self.assertEqual(len(self.test_rule_order.lead_ids),1)
        lead=self.test_rule_order.lead_ids
        self.assertLeadConvertion(
            self.test_rule_order,
            new_registrations.filtered(lambdareg:reg.email!='"JohnDoe"<invalid@not.example.com>'),
            partner=new_registrations[0].partner_id
        )
        #ensuringfilteringoutworkedalsoatdescriptionlevel
        self.assertNotIn('invalid@not.example.com',lead.description)

    @users('user_eventmanager')
    deftest_event_crm_flow_batch_update(self):
        """Testupdateofcontactordescriptionfieldsthatleadstolead
        update."""
        #initialdata:createregistrationsinbatch
        new_registrations=self.env['event.registration'].create(self.registration_values)
        self.assertEqual(len(self.event_0.registration_ids),5)
        self.assertEqual(len(self.test_rule_attendee.lead_ids),4)
        self.assertEqual(len(self.test_rule_order.lead_ids),1)

        #customerisupdated(likeaSOsettingitscustomer)
        new_registrations.write({'partner_id':self.event_customer2.id})

        #per-attendeerule
        self.assertEqual(len(self.test_rule_attendee.lead_ids),4)
        forregistrationinnew_registrations:
            lead=self.test_rule_attendee.lead_ids.filtered(lambdalead:registrationinlead.registration_ids)
            #testfilteringoutbasedondomain
            ifregistration.email=='"JohnDoe"<invalid@not.example.com>':
                self.assertEqual(lead,self.env['crm.lead'])
                continue

            #onlypartnerwithmatchingemail/phoneiskeptinmonoattendeemodetoavoid
            #loosingregistration-specificemail/phoneinformationsduetoleadsynchronization
            self.assertLeadConvertion(self.test_rule_attendee,registration,partner=None)

        #per-orderrule
        self.assertEqual(len(self.test_rule_order.lead_ids),1)
        self.assertEqual(self.test_rule_order.lead_ids.event_id,self.event_0)
        lead=self.test_rule_order.lead_ids
        self.assertLeadConvertion(
            self.test_rule_order,
            new_registrations.filtered(lambdareg:reg.email!='"JohnDoe"<invalid@not.example.com>'),
            partner=new_registrations[0].partner_id
        )
        #ensuringfilteringoutworkedalsoatdescriptionlevel
        self.assertNotIn('invalid@not.example.com',lead.description)

    @users('user_eventmanager')
    deftest_event_crm_flow_per_attendee_single_wo_partner(self):
        """Singleregistration,attendeebased,nopartnerinvolved,check
        contactinfopropagation"""
        forname,email,mobile,phonein[
            ('MyName','super.email@test.example.com','0456442211','0456332211'),
            (False,'super.email@test.example.com',False,'0456442211'),
            ('"MyName"','"MyName"<my.name@test.example.com',False,False),
        ]:
            withself.subTest(name=name,email=email,mobile=mobile,phone=phone):
                registration=self.env['event.registration'].create({
                    'name':name,
                    'partner_id':False,
                    'email':email,
                    'mobile':mobile,
                    'phone':phone,
                    'event_id':self.event_0.id,
                })
                self.assertLeadConvertion(self.test_rule_attendee,registration,partner=None)

        #test:partnerbutwithothercontactinformation->registrationprior
        registration=self.env['event.registration'].create({
            'partner_id':self.event_customer.id,
            'email':'other.email@test.example.com',
            'phone':False,
            'mobile':'0456112233',
            'event_id':self.event_0.id,
        })
        self.assertLeadConvertion(self.test_rule_attendee,registration,partner=None)

    @users('user_eventmanager')
    deftest_event_crm_flow_per_attendee_single_wpartner(self):
        """Singleregistration,attendeebased,withpartnerinvolved,check
        contactinformation,checksynchronizationandupdate"""
        self.event_customer2.write({
            'email':False,
            'phone':False,
        })
        self.test_rule_attendee.write({
            'event_registration_filter':'[]', #tryvariousemailcombinations
        })
        foremail,phone,base_partner,expected_partnerin[
            (False,False,self.event_customer,self.event_customer), #shouldtakepartnerinfo
            ('"OtherName"<constantin@test.example.com>',False,self.event_customer,self.event_customer), #sameemailnormalized
            ('other.email@test.example.com',False,self.event_customer,self.env['res.partner']), #notsameemail->nopartneronlead
            (False,'+32485112233',self.event_customer,self.event_customer), #samephonebutdifferentlyformatted
            (False,'0485112244',self.event_customer,self.env['res.partner']), #otherphone->nopartneronlead
            ('other.email@test.example.com','0485112244',self.event_customer2,self.event_customer2), #mail/phoneupdatefromregistrationasvoidonpartner
        ]:
            withself.subTest(email=email,phone=phone,base_partner=base_partner):
                registration=self.env['event.registration'].create({
                    'partner_id':base_partner.id,
                    'email':email,
                    'phone':phone,
                    'event_id':self.event_0.id,
                })
                self.assertLeadConvertion(self.test_rule_attendee,registration,partner=expected_partner)

    @users('user_eventmanager')
    deftest_order_rule_duplicate_lead(self):
        """Checkwhentworulesmatchoneevent
            butonlyonematchtheregistration,
            onlyoneleadshouldbecreated
        """
        test_rule_order_2=self.test_rule_order.copy(default={
            'event_registration_filter':[['email','notilike','@test.example.com']]
        })
        self.env['event.registration'].create({
            'name':'MyRegistration',
            'partner_id':False,
            'email':'super.email@test.example.com',
            'phone':False,
            'mobile':'0456332211',
            'event_id':self.event_0.id,
        })
        self.assertEqual(len(self.test_rule_order.lead_ids),1)
        self.assertEqual(len(test_rule_order_2.lead_ids),0)
