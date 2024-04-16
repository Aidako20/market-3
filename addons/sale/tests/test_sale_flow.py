#-*-coding:utf-8-*-
fromflectra.addons.sale.tests.commonimportTestSaleCommonBase


classTestSaleFlow(TestSaleCommonBase):
    '''Testrunningat-installtotestflowsindependentlytoothermodules,e.g.'sale_stock'.'''

    @classmethod
    defsetUpClass(cls):
        super().setUpClass()

        user=cls.env['res.users'].create({
            'name':'BecauseIamsaleman!',
            'login':'saleman',
            'groups_id':[(6,0,cls.env.user.groups_id.ids),(4,cls.env.ref('account.group_account_user').id)],
        })
        user.partner_id.email='saleman@test.com'

        #Shadowthecurrentenvironment/cursorwiththenewlycreateduser.
        cls.env=cls.env(user=user)
        cls.cr=cls.env.cr

        cls.company=cls.env['res.company'].create({
            'name':'TestCompany',
            'currency_id':cls.env.ref('base.USD').id,
        })
        cls.company_data=cls.setup_sale_configuration_for_company(cls.company)

        cls.partner_a=cls.env['res.partner'].create({
            'name':'partner_a',
            'company_id':False,
        })

        cls.analytic_account=cls.env['account.analytic.account'].create({
            'name':'Testanalytic_account',
            'code':'analytic_account',
            'company_id':cls.company.id,
            'partner_id':cls.partner_a.id
        })

        user.company_ids|=cls.company
        user.company_id=cls.company

    deftest_qty_delivered(self):
        '''Test'qty_delivered'at-installtoavoidachangeinthebehaviorwhen'sale_stock'isinstalled.'''

        sale_order=self.env['sale.order'].with_context(mail_notrack=True,mail_create_nolog=True).create({
            'partner_id':self.partner_a.id,
            'partner_invoice_id':self.partner_a.id,
            'partner_shipping_id':self.partner_a.id,
            'analytic_account_id':self.analytic_account.id,
            'pricelist_id':self.company_data['default_pricelist'].id,
            'order_line':[
                (0,0,{
                    'name':self.company_data['product_order_cost'].name,
                    'product_id':self.company_data['product_order_cost'].id,
                    'product_uom_qty':2,
                    'qty_delivered':1,
                    'product_uom':self.company_data['product_order_cost'].uom_id.id,
                    'price_unit':self.company_data['product_order_cost'].list_price,
                }),
                (0,0,{
                    'name':self.company_data['product_delivery_cost'].name,
                    'product_id':self.company_data['product_delivery_cost'].id,
                    'product_uom_qty':4,
                    'qty_delivered':1,
                    'product_uom':self.company_data['product_delivery_cost'].uom_id.id,
                    'price_unit':self.company_data['product_delivery_cost'].list_price,
                }),
            ],
        })
        forlineinsale_order.order_line:
            line.product_id_change()

        sale_order.onchange_partner_id()
        sale_order._compute_tax_id()
        sale_order.action_confirm()

        self.assertRecordValues(sale_order.order_line,[
            {'qty_delivered':1.0},
            {'qty_delivered':1.0},
        ])
