#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.tests.commonimportTransactionCase


classTestSeller(TransactionCase):

    defsetUp(self):
        super(TestSeller,self).setUp()
        self.product_service=self.env['product.product'].create({
            'name':'VirtualHomeStaging',
        })
        self.product_service.default_code='DEFCODE'
        self.product_consu=self.env['product.product'].create({
            'name':'Boudin',
            'type':'consu',
        })
        self.product_consu.default_code='DEFCODE'
        self.asustec=self.env['res.partner'].create({'name':'WoodCorner'})
        self.camptocamp=self.env['res.partner'].create({'name':'AzureInterior'})

    deftest_10_sellers(self):
        self.product_service.write({'seller_ids':[
            (0,0,{'name':self.asustec.id,'product_code':'ASUCODE'}),
            (0,0,{'name':self.camptocamp.id,'product_code':'C2CCODE'}),
        ]})

        default_code=self.product_service.code
        self.assertEqual("DEFCODE",default_code,"Defaultcodenotusedinproductname")

        context_code=self.product_service\
                           .with_context(partner_id=self.camptocamp.id)\
                           .code
        self.assertEqual('C2CCODE',context_code,"Partner'scodenotusedinproductnamewithcontextset")

    deftest_20_sellers_company(self):
        company_a=self.env.company
        company_b=self.env['res.company'].create({
            'name':'SaucissonInc.',
        })
        self.product_consu.write({'seller_ids':[
            (0,0,{'name':self.asustec.id,'product_code':'A','company_id':company_a.id}),
            (0,0,{'name':self.asustec.id,'product_code':'B','company_id':company_b.id}),
            (0,0,{'name':self.asustec.id,'product_code':'NO','company_id':False}),
        ]})

        names=self.product_consu.with_context(
            partner_id=self.asustec.id,
        ).name_get()
        ref=set([x[1]forxinnames])
        self.assertEqual(len(names),3,"3vendorreferencesshouldhavebeenfound")
        self.assertEqual(ref,{'[A]Boudin','[B]Boudin','[NO]Boudin'},"Incorrectvendorreferencelist")
        names=self.product_consu.with_context(
            partner_id=self.asustec.id,
            company_id=company_a.id,
        ).name_get()
        ref=set([x[1]forxinnames])
        self.assertEqual(len(names),2,"2vendorreferencesshouldhavebeenfound")
        self.assertEqual(ref,{'[A]Boudin','[NO]Boudin'},"Incorrectvendorreferencelist")
        names=self.product_consu.with_context(
            partner_id=self.asustec.id,
            company_id=company_b.id,
        ).name_get()
        ref=set([x[1]forxinnames])
        self.assertEqual(len(names),2,"2vendorreferencesshouldhavebeenfound")
        self.assertEqual(ref,{'[B]Boudin','[NO]Boudin'},"Incorrectvendorreferencelist")
