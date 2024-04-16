#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importflectra.tests


@flectra.tests.tagged('post_install','-at_install')
classTestUi(flectra.tests.HttpCase):

    deftest_01_free_delivery_when_exceed_threshold(self):
        
        #AvoidShipping/Billingaddresspage
        self.env.ref('base.partner_admin').write({
            'street':'215VineSt',
            'city':'Scranton',
            'zip':'18503',
            'country_id':self.env.ref('base.us').id,
            'state_id':self.env.ref('base.state_us_39').id,
            'phone':'+1555-555-5555',
            'email':'admin@yourcompany.example.com',
        })

        office_chair=self.env['product.product'].create({
            'name':'OfficeChairBlackTEST',
            'list_price':12.50,
        })
        self.env.ref("delivery.free_delivery_carrier").write({
            'name':'DeliveryNowFreeOver10',
            'fixed_price':2,
            'free_over':True,
            'amount':10,
        })
        self.product_delivery_poste=self.env['product.product'].create({
            'name':'ThePoste',
            'type':'service',
            'categ_id':self.env.ref('delivery.product_category_deliveries').id,
            'sale_ok':False,
            'purchase_ok':False,
            'list_price':20.0,
        })
        self.carrier=self.env['delivery.carrier'].create({
            'name':'ThePoste',
            'sequence':9999,#ensurelasttoloadpriceasync
            'fixed_price':20.0,
            'delivery_type':'base_on_rule',
            'product_id':self.product_delivery_poste.id,
            'website_published':True,
        })
        self.env['delivery.price.rule'].create([{
            'carrier_id':self.carrier.id,
            'max_value':5,
            'list_base_price':20,
        },{
            'carrier_id':self.carrier.id,
            'operator':'>=',
            'max_value':5,
            'list_base_price':50,
        },{
            'carrier_id':self.carrier.id,
            'operator':'>=',
            'max_value':300,
            'variable':'price',
            'list_base_price':0,
        }])

        cash_journal=self.env['account.journal'].create({'name':'Cash-Test','type':'cash','code':'CASH-Test'})
        self.env.ref('payment.payment_acquirer_transfer').journal_id=cash_journal

        #Ensure"WireTransfer"isthedefaultacquirer.
        #Acquirersaresortedbystate,showing`test`acquirersfirst(don'taskwhy).
        self.env.ref("payment.payment_acquirer_transfer").write({"state":"test"})

        self.start_tour("/",'check_free_delivery',login="admin")
