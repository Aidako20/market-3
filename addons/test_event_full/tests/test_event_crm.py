#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.addons.test_event_full.tests.commonimportTestEventFullCommon
fromflectra.testsimportusers


classTestEventCrm(TestEventFullCommon):

    @classmethod
    defsetUpClass(cls):
        super(TestEventCrm,cls).setUpClass()

        cls.TICKET1_COUNT,cls.TICKET2_COUNT=3,1
        ticket1=cls.event_0.event_ticket_ids[0]
        ticket2=cls.event_0.event_ticket_ids[1]

        #PREPARESODATA
        #------------------------------------------------------------

        #addingsometicketstoSO
        cls.customer_so.write({
            'order_line':[
                (0,0,{
                    'event_id':cls.event_0.id,
                    'event_ticket_id':ticket1.id,
                    'product_id':ticket1.product_id.id,
                    'product_uom_qty':cls.TICKET1_COUNT,
                }),(0,0,{
                    'event_id':cls.event_0.id,
                    'event_ticket_id':ticket2.id,
                    'product_id':ticket2.product_id.id,
                    'product_uom_qty':cls.TICKET2_COUNT,
                    'price_unit':50,
                })
            ]
        })

    @users('user_sales_salesman')
    deftest_event_crm_sale_customer(self):
        """TestaSOwitharealcustomersetonit,checkpartnerpropagation
        aswellasgroup-basedleadupdate."""
        customer_so=self.env['sale.order'].browse(self.customer_so.id)

        #addingsometicketstoSO
        t1_reg_vals=[
            dict(customer_data,
                 partner_id=customer_so.partner_id.id,
                 sale_order_line_id=customer_so.order_line[0].id)
            forcustomer_datainself.website_customer_data[:self.TICKET1_COUNT]
        ]
        t1_registrations=self.env['event.registration'].create(t1_reg_vals)

        #checkeffect:registrations,leads
        self.assertEqual(self.event_0.registration_ids,t1_registrations)
        self.assertEqual(len(self.test_rule_order.lead_ids),1)
        self.assertEqual(self.test_rule_order_done.lead_ids,self.env['crm.lead'])
        #checkleadconvertedbasedonregistrations
        self.assertLeadConvertion(self.test_rule_order,t1_registrations,partner=customer_so.partner_id)

        #SOisconfirmed->missingregistrationsshouldbeautomaticallyadded
        #andaddedtotheleadaspartofthesamegroup
        customer_so.action_confirm()
        self.assertEqual(customer_so.state,'sale')
        self.assertEqual(len(self.event_0.registration_ids),self.TICKET1_COUNT+self.TICKET2_COUNT)
        self.assertEqual(len(self.test_rule_order.lead_ids),1) #nonewleadcreated
        self.assertEqual(self.test_rule_order_done.lead_ids,self.env['crm.lead']) #thisonestillnottriggered

        #checkexistingleadhasbeenupdatedwithnewregistrations
        self.assertLeadConvertion(self.test_rule_order,self.event_0.registration_ids,partner=customer_so.partner_id)

        #Confirmregistrations->triggerthe"DONE"rule,onenewleadlinkedtoall
        #eventregistrationscreatedinthistestasallbelongtothesameSO
        self.event_0.registration_ids.write({'state':'done'})
        self.assertLeadConvertion(self.test_rule_order_done,self.event_0.registration_ids,partner=customer_so.partner_id)

    @users('user_sales_salesman')
    deftest_event_crm_sale_mixed_group(self):
        """Testamixedsaleorderlinecreation.Thisshouldnothappeninacustomer
        usecasebutshouldbesupportedbythecode."""
        public_partner=self.env.ref('base.public_partner')
        public_so=self.env['sale.order'].create({
            'partner_id':public_partner.id,
            'order_line':[
                (0,0,{
                    'event_id':self.event_0.id,
                    'event_ticket_id':self.event_0.event_ticket_ids[0].id,
                    'product_id':self.event_0.event_ticket_ids[0].product_id.id,
                    'product_uom_qty':2,
                })
            ]
        })
        customer_so=self.env['sale.order'].browse(self.customer_so.id)

        #makeamulti-SOcreate
        mixed_reg_vals=[
            dict(self.website_customer_data[0],
                 partner_id=customer_so.partner_id.id,
                 sale_order_line_id=customer_so.order_line[0].id),
            dict(self.website_customer_data[1],
                 partner_id=customer_so.partner_id.id,
                 sale_order_line_id=customer_so.order_line[0].id),
            dict(self.website_customer_data[2],
                 partner_id=public_so.partner_id.id,
                 sale_order_line_id=public_so.order_line[0].id),
            dict(self.website_customer_data[3],
                 partner_id=public_so.partner_id.id,
                 sale_order_line_id=public_so.order_line[0].id),
        ]
        self.env['event.registration'].create(mixed_reg_vals)

        public_regs=self.event_0.registration_ids.filtered(lambdareg:reg.sale_order_id==public_so)
        self.assertEqual(len(public_regs),2)
        customer_regs=self.event_0.registration_ids.filtered(lambdareg:reg.sale_order_id==customer_so)
        self.assertEqual(len(customer_regs),2)
        self.assertLeadConvertion(self.test_rule_order,public_regs,partner=None)
        self.assertLeadConvertion(self.test_rule_order,customer_regs,partner=customer_so.partner_id)

    @users('user_sales_salesman')
    deftest_event_crm_sale_public(self):
        """TestaSOwithapublicpartneronit,thenupdatedwhenSOisconfirmed.
        Thissomehowsimulatesasimplifiedwebsite_event_saleflow."""
        public_partner=self.env.ref('base.public_partner')
        customer_so=self.env['sale.order'].browse(self.customer_so.id)
        customer_so.write({'partner_id':public_partner.id})

        #addingsometicketstoSO
        t1_reg_vals=[
            dict(customer_data,
                 partner_id=public_partner.id,
                 sale_order_line_id=customer_so.order_line[0].id)
            forcustomer_datainself.website_customer_data[:self.TICKET1_COUNT]
        ]
        t1_registrations=self.env['event.registration'].create(t1_reg_vals)
        self.assertEqual(self.event_0.registration_ids,t1_registrations)

        #checkleadconvertedbasedonregistrations
        self.assertLeadConvertion(self.test_rule_order,t1_registrations,partner=None)

        #SOisconfirmed->missingregistrationsshouldbeautomaticallyadded
        #BUTaspublicuser->noemail->nottakenintoaccountbyrule
        customer_so.action_confirm()
        self.assertEqual(customer_so.state,'sale')
        self.assertEqual(len(self.event_0.registration_ids),self.TICKET1_COUNT+self.TICKET2_COUNT)
        self.assertLeadConvertion(self.test_rule_order,t1_registrations,partner=None)

        #SOhasacustomerset->maincontactofleadisupdatedaccordingly
        customer_so.write({'partner_id':self.event_customer.id})
        self.assertLeadConvertion(self.test_rule_order,t1_registrations,partner=self.event_customer)
