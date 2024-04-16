#-*-coding:utf-8-*-
fromdatetimeimporttimedelta

fromflectraimportfields
fromflectra.addons.stock.tests.common2importTestStockCommon
fromflectraimporttools
fromflectra.modules.moduleimportget_module_resource


classPurchaseTestCommon(TestStockCommon):

    def_create_make_procurement(self,product,product_qty,date_planned=False):
        ProcurementGroup=self.env['procurement.group']
        order_values={
            'warehouse_id':self.warehouse_1,
            'action':'pull_push',
            'date_planned':date_plannedorfields.Datetime.to_string(fields.datetime.now()+timedelta(days=10)), #10daysaddedtocurrentdateofprocurementtogetfuturescheduledateandorderdateofpurchaseorder.
            'group_id':self.env['procurement.group'],
        }
        returnProcurementGroup.run([self.env['procurement.group'].Procurement(
            product,product_qty,self.uom_unit,self.warehouse_1.lot_stock_id,
            product.name,'/',self.env.company,order_values)
        ])

    @classmethod
    defsetUpClass(cls):
        super(PurchaseTestCommon,cls).setUpClass()
        cls.env.ref('stock.route_warehouse0_mto').active=True

        cls.route_buy=cls.warehouse_1.buy_pull_id.route_id.id
        cls.route_mto=cls.warehouse_1.mto_pull_id.route_id.id

        #Updateproduct_1withtype,routeandDeliveryLeadTime
        cls.product_1.write({
            'type':'product',
            'route_ids':[(6,0,[cls.route_buy,cls.route_mto])],
            'seller_ids':[(0,0,{'name':cls.partner_1.id,'delay':5})]})

        cls.t_shirt=cls.env['product.product'].create({
            'name':'T-shirt',
            'route_ids':[(6,0,[cls.route_buy,cls.route_mto])],
            'seller_ids':[(0,0,{'name':cls.partner_1.id,'delay':5})]
        })

        #Updateproduct_2withtype,routeandDeliveryLeadTime
        cls.product_2.write({
            'type':'product',
            'route_ids':[(6,0,[cls.route_buy,cls.route_mto])],
            'seller_ids':[(0,0,{'name':cls.partner_1.id,'delay':2})]})

        cls.res_users_purchase_user=cls.env['res.users'].create({
            'company_id':cls.env.ref('base.main_company').id,
            'name':"PurchaseUser",
            'login':"pu",
            'email':"purchaseuser@yourcompany.com",
            'groups_id':[(6,0,[cls.env.ref('purchase.group_purchase_user').id])],
            })
