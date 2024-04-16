#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromdatetimeimportdate,datetime,timedelta
fromunittest.mockimportpatch

fromflectra.addons.event_sale.tests.commonimportTestEventSaleCommon
fromflectra.fieldsimportDatetimeasFieldsDatetime,DateasFieldsDate
fromflectra.tests.commonimportusers


classTestEventData(TestEventSaleCommon):

    @users('user_eventmanager')
    deftest_event_configuration_from_type(self):
        """Inadditiontoeventtest,alsotestticketsconfigurationcoming
        fromevent_salecapabilities."""
        event_type=self.event_type_complex.with_user(self.env.user)
        event_type.write({
            'use_mail_schedule':False,
            'use_ticket':False,
        })
        self.assertEqual(event_type.event_type_ticket_ids,self.env['event.type.ticket'])

        event=self.env['event.event'].create({
            'name':'EventUpdateType',
            'event_type_id':event_type.id,
            'date_begin':FieldsDatetime.to_string(datetime.today()+timedelta(days=1)),
            'date_end':FieldsDatetime.to_string(datetime.today()+timedelta(days=15)),
        })
        self.assertEqual(event.event_ticket_ids,self.env['event.event.ticket'])

        event_type.write({
            'use_ticket':True,
            'event_type_ticket_ids':[(5,0),(0,0,{
                'name':'FirstTicket',
                'product_id':self.event_product.id,
                'seats_max':5,
            })]
        })
        self.assertEqual(event_type.event_type_ticket_ids.description,self.event_product.description_sale)

        #synchronizeevent
        event.write({'event_type_id':event_type.id})
        self.assertEqual(event.event_ticket_ids.name,event.event_type_id.event_type_ticket_ids.name)
        self.assertTrue(event.event_ticket_ids.seats_limited)
        self.assertEqual(event.event_ticket_ids.seats_max,5)
        self.assertEqual(event.event_ticket_ids.product_id,self.event_product)
        self.assertEqual(event.event_ticket_ids.price,self.event_product.list_price)
        self.assertEqual(event.event_ticket_ids.description,self.event_product.description_sale)

    deftest_event_registrable(self):
        """Testif`_compute_event_registrations_open`worksproperlywithadditional
        productactiveconditionscomparedtobasetests(seeevent)"""
        event=self.event_0.with_user(self.env.user)
        self.assertTrue(event.event_registrations_open)

        #ticketwithoutdatesboundaries->ok
        ticket=self.env['event.event.ticket'].create({
            'name':'TestTicket',
            'event_id':event.id,
            'product_id':self.event_product.id,
        })
        self.assertTrue(event.event_registrations_open)

        #tickethasinactiveproduct->ko
        ticket.product_id.action_archive()
        self.assertFalse(event.event_registrations_open)

        #atleastonevalidticket->okisback
        event_product=self.env['product.product'].create({'name':'TestRegistrationProductNew',})
        new_ticket=self.env['event.event.ticket'].create({
            'name':'TestTicket2',
            'event_id':event.id,
            'product_id':event_product.id,
            'end_sale_date':datetime.now()+timedelta(days=2),
        })
        self.assertTrue(new_ticket.sale_available)
        self.assertTrue(event.event_registrations_open)


classTestEventTicketData(TestEventSaleCommon):

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
                    'product_id':self.event_product.id,
                    'seats_max':30,
                }),(0,0,{ #limitedintime,available(01/10(start)<01/31(today)<02/10(end))
                    'name':'SecondTicket',
                    'product_id':self.event_product.id,
                    'start_sale_date':date(2020,1,10),
                    'end_sale_date':date(2020,2,10),
                })
            ],
        })
        first_ticket=event.event_ticket_ids.filtered(lambdat:t.name=='FirstTicket')
        second_ticket=event.event_ticket_ids.filtered(lambdat:t.name=='SecondTicket')
        #forcesecondticketprice,aftercallingtheonchange
        second_ticket.write({'price':8.0})

        #pricecomingfromproduct
        self.assertEqual(first_ticket.price,self.event_product.list_price)
        self.assertEqual(second_ticket.price,8.0)

        #defaultavailability
        self.assertTrue(first_ticket.seats_limited)
        self.assertTrue(first_ticket.sale_available)
        self.assertFalse(first_ticket.is_expired)
        self.assertFalse(second_ticket.seats_limited)
        self.assertTrue(second_ticket.sale_available)
        self.assertFalse(second_ticket.is_expired)

        #productarchived
        self.event_product.action_archive()
        self.assertFalse(first_ticket.sale_available)
        self.assertFalse(second_ticket.sale_available)

        #saleisended
        self.event_product.action_unarchive()
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
