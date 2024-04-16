#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.testsimportcommon,Form


classTestProcurementException(common.TransactionCase):

    deftest_00_procurement_exception(self):

        res_partner_2=self.env['res.partner'].create({'name':'MyTestPartner'})
        res_partner_address=self.env['res.partner'].create({
            'name':'MyTestPartnerAddress',
            'parent_id':res_partner_2.id,
        })

        #Icreateaproductwithnosupplierdefineforit.
        product_form=Form(self.env['product.product'])
        product_form.name='productwithnoseller'
        product_form.lst_price=20.00
        product_form.categ_id=self.env.ref('product.product_category_1')
        product_with_no_seller=product_form.save()

        product_with_no_seller.standard_price=70.0

        #Icreateasalesorderwiththisproductwithroutedropship.
        so_form=Form(self.env['sale.order'])
        so_form.partner_id=res_partner_2
        so_form.partner_invoice_id=res_partner_address
        so_form.partner_shipping_id=res_partner_address
        so_form.payment_term_id=self.env.ref('account.account_payment_term_end_following_month')
        withso_form.order_line.new()asline:
            line.product_id=product_with_no_seller
            line.product_uom_qty=3
            line.route_id=self.env.ref('stock_dropshipping.route_drop_shipping')
        sale_order_route_dropship01=so_form.save()

        #Iconfirmthesalesorder,butitwillraiseanerror
        withself.assertRaises(Exception):
            sale_order_route_dropship01.action_confirm()

        #Isettheatleastonesupplierontheproduct.
        withForm(product_with_no_seller)asf:
            withf.seller_ids.new()asseller:
                seller.delay=1
                seller.name=res_partner_2
                seller.min_qty=2.0

        #Iconfirmthesalesorder,noerrorthistime
        sale_order_route_dropship01.action_confirm()

        #Icheckapurchasequotationwascreated.
        purchase=self.env['purchase.order.line'].search([
            ('sale_line_id','=',sale_order_route_dropship01.order_line.ids[0])]).order_id

        self.assertTrue(purchase,'NoPurchaseQuotationiscreated')
