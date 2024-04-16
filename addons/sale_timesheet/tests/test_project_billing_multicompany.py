#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.addons.sale_timesheet.tests.commonimportTestCommonSaleTimesheet
fromflectra.testsimporttagged


@tagged('-at_install','post_install')
classTestProjectBillingMulticompany(TestCommonSaleTimesheet):

    @classmethod
    defsetUpClass(cls,chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

        Project=cls.env['project.project'].with_context(tracking_disable=True)
        cls.project_non_billable=Project.create({
            'name':"NonBillableProject",
            'allow_timesheets':True,
            'allow_billable':True,
            'bill_type':'customer_project',
            'company_id':cls.env.company.id,
        })

    deftest_makeBillable_multiCompany(self):
        wizard=self.env['project.create.sale.order'].with_context(allowed_company_ids=[self.company_data_2['company'].id,self.env.company.id],company_id=self.company_data_2['company'].id,active_id=self.project_non_billable.id,active_model='project.project').create({
            'line_ids':[(0,0,{
                'product_id':self.product_delivery_timesheet3.id, #productcreatesnewTimesheetinnewProject
                'price_unit':self.product_delivery_timesheet3.list_price
            })],
            'partner_id':self.partner_a.id,
        })

        action=wizard.action_create_sale_order()
        sale_order=self.env['sale.order'].browse(action['res_id'])

        self.assertEqual(sale_order.company_id.id,self.project_non_billable.company_id.id,"Thecompanyonthesaleordershouldbethesameastheoneontheproject")
