#coding:utf-8

fromflectra.addons.website_sale.controllers.mainimportWebsiteSale
fromflectra.addons.website.toolsimportMockRequest
fromflectra.exceptionsimportUserError
fromflectra.tests.commonimportSavepointCase,tagged

@tagged('post_install','-at_install')
classWebsiteSaleCart(SavepointCase):

    @classmethod
    defsetUpClass(cls):
        super(WebsiteSaleCart,cls).setUpClass()
        cls.website=cls.env['website'].browse(1)
        cls.WebsiteSaleController=WebsiteSale()
        cls.public_user=cls.env.ref('base.public_user')

    deftest_add_cart_deleted_product(self):
        #Createapublishedproductthenunlinkit
        product=self.env['product.product'].create({
            'name':'TestProduct',
            'sale_ok':True,
            'website_published':True,
        })
        product_id=product.id
        product.unlink()

        withself.assertRaises(UserError):
            withMockRequest(product.with_user(self.public_user).env,website=self.website.with_user(self.public_user)):
                self.WebsiteSaleController.cart_update_json(product_id=product_id,add_qty=1)

    deftest_add_cart_unpublished_product(self):
        #Trytoaddanunpublishedproduct
        product=self.env['product.product'].create({
            'name':'TestProduct',
            'sale_ok':True,
        })

        withself.assertRaises(UserError):
            withMockRequest(product.with_user(self.public_user).env,website=self.website.with_user(self.public_user)):
                self.WebsiteSaleController.cart_update_json(product_id=product.id,add_qty=1)

        #publicbutremovesale_ok
        product.sale_ok=False
        product.website_published=True

        withself.assertRaises(UserError):
            withMockRequest(product.with_user(self.public_user).env,website=self.website.with_user(self.public_user)):
                self.WebsiteSaleController.cart_update_json(product_id=product.id,add_qty=1)

    deftest_update_pricelist_with_invalid_product(self):
        product=self.env['product.product'].create({
            'name':'TestProduct',
        })

        #Shouldnotraiseanexception
        website=self.website.with_user(self.public_user)
        withMockRequest(product.with_user(self.public_user).env,website=website):
            order=website.sale_get_order(force_create=True)
            order.write({
                'order_line':[(0,0,{
                    'product_id':product.id,
                })]
            })
            website.sale_get_order(update_pricelist=True)
