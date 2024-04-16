#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importdatetime

fromdateutil.relativedeltaimportrelativedelta

fromflectra.addons.event_sale.tests.commonimportTestEventSaleCommon
fromflectra.tests.commonimportForm


classTestEventSpecific(TestEventSaleCommon):

    deftest_event_change_max_seat_no_side_effect(self):
        """
        TestthatchangingtheMaximum(seats_max),theseats_reservedofalltheticketdonotchange
        """
        #Enable"sellticketswithsalesorders"sothatwehaveapricecolumnonthetickets
        #Eventtemplate
        withForm(self.env['event.type'])asevent_type_form:
            event_type_form.name="PastafarianEventTemplate"
            event_type_form.use_ticket=True
            #Editthedefaultline
            withevent_type_form.event_type_ticket_ids.edit(0)asticket_line:
                ticket_line.name='PastafarianRegistration'
                ticket_line.price=0
            event_type=event_type_form.save()

        withForm(self.env['event.event'])asevent_event_form:
            event_event_form.name='AnnualPastafarianReunion(APR)'
            event_event_form.date_begin=datetime.datetime.now()+relativedelta(days=2)
            event_event_form.date_end=datetime.datetime.now()+relativedelta(days=3)
            event_event_form.event_type_id=event_type #Setthetemplate
            event_event_form.auto_confirm=True
            #Createsecondticket(VIP)
            withevent_event_form.event_ticket_ids.new()asticket_line:
                ticket_line.name='VIP(VeryImportantPastafarian)'
                ticket_line.price=10
            event_event=event_event_form.save()

        #Addtworegistrationsfortheevent,oneregistrationforeachtickettype
        forticketinevent_event.event_ticket_ids:
            self.env['event.registration'].create({
                'event_id':event_event.id,
                'event_ticket_id':ticket.id
            })

        #Editthemaximum
        before_confirmed=[t.seats_reservedfortinevent_event.event_ticket_ids]
        withForm(event_event)asevent_event_form:
            withevent_event_form.event_ticket_ids.edit(0)asticket_line:
                ticket_line.seats_max=ticket_line.seats_max+1
        after_confirmed=[t.seats_reservedfortinevent_event.event_ticket_ids]
        self.assertEqual(before_confirmed,after_confirmed)
