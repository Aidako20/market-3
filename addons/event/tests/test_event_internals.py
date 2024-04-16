#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromdatetimeimportdate,datetime,timedelta
fromunittest.mockimportpatch

fromflectra.addons.event.tests.commonimportTestEventCommon
fromflectraimportexceptions
fromflectra.fieldsimportDatetimeasFieldsDatetime,DateasFieldsDate
fromflectra.tests.commonimportusers
fromflectra.toolsimportmute_logger


classTestEventData(TestEventCommon):

    @classmethod
    defsetUpClass(cls):
        super(TestEventData,cls).setUpClass()
        cls.patcher=patch('flectra.addons.event.models.event_event.fields.Datetime',wraps=FieldsDatetime)
        cls.mock_datetime=cls.patcher.start()
        cls.mock_datetime.now.return_value=datetime(2020,1,31,10,0,0)
        cls.addClassCleanup(cls.patcher.stop)

        cls.event_0.write({
            'date_begin':datetime(2020,2,1,8,30,0),
            'date_end':datetime(2020,2,4,18,45,0),
        })

    @users('user_eventmanager')
    deftest_event_date_computation(self):
        event=self.event_0.with_user(self.env.user)
        event.write({
            'registration_ids':[(0,0,{'partner_id':self.event_customer.id,'name':'test_reg'})],
            'date_begin':datetime(2020,1,31,15,0,0),
            'date_end':datetime(2020,4,5,18,0,0),
        })
        registration=event.registration_ids[0]
        self.assertEqual(registration.get_date_range_str(),u'today')

        event.date_begin=datetime(2020,2,1,15,0,0)
        self.assertEqual(registration.get_date_range_str(),u'tomorrow')

        event.date_begin=datetime(2020,2,2,6,0,0)
        self.assertEqual(registration.get_date_range_str(),u'in2days')

        event.date_begin=datetime(2020,2,20,17,0,0)
        self.assertEqual(registration.get_date_range_str(),u'nextmonth')

        event.date_begin=datetime(2020,3,1,10,0,0)
        self.assertEqual(registration.get_date_range_str(),u'onMar1,2020,11:00:00AM')

        #Isactually8:30to20:00inMexico
        event.write({
            'date_begin':datetime(2020,1,31,14,30,0),
            'date_end':datetime(2020,2,1,2,0,0),
            'date_tz':'Mexico/General'
        })
        self.assertTrue(event.is_one_day)

    @users('user_eventmanager')
    deftest_event_date_timezone(self):
        event=self.event_0.with_user(self.env.user)
        #Isactually8:30to20:00inMexico
        event.write({
            'date_begin':datetime(2020,1,31,14,30,0),
            'date_end':datetime(2020,2,1,2,0,0),
            'date_tz':'Mexico/General'
        })
        self.assertTrue(event.is_one_day)
        self.assertFalse(event.is_ongoing)

    @users('user_eventmanager')
    @mute_logger('flectra.models.unlink')
    deftest_event_configuration_from_type(self):
        """Testdatacomputationofeventcomingfromitsevent.typetemplate.
        Someone2manynotablyareduplicatedfromtypeconfigurationandsome
        advancedtestingisrequired,notablymailschedulers."""
        self.assertEqual(self.env.user.tz,'Europe/Brussels')

        #------------------------------------------------------------
        #STARTINGDATA
        #------------------------------------------------------------

        event_type=self.env['event.type'].browse(self.event_type_complex.id)
        event_type.write({
            'use_mail_schedule':False,
            'use_ticket':False,
        })
        self.assertEqual(event_type.event_type_mail_ids,self.env['event.type.mail'])
        self.assertEqual(event_type.event_type_ticket_ids,self.env['event.type.ticket'])

        event=self.env['event.event'].create({
            'name':'EventUpdateType',
            'date_begin':FieldsDatetime.to_string(datetime.today()+timedelta(days=1)),
            'date_end':FieldsDatetime.to_string(datetime.today()+timedelta(days=15)),
        })
        self.assertEqual(event.date_tz,self.env.user.tz)
        self.assertFalse(event.seats_limited)
        self.assertFalse(event.auto_confirm)
        self.assertEqual(event.event_mail_ids,self.env['event.mail'])
        self.assertEqual(event.event_ticket_ids,self.env['event.event.ticket'])

        registration=self._create_registrations(event,1)
        self.assertEqual(registration.state,'draft') #eventisnotautoconfirm

        #------------------------------------------------------------
        #FILLSYNCTEST
        #------------------------------------------------------------

        #changetemplatetoaonewithmails->filleventasitisvoid
        event_type.write({
            'use_mail_schedule':True,
            'event_type_mail_ids':[(5,0),(0,0,{
                'interval_nbr':1,'interval_unit':'days','interval_type':'before_event',
                'template_id':self.env['ir.model.data'].xmlid_to_res_id('event.event_reminder')})],
            'use_ticket':True,
            'event_type_ticket_ids':[(5,0),(0,0,{'name':'TestRegistration'})],
        })
        event.write({'event_type_id':event_type.id})
        self.assertEqual(event.date_tz,'Europe/Paris')
        self.assertTrue(event.seats_limited)
        self.assertEqual(event.seats_max,event_type.seats_max)
        self.assertTrue(event.auto_confirm)
        #check2manyfieldsbeingpopulated
        self.assertEqual(len(event.event_mail_ids),1)
        self.assertEqual(event.event_mail_ids.interval_nbr,1)
        self.assertEqual(event.event_mail_ids.interval_unit,'days')
        self.assertEqual(event.event_mail_ids.interval_type,'before_event')
        self.assertEqual(event.event_mail_ids.template_id,self.env.ref('event.event_reminder'))
        self.assertEqual(len(event.event_ticket_ids),1)

        #updatetemplate,unlinkfromevent->shouldnotimpactevent
        event_type.write({'has_seats_limitation':False})
        self.assertEqual(event_type.seats_max,0)
        self.assertTrue(event.seats_limited)
        self.assertEqual(event.seats_max,30) #originaltemplatevalue
        event.write({'event_type_id':False})
        self.assertEqual(event.event_type_id,self.env["event.type"])

        #settemplateback->updateevent
        event.write({'event_type_id':event_type.id})
        self.assertFalse(event.seats_limited)
        self.assertEqual(event.seats_max,0)
        self.assertEqual(len(event.event_ticket_ids),1)
        event_ticket1=event.event_ticket_ids[0]
        self.assertEqual(event_ticket1.name,'TestRegistration')

        #------------------------------------------------------------
        #RESETTEST
        #------------------------------------------------------------

        #linkregistrationtoticket
        registration.write({'event_ticket_id':event_ticket1.id})
        self.assertEqual(registration.event_ticket_id,event_ticket1)

        #changetemplatetoavoidoneformails->reseteventlinesthatarevoid
        #changetemplatetoaonewithothertickets->keeplinelinkedtoaregistration
        event_type.write({
            'use_mail_schedule':False,
            'event_type_mail_ids':[(5,0)],
            'event_type_ticket_ids':[(5,0),
                                      (0,0,{'name':'Registration1'}),
                                      (0,0,{'name':'Registration2'})],
        })
        event._compute_event_ticket_ids()
        event._compute_event_mail_ids()
        self.assertEqual(event.event_mail_ids,self.env['event.mail'])
        self.assertEqual(len(event.event_ticket_ids),3)
        self.assertEqual(
            set(event.mapped('event_ticket_ids.name')),
            set(['TestRegistration','Registration1','Registration2'])
        )
        #registrationlooseitsticket
        self.assertEqual(registration.event_ticket_id,event_ticket1)

        #changetemplatetoaonewithdifferentmails->resetevent
        event_type.write({
            'use_mail_schedule':True,
            'event_type_mail_ids':[(5,0),(0,0,{
                'interval_nbr':3,'interval_unit':'days','interval_type':'after_event',
                'template_id':self.env['ir.model.data'].xmlid_to_res_id('event.event_reminder')})]
        })
        event._compute_event_ticket_ids()
        event._compute_event_mail_ids()
        self.assertEqual(len(event.event_mail_ids),1)
        self.assertEqual(event.event_mail_ids.interval_nbr,3)
        self.assertEqual(event.event_mail_ids.interval_type,'after_event')

    @users('user_eventmanager')
    deftest_event_registrable(self):
        """Testif`_compute_event_registrations_open`worksproperly."""
        event=self.event_0.with_user(self.env.user)
        event.write({
            'date_begin':datetime(2020,1,30,8,0,0),
            'date_end':datetime(2020,1,31,8,0,0),
        })
        self.assertFalse(event.event_registrations_open)
        event.write({
            'date_end':datetime(2020,2,4,8,0,0),
        })
        self.assertTrue(event.event_registrations_open)

        #ticketwithoutdatesboundaries->ok
        ticket=self.env['event.event.ticket'].create({
            'name':'TestTicket',
            'event_id':event.id,
        })
        self.assertTrue(event.event_registrations_open)

        #evenwithvalidtickets,datelimitsregistrations
        event.write({
            'date_begin':datetime(2020,1,28,15,0,0),
            'date_end':datetime(2020,1,30,15,0,0),
        })
        self.assertFalse(event.event_registrations_open)

        #nomoreseatsavailable
        registration=self.env['event.registration'].create({
            'name':'AlbertTest',
            'event_id':event.id,
        })
        registration.action_confirm()
        event.write({
            'date_end':datetime(2020,2,1,15,0,0),
            'seats_max':1,
            'seats_limited':True,
        })
        self.assertEqual(event.seats_available,0)
        self.assertFalse(event.event_registrations_open)

        #seatsavailableareback
        registration.unlink()
        self.assertEqual(event.seats_available,1)
        self.assertTrue(event.event_registrations_open)

        #butticketsareexpired
        ticket.write({'end_sale_date':datetime(2020,1,30,15,0,0)})
        self.assertTrue(ticket.is_expired)
        self.assertFalse(event.event_registrations_open)

    @users('user_eventmanager')
    deftest_event_ongoing(self):
        event_1=self.env['event.event'].create({
            'name':'TestEvent1',
            'date_begin':datetime(2020,1,25,8,0,0),
            'date_end':datetime(2020,2,1,18,0,0),
        })
        self.assertTrue(event_1.is_ongoing)
        ongoing_event_ids=self.env['event.event']._search([('is_ongoing','=',True)])
        self.assertIn(event_1.id,ongoing_event_ids)

        event_1.update({'date_begin':datetime(2020,2,1,9,0,0)})
        self.assertFalse(event_1.is_ongoing)
        ongoing_event_ids=self.env['event.event']._search([('is_ongoing','=',True)])
        self.assertNotIn(event_1.id,ongoing_event_ids)

        event_2=self.env['event.event'].create({
            'name':'TestEvent2',
            'date_begin':datetime(2020,1,25,8,0,0),
            'date_end':datetime(2020,1,28,8,0,0),
        })
        self.assertFalse(event_2.is_ongoing)
        finished_or_upcoming_event_ids=self.env['event.event']._search([('is_ongoing','=',False)])
        self.assertIn(event_2.id,finished_or_upcoming_event_ids)

        event_2.update({'date_end':datetime(2020,2,2,8,0,1)})
        self.assertTrue(event_2.is_ongoing)
        finished_or_upcoming_event_ids=self.env['event.event']._search([('is_ongoing','=',False)])
        self.assertNotIn(event_2.id,finished_or_upcoming_event_ids)

    @users('user_eventmanager')
    deftest_event_seats(self):
        event_type=self.event_type_complex.with_user(self.env.user)
        event=self.env['event.event'].create({
            'name':'EventUpdateType',
            'event_type_id':event_type.id,
            'date_begin':FieldsDatetime.to_string(datetime.today()+timedelta(days=1)),
            'date_end':FieldsDatetime.to_string(datetime.today()+timedelta(days=15)),
        })

        self.assertEqual(event.address_id,self.env.user.company_id.partner_id)
        #seats:comingfromeventtypeconfiguration
        self.assertTrue(event.seats_limited)
        self.assertEqual(event.seats_available,event.event_type_id.seats_max)
        self.assertEqual(event.seats_unconfirmed,0)
        self.assertEqual(event.seats_reserved,0)
        self.assertEqual(event.seats_used,0)
        self.assertEqual(event.seats_expected,0)

        #createregistrationinordertochecktheseatscomputation
        self.assertTrue(event.auto_confirm)
        forxinrange(5):
            reg=self.env['event.registration'].create({
                'event_id':event.id,
                'name':'reg_open',
            })
            self.assertEqual(reg.state,'open')
        reg_draft=self.env['event.registration'].create({
            'event_id':event.id,
            'name':'reg_draft',
        })
        reg_draft.write({'state':'draft'})
        reg_done=self.env['event.registration'].create({
            'event_id':event.id,
            'name':'reg_done',
        })
        reg_done.write({'state':'done'})
        self.assertEqual(event.seats_available,event.event_type_id.seats_max-6)
        self.assertEqual(event.seats_unconfirmed,1)
        self.assertEqual(event.seats_reserved,5)
        self.assertEqual(event.seats_used,1)
        self.assertEqual(event.seats_expected,7)


classTestEventRegistrationData(TestEventCommon):

    @users('user_eventmanager')
    deftest_registration_partner_sync(self):
        """Testregistrationcomputedfieldsaboutpartner"""
        test_email='"NibblerInSpace"<nibbler@futurama.example.com>'
        test_phone='0456001122'

        event=self.env['event.event'].browse(self.event_0.ids)
        customer=self.env['res.partner'].browse(self.event_customer.id)

        #takeallfrompartner
        event.write({
            'registration_ids':[(0,0,{
                'partner_id':customer.id,
            })]
        })
        new_reg=event.registration_ids[0]
        self.assertEqual(new_reg.partner_id,customer)
        self.assertEqual(new_reg.name,customer.name)
        self.assertEqual(new_reg.email,customer.email)
        self.assertEqual(new_reg.phone,customer.phone)

        #partialupdate
        event.write({
            'registration_ids':[(0,0,{
                'partner_id':customer.id,
                'name':'NibblerInSpace',
                'email':test_email,
            })]
        })
        new_reg=event.registration_ids.sorted()[0]
        self.assertEqual(new_reg.partner_id,customer)
        self.assertEqual(
            new_reg.name,'NibblerInSpace',
            'Registrationshouldtakeuserinputovercomputedpartnervalue')
        self.assertEqual(
            new_reg.email,test_email,
            'Registrationshouldtakeuserinputovercomputedpartnervalue')
        self.assertEqual(
            new_reg.phone,customer.phone,
            'Registrationshouldtakepartnervalueifnotuserinput')

        #alreadyfilledinformationshouldnotbeupdated
        event.write({
            'registration_ids':[(0,0,{
                'name':'NibblerInSpace',
                'phone':test_phone,
            })]
        })
        new_reg=event.registration_ids.sorted()[0]
        self.assertEqual(new_reg.name,'NibblerInSpace')
        self.assertEqual(new_reg.email,False)
        self.assertEqual(new_reg.phone,test_phone)
        new_reg.write({'partner_id':customer.id})
        self.assertEqual(new_reg.partner_id,customer)
        self.assertEqual(new_reg.name,'NibblerInSpace')
        self.assertEqual(new_reg.email,customer.email)
        self.assertEqual(new_reg.phone,test_phone)

    @users('user_eventmanager')
    deftest_registration_partner_sync_company(self):
        """Testsynchronizationinvolvingcompanies"""
        event=self.env['event.event'].browse(self.event_0.ids)
        customer=self.env['res.partner'].browse(self.event_customer.id)

        #createcompanystructure(usingsudoasrequiredpartnermanagergroup)
        company=self.env['res.partner'].sudo().create({
            'name':'CustomerCompany',
            'is_company':True,
            'type':'other',
        })
        customer.sudo().write({'type':'invoice','parent_id':company.id})
        contact=self.env['res.partner'].sudo().create({
            'name':'ContactName',
            'parent_id':company.id,
            'type':'contact',
            'email':'ContactEmail<contact.email@test.example.com>',
            'phone':'+32456998877',
        })

        #takeallfrompartner
        event.write({
            'registration_ids':[(0,0,{
                'partner_id':customer.id,
            })]
        })
        new_reg=event.registration_ids[0]
        self.assertEqual(new_reg.partner_id,customer)
        self.assertEqual(new_reg.name,contact.name)
        self.assertEqual(new_reg.email,contact.email)
        self.assertEqual(new_reg.phone,contact.phone)


classTestEventTicketData(TestEventCommon):

    defsetUp(self):
        super(TestEventTicketData,self).setUp()
        self.ticket_date_patcher=patch('flectra.addons.event.models.event_ticket.fields.Date',wraps=FieldsDate)
        self.ticket_date_patcher_mock=self.ticket_date_patcher.start()
        self.ticket_date_patcher_mock.context_today.return_value=date(2020,1,31)

    deftearDown(self):
        super(TestEventTicketData,self).tearDown()
        self.ticket_date_patcher.stop()

    @users('user_eventmanager')
    deftest_event_ticket_fields(self):
        """Testeventticketfieldssynchronization"""
        event=self.event_0.with_user(self.env.user)
        event.write({
            'event_ticket_ids':[
                (5,0),
                (0,0,{
                    'name':'FirstTicket',
                    'seats_max':30,
                }),(0,0,{ #limitedintime,available(01/10(start)<01/31(today)<02/10(end))
                    'name':'SecondTicket',
                    'start_sale_date':date(2020,1,10),
                    'end_sale_date':date(2020,2,10),
                })
            ],
        })
        first_ticket=event.event_ticket_ids.filtered(lambdat:t.name=='FirstTicket')
        second_ticket=event.event_ticket_ids.filtered(lambdat:t.name=='SecondTicket')

        self.assertTrue(first_ticket.seats_limited)
        self.assertTrue(first_ticket.sale_available)
        self.assertFalse(first_ticket.is_expired)

        self.assertFalse(second_ticket.seats_limited)
        self.assertTrue(second_ticket.sale_available)
        self.assertFalse(second_ticket.is_expired)
        #saleisended
        second_ticket.write({'end_sale_date':date(2020,1,20)})
        self.assertFalse(second_ticket.sale_available)
        self.assertTrue(second_ticket.is_expired)
        #salehasnotstarted
        second_ticket.write({
            'start_sale_date':date(2020,2,10),
            'end_sale_date':date(2020,2,20),
        })
        self.assertFalse(second_ticket.sale_available)
        self.assertFalse(second_ticket.is_expired)
        #salestartedtoday
        second_ticket.write({
            'start_sale_date':date(2020,1,31),
            'end_sale_date':date(2020,2,20),
        })
        self.assertTrue(second_ticket.sale_available)
        self.assertTrue(second_ticket.is_launched())
        self.assertFalse(second_ticket.is_expired)
        #incoherentdatesareinvalid
        withself.assertRaises(exceptions.UserError):
            second_ticket.write({'end_sale_date':date(2020,1,20)})


classTestEventTypeData(TestEventCommon):

    @users('user_eventmanager')
    deftest_event_type_fields(self):
        """Testeventtypefieldssynchronization"""
        #createtesttypeandensureitsinitialvalues
        event_type=self.env['event.type'].create({
            'name':'Testingfieldscomputation',
            'has_seats_limitation':True,
            'seats_max':30,
            'use_ticket':True,
        })
        self.assertTrue(event_type.has_seats_limitation)
        self.assertEqual(event_type.seats_max,30)
        self.assertEqual(event_type.event_type_ticket_ids.mapped('name'),['Registration'])

        #resetseatslimitation
        event_type.write({'has_seats_limitation':False})
        self.assertFalse(event_type.has_seats_limitation)
        self.assertEqual(event_type.seats_max,0)

        #resettickets
        event_type.write({'use_ticket':False})
        self.assertEqual(event_type.event_type_ticket_ids,self.env['event.type.ticket'])
