#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromdatetimeimporttimedelta

fromflectraimportfields
fromflectra.testsimporttagged
fromflectra.addons.sale_purchase.tests.commonimportTestCommonSalePurchaseNoChart


@tagged('post_install','-at_install')
classTestLeadTime(TestCommonSalePurchaseNoChart):

    @classmethod
    defsetUpClass(cls):
        super(TestLeadTime,cls).setUpClass()

        cls.buy_route=cls.env.ref('purchase_stock.route_warehouse0_buy')
        cls.mto_route=cls.env.ref('stock.route_warehouse0_mto')
        cls.mto_route.active=True
        cls.vendor=cls.env['res.partner'].create({'name':'TheEmperor'})
        cls.user_salesperson=cls.env['res.users'].with_context(no_reset_password=True).create({
            'name':'LeGrandHorus',
            'login':'grand.horus',
            'email':'grand.horus@chansonbelge.dz',
        })


    deftest_supplier_lead_time(self):
        """Basicstockconfigurationandasupplierwithaminimumqtyandaleadtime"""

        self.env.user.company_id.po_lead=7
        seller=self.env['product.supplierinfo'].create({
            'name':self.vendor.id,
            'min_qty':1,
            'price':10,
            'date_start':fields.Date.today()-timedelta(days=1),
        })

        product=self.env['product.product'].create({
            'name':'corpsestarch',
            'type':'product',
            'seller_ids':[(6,0,seller.ids)],
            'route_ids':[(6,0,(self.mto_route+self.buy_route).ids)],
        })

        so=self.env['sale.order'].with_user(self.user_salesperson).create({
            'partner_id':self.partner_a.id,
            'user_id':self.user_salesperson.id,
        })
        self.env['sale.order.line'].create({
            'name':product.name,
            'product_id':product.id,
            'product_uom_qty':1,
            'product_uom':product.uom_id.id,
            'price_unit':product.list_price,
            'tax_id':False,
            'order_id':so.id,
        })
        so.action_confirm()

        po=self.env['purchase.order'].search([('partner_id','=',self.vendor.id)])
        self.assertEqual(po.order_line.price_unit,seller.price)
