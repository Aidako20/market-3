#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.testsimporttagged
fromflectra.addons.sale_purchase.tests.commonimportTestCommonSalePurchaseNoChart


@tagged('post_install','-at_install')
classTestAccessRights(TestCommonSalePurchaseNoChart):

    @classmethod
    defsetUpClass(cls):
        super(TestAccessRights,cls).setUpClass()

        group_sale_user=cls.env.ref('sales_team.group_sale_salesman')

        cls.user_salesperson=cls.env['res.users'].with_context(no_reset_password=True).create({
            'name':'LeGrandJojoUser',
            'login':'grand.jojo',
            'email':'grand.jojo@chansonbelge.com',
            'groups_id':[(6,0,[group_sale_user.id])]
        })

    deftest_access_saleperson_decreases_qty(self):
        """
        SupposeauserwhohasnorightonPO
        SupposeaPOlinkedtoaSO
        TheuserdecreasestheqtyontheSO
        Thistestensuresthatanactivity(warning)isaddedtothePO
        """
        mto_route=self.env.ref('stock.route_warehouse0_mto')
        buy_route=self.env.ref('purchase_stock.route_warehouse0_buy')
        mto_route.active=True

        vendor=self.env['res.partner'].create({'name':'vendor'})
        seller=self.env['product.supplierinfo'].create({
            'name':vendor.id,
            'price':8,
        })

        product=self.env['product.product'].create({
            'name':'SuperProduct',
            'type':'product',
            'seller_ids':[(6,0,seller.ids)],
            'route_ids':[(6,0,(mto_route+buy_route).ids)]
        })

        so=self.env['sale.order'].with_user(self.user_salesperson).create({
            'partner_id':self.partner_a.id,
            'user_id':self.user_salesperson.id,
        })
        so_line,_=self.env['sale.order.line'].create([{
            'name':product.name,
            'product_id':product.id,
            'product_uom_qty':1,
            'product_uom':product.uom_id.id,
            'price_unit':product.list_price,
            'tax_id':False,
            'order_id':so.id,
        },{
            'name':'SuperSection',
            'display_type':'line_section',
            'order_id':so.id,
        }])

        so.action_confirm()

        po=self.env['purchase.order'].search([('partner_id','=',vendor.id)])
        po.button_confirm()

        #salespersonwritesontheSO
        so.write({
            'order_line':[(1,so_line.id,{'product_uom_qty':0.9})]
        })

        self.assertIn(so.name,po.activity_ids.note)
