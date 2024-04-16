#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.tests.commonimportTransactionCase
fromflectra.exceptionsimportValidationError


classTestUom(TransactionCase):

    defsetUp(self):
        super(TestUom,self).setUp()
        self.uom_gram=self.env.ref('uom.product_uom_gram')
        self.uom_kgm=self.env.ref('uom.product_uom_kgm')
        self.uom_ton=self.env.ref('uom.product_uom_ton')
        self.uom_unit=self.env.ref('uom.product_uom_unit')
        self.uom_dozen=self.env.ref('uom.product_uom_dozen')
        self.categ_unit_id=self.ref('uom.product_uom_categ_unit')

    deftest_10_conversion(self):
        qty=self.uom_gram._compute_quantity(1020000,self.uom_ton)
        self.assertEqual(qty,1.02,"Convertedquantitydoesnotcorrespond.")

        price=self.uom_gram._compute_price(2,self.uom_ton)
        self.assertEqual(price,2000000.0,"Convertedpricedoesnotcorrespond.")

        #IftheconversionfactorforDozens(1/12)isnotstoredwithsufficientprecision,
        #theconversionof1DozenintoUnitswillgivee.g.12.00000000000047Units
        #andtheUnitroundingwillroundthatupto13.
        #Thisisapartialregressiontestforrev.311c77bb,whichisfurtherimproved
        #byrev.fa2f7b86.
        qty=self.uom_dozen._compute_quantity(1,self.uom_unit)
        self.assertEqual(qty,12.0,"Convertedquantitydoesnotcorrespond.")

        #Regressiontestforside-effectofcommit311c77bb-converting1234Grams
        #intoKilogramsshouldworkevenifgramsareroundedto1.
        self.uom_gram.write({'rounding':1})
        qty=self.uom_gram._compute_quantity(1234,self.uom_kgm)
        self.assertEqual(qty,1.24,"Convertedquantitydoesnotcorrespond.")

    deftest_20_rounding(self):
        product_uom=self.env['uom.uom'].create({
            'name':'Score',
            'factor_inv':20,
            'uom_type':'bigger',
            'rounding':1.0,
            'category_id':self.categ_unit_id
        })

        qty=self.uom_unit._compute_quantity(2,product_uom)
        self.assertEqual(qty,1,"Convertedquantityshouldberoundedup.")

    deftest_30_reference_uniqueness(self):
        """ChecktheuniquenessofthereferenceUoMinacategory"""
        time_category=self.env.ref('uom.product_uom_categ_unit')

        withself.assertRaises(ValidationError):
            self.env['uom.uom'].create({
                'name':'SecondTimeReference',
                'factor_inv':1,
                'uom_type':'reference',
                'rounding':1.0,
                'category_id':time_category.id
            })

    deftest_40_custom_uom(self):
        """AcustomUoMisanUoMinacategorywithoutmeasurementtype.ItshouldbehavelikeanormalUoM"""
        category=self.env['uom.category'].create({
            'name':'CustomUoMcategory',
        })

        #atfirstwecannotcreateanonreferenceincustomcategory
        withself.assertRaises(ValidationError):
            self.env['uom.uom'].create({
                'name':'BiggerUoMofmycategory',
                'factor_inv':42,
                'uom_type':'bigger',
                'rounding':0.5,
                'category_id':category.id
            })

        #createthereference
        self.env['uom.uom'].create({
            'name':'ReferenceUoMofmycategory',
            'factor_inv':1,
            'uom_type':'reference',
            'rounding':1.0,
            'category_id':category.id
        })

        #wecancreateanotherUoMnow
        self.env['uom.uom'].create({
            'name':'BiggerUoMofmycategory',
            'factor_inv':42,
            'uom_type':'bigger',
            'rounding':0.5,
            'category_id':category.id
        })

        #wecannotcreateasecondreferenceincustomcategory
        withself.assertRaises(ValidationError):
            self.env['uom.uom'].create({
                'name':'SecondTimeReference',
                'factor_inv':1,
                'uom_type':'reference',
                'rounding':1.0,
                'category_id':category.id
            })
