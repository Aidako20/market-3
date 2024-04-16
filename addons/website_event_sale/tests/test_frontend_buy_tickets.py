#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importflectra.tests

fromdatetimeimporttimedelta

fromflectra.addons.base.tests.commonimportHttpCaseWithUserDemo
fromflectra.fieldsimportDatetime


@flectra.tests.common.tagged('post_install','-at_install')
classTestUi(HttpCaseWithUserDemo):

    defsetUp(self):
        super().setUp()
        self.event_2=self.env['event.event'].create({
            'name':'ConferenceforArchitectsTEST',
            'user_id':self.env.ref('base.user_admin').id,
            'date_begin':(Datetime.today()+timedelta(days=5)).strftime('%Y-%m-%d07:00:00'),
            'date_end':(Datetime.today()+timedelta(days=5)).strftime('%Y-%m-%d16:30:00'),
            'website_published':True,
        })

        self.env['event.event.ticket'].create([{
            'name':'Standard',
            'event_id':self.event_2.id,
            'product_id':self.env.ref('event_sale.product_product_event').id,
            'start_sale_date':(Datetime.today()-timedelta(days=5)).strftime('%Y-%m-%d07:00:00'),
            'end_sale_date':(Datetime.today()+timedelta(90)).strftime('%Y-%m-%d'),
            'price':1000.0,
        },{
            'name':'VIP',
            'event_id':self.event_2.id,
            'product_id':self.env.ref('event_sale.product_product_event').id,
            'end_sale_date':(Datetime.today()+timedelta(90)).strftime('%Y-%m-%d'),
            'price':1500.0,
        }])

        self.event_3=self.env['event.event'].create({
            'name':'Lasttickettest',
            'user_id':self.env.ref('base.user_admin').id,
            'date_begin':(Datetime.today()+timedelta(days=5)).strftime('%Y-%m-%d07:00:00'),
            'date_end':(Datetime.today()+timedelta(days=5)).strftime('%Y-%m-%d16:30:00'),
            'website_published':True,
        })

        self.env['event.event.ticket'].create([{
            'name':'VIP',
            'event_id':self.event_3.id,
            'product_id':self.env.ref('event_sale.product_product_event').id,
            'end_sale_date':(Datetime.today()+timedelta(90)).strftime('%Y-%m-%d'),
            'price':1500.0,
            'seats_max':2,
        }])


        #flusheventtoensurehavingticketsavailableinthetests
        self.event_2.flush()
        self.event_3.flush()

        (self.env.ref('base.partner_admin')+self.partner_demo).write({
            'street':'215VineSt',
            'city':'Scranton',
            'zip':'18503',
            'country_id':self.env.ref('base.us').id,
            'state_id':self.env.ref('base.state_us_39').id,
            'phone':'+1555-555-5555',
            'email':'admin@yourcompany.example.com',
        })

        cash_journal=self.env['account.journal'].create({'name':'Cash-Test','type':'cash','code':'CASH-Test'})
        self.env.ref('payment.payment_acquirer_transfer').journal_id=cash_journal

    deftest_admin(self):
        #Seenthat:
        #-thistestreliesondemodatathatareentirelyinUSD(pricelists)
        #-thatmaindemocompanyisgelocatedinUS
        #-thatthistestawaitsforhardcodedUSDsamount
        #wehavetoforcecompanycurrencyasUSDsonlyforthistest
        self.cr.execute("UPDATEres_companySETcurrency_id=%sWHEREid=%s",[self.env.ref('base.USD').id,self.env.ref('base.main_company').id])

        self.start_tour("/",'event_buy_tickets',login="admin")

    deftest_demo(self):
        self.start_tour("/",'event_buy_tickets',login="demo")

    deftest_buy_last_ticket(self):
        self.start_tour("/",'event_buy_last_ticket')

    #TODO-addpublictestwithnewaddresswhenconverttoweb.tourformat.
