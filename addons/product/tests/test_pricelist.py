#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.tests.commonimportTransactionCase


classTestPricelist(TransactionCase):

    defsetUp(self):
        super(TestPricelist,self).setUp()

        self.datacard=self.env['product.product'].create({'name':'OfficeLamp'})
        self.usb_adapter=self.env['product.product'].create({'name':'OfficeChair'})
        self.uom_ton=self.env.ref('uom.product_uom_ton')
        self.uom_unit_id=self.ref('uom.product_uom_unit')
        self.uom_dozen_id=self.ref('uom.product_uom_dozen')
        self.uom_kgm_id=self.ref('uom.product_uom_kgm')

        self.public_pricelist=self.env.ref('product.list0')
        self.sale_pricelist_id=self.env['product.pricelist'].create({
            'name':'Salepricelist',
            'item_ids':[(0,0,{
                    'compute_price':'formula',
                    'base':'list_price', #basedonpublicprice
                    'price_discount':10,
                    'product_id':self.usb_adapter.id,
                    'applied_on':'0_product_variant',
                }),(0,0,{
                    'compute_price':'formula',
                    'base':'list_price', #basedonpublicprice
                    'price_surcharge':-0.5,
                    'product_id':self.datacard.id,
                    'applied_on':'0_product_variant',
                })]
        })

    deftest_10_discount(self):
        #Makesurethepriceusingapricelististhesamethanwithoutafter
        #applyingthecomputationmanually
        context={}

        public_context=dict(context,pricelist=self.public_pricelist.id)
        pricelist_context=dict(context,pricelist=self.sale_pricelist_id.id)

        usb_adapter_without_pricelist=self.usb_adapter.with_context(public_context)
        usb_adapter_with_pricelist=self.usb_adapter.with_context(pricelist_context)
        self.assertEqual(usb_adapter_with_pricelist.price,usb_adapter_without_pricelist.price*0.9)

        datacard_without_pricelist=self.datacard.with_context(public_context)
        datacard_with_pricelist=self.datacard.with_context(pricelist_context)
        self.assertEqual(datacard_with_pricelist.price,datacard_without_pricelist.price-0.5)

        #Makesurethatchangingtheunitofmeasuredoesnotbreaktheunit
        #price(afterconverting)
        unit_context=dict(context,pricelist=self.sale_pricelist_id.id,uom=self.uom_unit_id)
        dozen_context=dict(context,pricelist=self.sale_pricelist_id.id,uom=self.uom_dozen_id)

        usb_adapter_unit=self.usb_adapter.with_context(unit_context)
        usb_adapter_dozen=self.usb_adapter.with_context(dozen_context)
        self.assertAlmostEqual(usb_adapter_unit.price*12,usb_adapter_dozen.price)
        datacard_unit=self.datacard.with_context(unit_context)
        datacard_dozen=self.datacard.with_context(dozen_context)
        #price_surchargeappliestoproductdefaultUoM,here"Units",sosurchargewillbemultiplied
        self.assertAlmostEqual(datacard_unit.price*12,datacard_dozen.price)

    deftest_20_pricelist_uom(self):
        #Verifythatthepricelistrulesarecorrectlyusingtheproduct'sdefaultUoM
        #asreference,andreturnaresultaccordingtothetargetUoM(asspecificinthecontext)

        kg,tonne=self.uom_kgm_id,self.uom_ton.id
        tonne_price=100

        #makesure'tonne'resolvesdownto1'kg'.
        self.uom_ton.write({'rounding':0.001})
        #setupproductstoredin'tonnes',withadiscountedpricelistforqty>3tonnes
        spam_id=self.env['product.product'].create({
            'name':'1tonneofspam',
            'uom_id':self.uom_ton.id,
            'uom_po_id':self.uom_ton.id,
            'list_price':tonne_price,
            'type':'consu'
        })

        self.env['product.pricelist.item'].create({
            'pricelist_id':self.public_pricelist.id,
            'applied_on':'0_product_variant',
            'compute_price':'formula',
            'base':'list_price', #basedonpublicprice
            'min_quantity':3, #min=3tonnes
            'price_surcharge':-10, #-10EUR/tonne
            'product_id':spam_id.id
        })
        pricelist=self.public_pricelist

        deftest_unit_price(qty,uom,expected_unit_price):
            spam=spam_id.with_context({'uom':uom})
            unit_price=pricelist.with_context({'uom':uom}).get_product_price(spam,qty,False)
            self.assertAlmostEqual(unit_price,expected_unit_price,msg='Computedunitpriceiswrong')

        #Testprices-theyare*perunit*,thequantityisonlyheretomatchthepricelistrules!
        test_unit_price(2,kg,tonne_price/1000.0)
        test_unit_price(2000,kg,tonne_price/1000.0)
        test_unit_price(3500,kg,(tonne_price-10)/1000.0)
        test_unit_price(2,tonne,tonne_price)
        test_unit_price(3,tonne,tonne_price-10)
