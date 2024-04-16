#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromcontextlibimportclosing
fromdatetimeimportdatetime,timedelta
fromunittest.mockimportpatch

fromflectraimportfields
fromflectra.addons.mail.tests.commonimportmail_new_test_user
fromflectra.exceptionsimportValidationError
fromflectra.tests.commonimportSavepointCase
fromflectra.exceptionsimportAccessError,RedirectWarning,UserError


classStockQuant(SavepointCase):
    @classmethod
    defsetUpClass(cls):
        super(StockQuant,cls).setUpClass()
        cls.demo_user=mail_new_test_user(
            cls.env,
            name='PaulinePoivraisselle',
            login='pauline',
            email='p.p@example.com',
            notification_type='inbox',
            groups='base.group_user',
        )
        cls.stock_user=mail_new_test_user(
            cls.env,
            name='PaulinePoivraisselle',
            login='pauline2',
            email='p.p@example.com',
            notification_type='inbox',
            groups='stock.group_stock_user',
        )

        cls.product=cls.env['product.product'].create({
            'name':'ProductA',
            'type':'product',
        })
        cls.product_lot=cls.env['product.product'].create({
            'name':'ProductA',
            'type':'product',
            'tracking':'lot',
        })
        cls.product_consu=cls.env['product.product'].create({
            'name':'ProductA',
            'type':'consu',
        })
        cls.product_serial=cls.env['product.product'].create({
            'name':'ProductA',
            'type':'product',
            'tracking':'serial',
        })
        cls.stock_location=cls.env['stock.location'].create({
            'name':'stock_location',
            'usage':'internal',
        })
        cls.stock_subloc2=cls.env['stock.location'].create({
            'name':'subloc2',
            'usage':'internal',
            'location_id':cls.stock_location.id,
        })

    defgather_relevant(self,product_id,location_id,lot_id=None,package_id=None,owner_id=None,strict=False):
        quants=self.env['stock.quant']._gather(product_id,location_id,lot_id=lot_id,package_id=package_id,owner_id=owner_id,strict=strict)
        returnquants.filtered(lambdaq:not(q.quantity==0andq.reserved_quantity==0))

    deftest_get_available_quantity_1(self):
        """Quantityavailabilitywithonlyonequantinalocation.
        """
        self.env['stock.quant'].create({
            'product_id':self.product.id,
            'location_id':self.stock_location.id,
            'quantity':1.0,
        })
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),1.0)

    deftest_get_available_quantity_2(self):
        """Quantityavailabilitywithmultiplequantsinalocation.
        """
        foriinrange(3):
            self.env['stock.quant'].create({
                'product_id':self.product.id,
                'location_id':self.stock_location.id,
                'quantity':1.0,
            })
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),3.0)

    deftest_get_available_quantity_3(self):
        """Quantityavailabilitywithmultiplequants(includingnegativesones)inalocation.
        """
        foriinrange(3):
            self.env['stock.quant'].create({
                'product_id':self.product.id,
                'location_id':self.stock_location.id,
                'quantity':1.0,
            })
        self.env['stock.quant'].create({
            'product_id':self.product.id,
            'location_id':self.stock_location.id,
            'quantity':-3.0,
        })
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),0.0)

    deftest_get_available_quantity_4(self):
        """Quantityavailabilitywithnoquantsinalocation.
        """
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),0.0)

    deftest_get_available_quantity_5(self):
        """Quantityavailabilitywithmultiplepartiallyreservedquantsinalocation.
        """
        self.env['stock.quant'].create({
            'product_id':self.product.id,
            'location_id':self.stock_location.id,
            'quantity':10.0,
            'reserved_quantity':9.0,
        })
        self.env['stock.quant'].create({
            'product_id':self.product.id,
            'location_id':self.stock_location.id,
            'quantity':1.0,
            'reserved_quantity':1.0,
        })
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),1.0)

    deftest_get_available_quantity_6(self):
        """Quantityavailabilitywithmultiplepartiallyreservedquantsinalocation.
        """
        self.env['stock.quant'].create({
            'product_id':self.product.id,
            'location_id':self.stock_location.id,
            'quantity':10.0,
            'reserved_quantity':20.0,
        })
        self.env['stock.quant'].create({
            'product_id':self.product.id,
            'location_id':self.stock_location.id,
            'quantity':5.0,
            'reserved_quantity':0.0,
        })
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),0.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location,allow_negative=True),-5.0)

    deftest_get_available_quantity_7(self):
        """Quantityavailabilitywithonlyonetrackedquantinalocation.
        """
        lot1=self.env['stock.production.lot'].create({
            'name':'lot1',
            'product_id':self.product_lot.id,
            'company_id':self.env.company.id,
        })
        self.env['stock.quant'].create({
            'product_id':self.product_lot.id,
            'location_id':self.stock_location.id,
            'quantity':10.0,
            'reserved_quantity':20.0,
            'lot_id':lot1.id,
        })
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product_lot,self.stock_location,lot_id=lot1),0.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product_lot,self.stock_location,lot_id=lot1,allow_negative=True),-10.0)

    deftest_get_available_quantity_8(self):
        """Quantityavailabilitywithaconsumableproduct.
        """
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product_consu,self.stock_location),0.0)
        self.assertEqual(len(self.gather_relevant(self.product_consu,self.stock_location)),0)
        withself.assertRaises(ValidationError):
            self.env['stock.quant']._update_available_quantity(self.product_consu,self.stock_location,1.0)

    deftest_get_available_quantity_9(self):
        """Quantityavailabilitybyademouserwithaccessrights/rules.
        """
        self.env['stock.quant'].create({
            'product_id':self.product.id,
            'location_id':self.stock_location.id,
            'quantity':1.0,
        })
        self.env=self.env(user=self.demo_user)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),1.0)

    deftest_increase_available_quantity_1(self):
        """Increasetheavailablequantitywhennoquantsarealreadyinalocation.
        """
        self.env['stock.quant']._update_available_quantity(self.product,self.stock_location,1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),1.0)

    deftest_increase_available_quantity_2(self):
        """Increasetheavailablequantitywhenmultiplequantsarealreadyinalocation.
        """
        foriinrange(2):
            self.env['stock.quant'].create({
                'product_id':self.product.id,
                'location_id':self.stock_location.id,
                'quantity':1.0,
            })
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),2.0)
        self.env['stock.quant']._update_available_quantity(self.product,self.stock_location,1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),3.0)
        self.assertEqual(len(self.gather_relevant(self.product,self.stock_location)),2)

    deftest_increase_available_quantity_3(self):
        """Increasetheavailablequantitywhenaconcurrenttransactionisalreadyincreasing
        thereservedquanntityforthesameproduct.
        """
        quant=self.env['stock.quant'].search([('location_id','=',self.stock_location.id)],limit=1)
        ifnotquant:
            self.skipTest('Cannottestconcurrenttransactionswithoutdemodata.')
        product=quant.product_id
        available_quantity=self.env['stock.quant']._get_available_quantity(product,self.stock_location,allow_negative=True)
        #opensanewcursorandSELECTFORUPDATEthequant,tosimulateanotherconcurrentreserved
        #quantityincrease
        withclosing(self.registry.cursor())ascr:
            cr.execute("SELECTidFROMstock_quantWHEREproduct_id=%sANDlocation_id=%s",(product.id,self.stock_location.id))
            quant_id=cr.fetchone()
            cr.execute("SELECT1FROMstock_quantWHEREid=%sFORUPDATE",quant_id)
            self.env['stock.quant']._update_available_quantity(product,self.stock_location,1.0)

        self.assertEqual(self.env['stock.quant']._get_available_quantity(product,self.stock_location,allow_negative=True),available_quantity+1)
        self.assertEqual(len(self.gather_relevant(product,self.stock_location,strict=True)),2)

    deftest_increase_available_quantity_4(self):
        """Increasetheavailablequantitywhennoquantsarealreadyinalocationwithauserwithoutaccessright.
        """
        self.env=self.env(user=self.demo_user)
        self.env['stock.quant']._update_available_quantity(self.product,self.stock_location,1.0)

    deftest_increase_available_quantity_5(self):
        """Increasetheavailablequantitywhennoquantsarealreadyinstock.
        IncreaseasubLocationandcheckthatquantsareinthislocation.Alsotestinverse.
        """
        stock_sub_location=self.stock_location.child_ids[0]
        product2=self.env['product.product'].create({
            'name':'ProductB',
            'type':'product',
        })
        self.env['stock.quant']._update_available_quantity(self.product,self.stock_location,1.0)
        self.env['stock.quant']._update_available_quantity(self.product,stock_sub_location,1.0)

        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),2.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,stock_sub_location),1.0)

        self.env['stock.quant']._update_available_quantity(product2,stock_sub_location,1.0)
        self.env['stock.quant']._update_available_quantity(product2,self.stock_location,1.0)

        self.assertEqual(self.env['stock.quant']._get_available_quantity(product2,self.stock_location),2.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(product2,stock_sub_location),1.0)

    deftest_increase_available_quantity_6(self):
        """Increasingtheavailablequantityinaviewlocationshouldbeforbidden.
        """
        location1=self.env['stock.location'].create({
            'name':'viewloc1',
            'usage':'view',
            'location_id':self.stock_location.id,
        })
        withself.assertRaises(ValidationError):
            self.env['stock.quant']._update_available_quantity(self.product,location1,1.0)

    deftest_increase_available_quantity_7(self):
        """Settingalocation'susageas"view"shouldbeforbiddenifitalready
        containsquant.
        """
        self.env['stock.quant']._update_available_quantity(self.product,self.stock_location,1.0)
        self.assertTrue(len(self.stock_location.quant_ids.ids)>0)
        withself.assertRaises(UserError):
            self.stock_location.usage='view'

    deftest_decrease_available_quantity_1(self):
        """Decreasetheavailablequantitywhennoquantsarealreadyinalocation.
        """
        self.env['stock.quant']._update_available_quantity(self.product,self.stock_location,-1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),0.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location,allow_negative=True),-1.0)

    deftest_decrease_available_quantity_2(self):
        """Decreasetheavailablequantitywhenmultiplequantsarealreadyinalocation.
        """
        foriinrange(2):
            self.env['stock.quant'].create({
                'product_id':self.product.id,
                'location_id':self.stock_location.id,
                'quantity':1.0,
            })
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),2.0)
        self.assertEqual(len(self.gather_relevant(self.product,self.stock_location)),2)
        self.env['stock.quant']._update_available_quantity(self.product,self.stock_location,-1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),1.0)
        self.assertEqual(len(self.gather_relevant(self.product,self.stock_location)),1)

    deftest_decrease_available_quantity_3(self):
        """Decreasetheavailablequantitywhenaconcurrenttransactionisalreadyincreasing
        thereservedquanntityforthesameproduct.
        """
        quant=self.env['stock.quant'].search([('location_id','=',self.stock_location.id)],limit=1)
        ifnotquant:
            self.skipTest('Cannottestconcurrenttransactionswithoutdemodata.')
        product=quant.product_id
        available_quantity=self.env['stock.quant']._get_available_quantity(product,self.stock_location,allow_negative=True)

        #opensanewcursorandSELECTFORUPDATEthequant,tosimulateanotherconcurrentreserved
        #quantityincrease
        withclosing(self.registry.cursor())ascr:
            cr.execute("SELECT1FROMstock_quantWHEREid=%sFORUPDATE",quant.ids)
            self.env['stock.quant']._update_available_quantity(product,self.stock_location,-1.0)

        self.assertEqual(self.env['stock.quant']._get_available_quantity(product,self.stock_location,allow_negative=True),available_quantity-1)
        self.assertEqual(len(self.gather_relevant(product,self.stock_location,strict=True)),2)

    deftest_decrease_available_quantity_4(self):
        """Decreasetheavailablequantitythatdeletethequant.Theactiveusershouldhave
        read,writeandunlinkrights
        """
        self.env['stock.quant'].create({
            'product_id':self.product.id,
            'location_id':self.stock_location.id,
            'quantity':1.0,
        })
        self.env=self.env(user=self.demo_user)
        self.env['stock.quant']._update_available_quantity(self.product,self.stock_location,-1.0)
        self.assertEqual(len(self.gather_relevant(self.product,self.stock_location)),0)

    deftest_increase_reserved_quantity_1(self):
        """Increasethereservedquantityofquantityxwhenthere'sasinglequantinagiven
        locationwhichhasanavailablequantityofx.
        """
        self.env['stock.quant'].create({
            'product_id':self.product.id,
            'location_id':self.stock_location.id,
            'quantity':10.0,
        })
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),10.0)
        self.assertEqual(len(self.gather_relevant(self.product,self.stock_location)),1)
        self.env['stock.quant']._update_reserved_quantity(self.product,self.stock_location,10.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),0.0)
        self.assertEqual(len(self.gather_relevant(self.product,self.stock_location)),1)

    deftest_increase_reserved_quantity_2(self):
        """Increasethereservedquantityofquantityxwhenthere'stwoquantsinagiven
        locationwhichhaveanavailablequantityofxtogether.
        """
        foriinrange(2):
            self.env['stock.quant'].create({
                'product_id':self.product.id,
                'location_id':self.stock_location.id,
                'quantity':5.0,
            })
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),10.0)
        self.assertEqual(len(self.gather_relevant(self.product,self.stock_location)),2)
        self.env['stock.quant']._update_reserved_quantity(self.product,self.stock_location,10.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),0.0)
        self.assertEqual(len(self.gather_relevant(self.product,self.stock_location)),2)

    deftest_increase_reserved_quantity_3(self):
        """Increasethereservedquantityofquantityxwhenthere'smultiplequantsinagiven
        locationwhichhaveanavailablequantityofxtogether.
        """
        self.env['stock.quant'].create({
            'product_id':self.product.id,
            'location_id':self.stock_location.id,
            'quantity':5.0,
            'reserved_quantity':2.0,
        })
        self.env['stock.quant'].create({
            'product_id':self.product.id,
            'location_id':self.stock_location.id,
            'quantity':10.0,
            'reserved_quantity':12.0,
        })
        self.env['stock.quant'].create({
            'product_id':self.product.id,
            'location_id':self.stock_location.id,
            'quantity':8.0,
            'reserved_quantity':3.0,
        })
        self.env['stock.quant'].create({
            'product_id':self.product.id,
            'location_id':self.stock_location.id,
            'quantity':35.0,
            'reserved_quantity':12.0,
        })
        #totalquantity:58
        #totalreservedquantity:29
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),29.0)
        self.assertEqual(len(self.gather_relevant(self.product,self.stock_location)),4)
        self.env['stock.quant']._update_reserved_quantity(self.product,self.stock_location,10.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),19.0)
        self.assertEqual(len(self.gather_relevant(self.product,self.stock_location)),4)

    deftest_increase_reserved_quantity_4(self):
        """Increasethereservedquantityofquantityxwhenthere'smultiplequantsinagiven
        locationwhichhaveanavailablequantityofxtogether.
        """
        self.env['stock.quant'].create({
            'product_id':self.product.id,
            'location_id':self.stock_location.id,
            'quantity':5.0,
            'reserved_quantity':7.0,
        })
        self.env['stock.quant'].create({
            'product_id':self.product.id,
            'location_id':self.stock_location.id,
            'quantity':12.0,
            'reserved_quantity':10.0,
        })
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),0.0)
        self.assertEqual(len(self.gather_relevant(self.product,self.stock_location)),2)
        withself.assertRaises(UserError):
            self.env['stock.quant']._update_reserved_quantity(self.product,self.stock_location,10.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),0.0)

    deftest_increase_reserved_quantity_5(self):
        """Decreasetheavailablequantitywhennoquantareinalocation.
        """
        withself.assertRaises(UserError):
            self.env['stock.quant']._update_reserved_quantity(self.product,self.stock_location,1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),0.0)

    deftest_decrease_reserved_quantity_1(self):
        self.env['stock.quant'].create({
            'product_id':self.product.id,
            'location_id':self.stock_location.id,
            'quantity':10.0,
            'reserved_quantity':10.0,
        })
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),0.0)
        self.assertEqual(len(self.gather_relevant(self.product,self.stock_location)),1)
        self.env['stock.quant']._update_reserved_quantity(self.product,self.stock_location,-10.0,strict=True)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),10.0)
        self.assertEqual(len(self.gather_relevant(self.product,self.stock_location)),1)

    deftest_increase_decrease_reserved_quantity_1(self):
        """Decreasethenincreasereservedquantitywhennoquantareinalocation.
        """
        withself.assertRaises(UserError):
            self.env['stock.quant']._update_reserved_quantity(self.product,self.stock_location,1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),0.0)
        withself.assertRaises(RedirectWarning):
            self.env['stock.quant']._update_reserved_quantity(self.product,self.stock_location,-1.0,strict=True)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),0.0)

    deftest_action_done_1(self):
        pack_location=self.env.ref('stock.location_pack_zone')
        pack_location.active=True
        self.env['stock.quant']._update_available_quantity(self.product,self.stock_location,2.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),2.0)
        self.env['stock.quant']._update_reserved_quantity(self.product,self.stock_location,2.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),0.0)
        self.env['stock.quant']._update_reserved_quantity(self.product,self.stock_location,-2.0,strict=True)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),2.0)
        self.env['stock.quant']._update_available_quantity(self.product,self.stock_location,-2.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,self.stock_location),0.0)
        self.env['stock.quant']._update_available_quantity(self.product,pack_location,2.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product,pack_location),2.0)

    deftest_mix_tracked_untracked_1(self):
        lot1=self.env['stock.production.lot'].create({
            'name':'lot1',
            'product_id':self.product_serial.id,
            'company_id':self.env.company.id,
        })

        #addonetracked,oneuntracked
        self.env['stock.quant']._update_available_quantity(self.product_serial,self.stock_location,1.0)
        self.env['stock.quant']._update_available_quantity(self.product_serial,self.stock_location,1.0,lot_id=lot1)

        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product_serial,self.stock_location),2.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product_serial,self.stock_location,strict=True),1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product_serial,self.stock_location,lot_id=lot1),2.0)

        self.env['stock.quant']._update_reserved_quantity(self.product_serial,self.stock_location,1.0,lot_id=lot1,strict=True)

        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product_serial,self.stock_location),1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product_serial,self.stock_location,strict=True),1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product_serial,self.stock_location,lot_id=lot1),1.0)

        self.env['stock.quant']._update_reserved_quantity(self.product_serial,self.stock_location,-1.0,lot_id=lot1,strict=True)

        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product_serial,self.stock_location),2.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product_serial,self.stock_location,strict=True),1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product_serial,self.stock_location,lot_id=lot1),2.0)

        withself.assertRaises(RedirectWarning):
            self.env['stock.quant']._update_reserved_quantity(self.product_serial,self.stock_location,-1.0,strict=True)

        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product_serial,self.stock_location),2.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product_serial,self.stock_location,strict=True),1.0)
        self.assertEqual(self.env['stock.quant']._get_available_quantity(self.product_serial,self.stock_location,lot_id=lot1),2.0)

    deftest_access_rights_1(self):
        """Directlyupdatethequantwithauserwithorwithoutstockaccessrightssouldraise
        anAccessError.
        """
        quant=self.env['stock.quant'].create({
            'product_id':self.product.id,
            'location_id':self.stock_location.id,
            'quantity':1.0,
        })
        self.env=self.env(user=self.demo_user)
        withself.assertRaises(AccessError):
            self.env['stock.quant'].create({
                'product_id':self.product.id,
                'location_id':self.stock_location.id,
                'quantity':1.0,
            })
        withself.assertRaises(AccessError):
            quant.with_user(self.demo_user).write({'quantity':2.0})
        withself.assertRaises(UserError):
            quant.with_user(self.demo_user).unlink()

        self.env=self.env(user=self.stock_user)
        withself.assertRaises(AccessError):
            self.env['stock.quant'].create({
                'product_id':self.product.id,
                'location_id':self.stock_location.id,
                'quantity':1.0,
            })
        withself.assertRaises(AccessError):
            quant.with_user(self.demo_user).write({'quantity':2.0})
        withself.assertRaises(UserError):
            quant.with_user(self.demo_user).unlink()

    deftest_in_date_1(self):
        """Checkthatnoincomingdateissetwhenupdatingthequantityofanuntrackedquant.
        """
        quantity,in_date=self.env['stock.quant']._update_available_quantity(self.product,self.stock_location,1.0)
        self.assertEqual(quantity,1)
        self.assertNotEqual(in_date,None)

    deftest_in_date_1b(self):
        self.env['stock.quant'].create({
            'product_id':self.product.id,
            'location_id':self.stock_location.id,
            'quantity':1.0,
        })
        quantity,in_date=self.env['stock.quant']._update_available_quantity(self.product,self.stock_location,2.0)
        self.assertEqual(quantity,3)
        self.assertNotEqual(in_date,None)

    deftest_in_date_2(self):
        """Checkthatanincomingdateiscorrectlysetwhenupdatingthequantityofatracked
        quant.
        """
        lot1=self.env['stock.production.lot'].create({
            'name':'lot1',
            'product_id':self.product_serial.id,
            'company_id':self.env.company.id,
        })
        quantity,in_date=self.env['stock.quant']._update_available_quantity(self.product_serial,self.stock_location,1.0,lot_id=lot1)
        self.assertEqual(quantity,1)
        self.assertNotEqual(in_date,None)

    deftest_in_date_3(self):
        """CheckthattheFIFOstrategiescorrectlyapplieswhenyouhavemultiplelotreceived
        atdifferenttimesforatrackedproduct.
        """
        lot1=self.env['stock.production.lot'].create({
            'name':'lot1',
            'product_id':self.product_serial.id,
            'company_id':self.env.company.id,
        })
        lot2=self.env['stock.production.lot'].create({
            'name':'lot2',
            'product_id':self.product_serial.id,
            'company_id':self.env.company.id,
        })
        in_date_lot1=datetime.now()
        in_date_lot2=datetime.now()-timedelta(days=5)
        self.env['stock.quant']._update_available_quantity(self.product_serial,self.stock_location,1.0,lot_id=lot1,in_date=in_date_lot1)
        self.env['stock.quant']._update_available_quantity(self.product_serial,self.stock_location,1.0,lot_id=lot2,in_date=in_date_lot2)

        quants=self.env['stock.quant']._update_reserved_quantity(self.product_serial,self.stock_location,1)

        #DefaultremovalstrategyisFIFO,solot2shouldbereceivedasitwasreceivedearlier.
        self.assertEqual(quants[0][0].lot_id.id,lot2.id)

    deftest_in_date_4(self):
        """CheckthattheLIFOstrategiescorrectlyapplieswhenyouhavemultiplelotreceived
        atdifferenttimesforatrackedproduct.
        """
        lifo_strategy=self.env['product.removal'].search([('method','=','lifo')])
        self.stock_location.removal_strategy_id=lifo_strategy
        lot1=self.env['stock.production.lot'].create({
            'name':'lot1',
            'product_id':self.product_serial.id,
            'company_id':self.env.company.id,
        })
        lot2=self.env['stock.production.lot'].create({
            'name':'lot2',
            'product_id':self.product_serial.id,
            'company_id':self.env.company.id,
        })
        in_date_lot1=datetime.now()
        in_date_lot2=datetime.now()-timedelta(days=5)
        self.env['stock.quant']._update_available_quantity(self.product_serial,self.stock_location,1.0,lot_id=lot1,in_date=in_date_lot1)
        self.env['stock.quant']._update_available_quantity(self.product_serial,self.stock_location,1.0,lot_id=lot2,in_date=in_date_lot2)

        quants=self.env['stock.quant']._update_reserved_quantity(self.product_serial,self.stock_location,1)

        #RemovalstrategyisLIFO,solot1shouldbereceivedasitwasreceivedlater.
        self.assertEqual(quants[0][0].lot_id.id,lot1.id)

    deftest_in_date_4b(self):
        """CheckforLIFOandmaxwith/withoutin_datethatithandlestheLIFONULLSLASTwell
        """
        stock_location1=self.env['stock.location'].create({
            'name':'Shelf1',
            'location_id':self.stock_location.id
        })
        stock_location2=self.env['stock.location'].create({
            'name':'Shelf2',
            'location_id':self.stock_location.id
        })
        lifo_strategy=self.env['product.removal'].search([('method','=','lifo')])
        self.stock_location.removal_strategy_id=lifo_strategy

        self.env['stock.quant'].create({
            'product_id':self.product_serial.id,
            'location_id':stock_location1.id,
            'quantity':1.0,
        })

        in_date_location2=datetime.now()
        self.env['stock.quant']._update_available_quantity(self.product_serial,stock_location2,1.0,in_date=in_date_location2)

        quants=self.env['stock.quant']._update_reserved_quantity(self.product_serial,self.stock_location,1)

        #RemovalstrategyisLIFO,sotheonewithdateisthemostrecentoneandshouldbeselected
        self.assertEqual(quants[0][0].location_id.id,stock_location2.id)

    deftest_in_date_5(self):
        """Receivethesamelotatdifferenttimes,oncethey'reinthesamelocation,thequants
        aremergedandonlytheearliestincomingdateiskept.
        """
        lot1=self.env['stock.production.lot'].create({
            'name':'lot1',
            'product_id':self.product_lot.id,
            'company_id':self.env.company.id,
        })

        fromflectra.fieldsimportDatetime
        in_date1=Datetime.now()
        self.env['stock.quant']._update_available_quantity(self.product_lot,self.stock_location,1.0,lot_id=lot1,in_date=in_date1)

        quant=self.env['stock.quant'].search([
            ('product_id','=',self.product_lot.id),
            ('location_id','=',self.stock_location.id),
        ])
        self.assertEqual(len(quant),1)
        self.assertEqual(quant.quantity,1)
        self.assertEqual(quant.lot_id.id,lot1.id)
        self.assertEqual(quant.in_date,in_date1)

        in_date2=Datetime.now()-timedelta(days=5)
        self.env['stock.quant']._update_available_quantity(self.product_lot,self.stock_location,1.0,lot_id=lot1,in_date=in_date2)

        quant=self.env['stock.quant'].search([
            ('product_id','=',self.product_lot.id),
            ('location_id','=',self.stock_location.id),
        ])
        self.assertEqual(len(quant),1)
        self.assertEqual(quant.quantity,2)
        self.assertEqual(quant.lot_id.id,lot1.id)
        self.assertEqual(quant.in_date,in_date2)

    deftest_in_date_6(self):
        """
        OnePinstock,Pisdelivered.Lateron,astockadjustementaddsoneP.Thistestchecks
        thedatevalueoftherelatedquant
        """
        self.env['stock.quant']._update_available_quantity(self.product,self.stock_location,1.0)

        move=self.env['stock.move'].create({
            'name':'OUT1product',
            'product_id':self.product.id,
            'product_uom_qty':1,
            'product_uom':self.product.uom_id.id,
            'location_id':self.stock_location.id,
            'location_dest_id':self.ref('stock.stock_location_customers'),
        })
        move._action_confirm()
        move._action_assign()
        move.quantity_done=1
        move._action_done()

        tomorrow=fields.Datetime.now()+timedelta(days=1)
        withpatch.object(fields.Datetime,'now',lambda:tomorrow):
            inventory=self.env['stock.inventory'].create({
                'name':'add1xproduct',
                'location_ids':[(4,self.stock_location.id)],
                'product_ids':[(4,self.product.id)],
            })
            inventory.action_start()
            self.env['stock.inventory.line'].create({
                'inventory_id':inventory.id,
                'product_id':self.product.id,
                'product_uom_id':self.product.uom_id.id,
                'product_qty':1,
                'location_id':self.stock_location.id,
            })
            inventory._action_done()
            quant=self.env['stock.quant'].search([('product_id','=',self.product.id),('location_id','=',self.stock_location.id),('quantity','>',0)])
            self.assertEqual(quant.in_date,tomorrow)

    deftest_unpack_and_quants_merging(self):
        """
        Whenunpackingapackage,iftherearealreadysomequantitiesofthe
        packedproductinthestock,thequantoftheonhandquantityandthe
        oneofthepackageshouldbemerged
        """
        stock_location=self.env['stock.warehouse'].search([],limit=1).lot_stock_id
        supplier_location=self.env.ref('stock.stock_location_suppliers')
        picking_type_in=self.env.ref('stock.picking_type_in')

        self.env['stock.quant']._update_available_quantity(self.product,stock_location,1.0)

        picking=self.env['stock.picking'].create({
            'picking_type_id':picking_type_in.id,
            'location_id':supplier_location.id,
            'location_dest_id':stock_location.id,
            'move_lines':[(0,0,{
                'name':'In10x%s'%self.product.name,
                'product_id':self.product.id,
                'location_id':supplier_location.id,
                'location_dest_id':stock_location.id,
                'product_uom_qty':10,
                'product_uom':self.product.uom_id.id,
            })],
        })
        picking.action_confirm()

        package=self.env['stock.quant.package'].create({
            'name':'SuperPackage',
        })
        picking.move_lines.move_line_ids.write({
            'qty_done':10,
            'result_package_id':package.id,
        })
        picking.button_validate()

        package.unpack()

        quant=self.env['stock.quant'].search([('product_id','=',self.product.id),('on_hand','=',True)])
        self.assertEqual(len(quant),1)
        #ThequantsmergingisprocessedthankstoaSQLquery(seeStockQuant._merge_quants).
        #Atthatpoint,theORMisnotawareofthenewvalue.Soweneedtoinvalidatethe
        #cachetoensurethatthevaluewillbethenewest
        quant.invalidate_cache(fnames=['quantity'],ids=quant.ids)
        self.assertEqual(quant.quantity,11)
