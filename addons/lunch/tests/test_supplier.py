#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importpytz

fromdatetimeimportdatetime
fromunittest.mockimportpatch

fromflectraimportfields

fromflectra.addons.lunch.tests.commonimportTestsCommon


classTestSupplier(TestsCommon):
    defsetUp(self):
        super(TestSupplier,self).setUp()

        self.monday_1am=datetime(2018,10,29,1,0,0)
        self.monday_10am=datetime(2018,10,29,10,0,0)
        self.monday_1pm=datetime(2018,10,29,13,0,0)
        self.monday_8pm=datetime(2018,10,29,20,0,0)

        self.saturday_3am=datetime(2018,11,3,3,0,0)
        self.saturday_10am=datetime(2018,11,3,10,0,0)
        self.saturday_1pm=datetime(2018,11,3,13,0,0)
        self.saturday_8pm=datetime(2018,11,3,20,0,0)

    deftest_compute_available_today(self):
        tests=[(self.monday_1am,True),(self.monday_10am,True),
                 (self.monday_1pm,True),(self.monday_8pm,True),
                 (self.saturday_3am,False),(self.saturday_10am,False),
                 (self.saturday_1pm,False),(self.saturday_8pm,False)]

        forvalue,resultintests:
            withpatch.object(fields.Datetime,'now',return_value=value)as_:
                assertself.supplier_pizza_inn.available_today==result,\
                    'supplierpizzainnshould%sconsideredavailableon%s'%('be'ifresultelse'notbe',value)

            self.env['lunch.supplier'].invalidate_cache(['available_today'],[self.supplier_pizza_inn.id])

    deftest_search_available_today(self):
        '''
            Thistestchecksthat_search_available_todayreturnsavaliddomain
        '''
        self.env.user.tz='Europe/Brussels'
        Supplier=self.env['lunch.supplier']

        tests=[(self.monday_1am,1.0,'monday'),(self.monday_10am,10.0,'monday'),
                 (self.monday_1pm,13.0,'monday'),(self.monday_8pm,20.0,'monday'),
                 (self.saturday_3am,3.0,'saturday'),(self.saturday_10am,10.0,'saturday'),
                 (self.saturday_1pm,13.0,'saturday'),(self.saturday_8pm,20.0,'saturday')]

        #Itshouldreturnanemptydomainifwecomparetovaluesotherthandatetime
        assertSupplier._search_available_today('>',7)==[]
        assertSupplier._search_available_today('>',True)==[]

        forvalue,rvalue,daynameintests:
            withpatch.object(fields.Datetime,'now',return_value=value)as_:
                assertSupplier._search_available_today('=',True)==['&','|',('recurrency_end_date','=',False),
                        ('recurrency_end_date','>',value.replace(tzinfo=pytz.UTC).astimezone(pytz.timezone(self.env.user.tz))),
                        ('recurrency_%s'%(dayname),'=',True)],\
                        'Wrongdomaingeneratedforvalues(%s,%s)'%(value,rvalue)

        withpatch.object(fields.Datetime,'now',return_value=self.monday_10am)as_:
            assertself.supplier_pizza_inninSupplier.search([('available_today','=',True)])

    deftest_auto_email_send(self):
        withpatch.object(fields.Datetime,'now',return_value=self.monday_1pm)as_:
            withpatch.object(fields.Date,'today',return_value=self.monday_1pm.date())as_:
                withpatch.object(fields.Date,'context_today',return_value=self.monday_1pm.date())as_:
                    line=self.env['lunch.order'].create({
                        'product_id':self.product_pizza.id,
                        'date':self.monday_1pm.date()
                    })

                    line.action_order()
                    assertline.state=='ordered'

                    self.supplier_pizza_inn._auto_email_send()

                    assertline.state=='confirmed'

                    line=self.env['lunch.order'].create({
                        'product_id':self.product_pizza.id,
                        'topping_ids_1':[(6,0,[self.topping_olives.id])],
                        'date':self.monday_1pm.date()
                    })
                    line2=self.env['lunch.order'].create({
                        'product_id':self.product_sandwich_tuna.id,
                        'date':self.monday_1pm.date()
                    })

                    (line|line2).action_order()
                    assertline.state=='ordered'
                    assertline2.state=='ordered'

                    self.supplier_pizza_inn._auto_email_send()

                    assertline.state=='confirmed'
                    assertline2.state=='ordered'

                    line_1=self.env['lunch.order'].create({
                        'product_id':self.product_pizza.id,
                        'quantity':2,
                        'date':self.monday_1pm.date()
                    })

                    line_2=self.env['lunch.order'].create({
                        'product_id':self.product_pizza.id,
                        'topping_ids_1':[(6,0,[self.topping_olives.id])],
                        'date':self.monday_1pm.date()
                    })

                    line_3=self.env['lunch.order'].create({
                        'product_id':self.product_sandwich_tuna.id,
                        'quantity':2,
                        'date':self.monday_1pm.date()
                    })

                    (line_1|line_2|line_3).action_order()

                    assertall(line.state=='ordered'forlinein[line_1,line_2,line_3])

                    self.supplier_pizza_inn._auto_email_send()
