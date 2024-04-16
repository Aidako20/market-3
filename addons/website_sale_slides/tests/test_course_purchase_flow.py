#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.addons.website_slides.testsimportcommon


classTestCoursePurchaseFlow(common.SlidesCase):
    @classmethod
    defsetUpClass(cls):
        super().setUpClass()
        cls.user_salesman=cls.env['res.users'].create({
            'name':'salesman',
            'login':'salesman',
            'email':'salesman007@example.com',
            'groups_id':[(6,0,cls.env.ref('sales_team.group_sale_salesman').ids)],
        })

    deftest_course_purchase_flow(self):
        #Step1:createacourseproductandassignitto2slide.channels
        course_product=self.env['product.product'].create({
            'name':"CourseProduct",
            'standard_price':100,
            'list_price':150,
            'type':'service',
            'invoice_policy':'order',
            'is_published':True,
        })

        self.channel.write({
            'enroll':'payment',
            'product_id':course_product.id
        })

        self.channel_2=self.env['slide.channel'].with_user(self.user_officer).create({
            'name':'TestChannel',
            'enroll':'payment',
            'product_id':course_product.id,
            'is_published':True,
        })

        #Step2:createasale_orderwiththecourseproduct
        sale_order=self.env['sale.order'].create({
            'partner_id':self.customer.id,
            'order_line':[
                (0,0,{
                    'name':course_product.name,
                    'product_id':course_product.id,
                    'product_uom_qty':1,
                    'price_unit':course_product.list_price,
                })
            ],
        })

        sale_order.action_confirm()

        #Step3:checkthatthecustomerisnowamemberofbothchannel
        self.assertIn(self.customer,self.channel.partner_ids)
        self.assertIn(self.customer,self.channel_2.partner_ids)

        #Step4:Sametestassalesman
        salesman_sale_order=self.env['sale.order'].with_user(self.user_salesman).create({
            'partner_id':self.user_portal.partner_id.id,
            'order_line':[
                (0,0,{
                    'name':course_product.name,
                    'product_id':course_product.id,
                    'product_uom_qty':1,
                    'price_unit':course_product.list_price,
                })
            ],
        })

        salesman_sale_order.action_confirm()

        self.assertIn(self.user_portal.partner_id,self.channel.partner_ids)
        self.assertIn(self.user_portal.partner_id,self.channel_2.partner_ids)
