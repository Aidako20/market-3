#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.addons.base.tests.commonimportHttpCaseWithUserPortal
fromflectra.testsimporttagged


@tagged('post_install','-at_install')
classTestSaleSignature(HttpCaseWithUserPortal):
    deftest_01_portal_sale_signature_tour(self):
        """ThegoalofthistestistomakesuretheportalusercansignSO."""

        portal_user=self.partner_portal
        #createaSOtobesigned
        sales_order=self.env['sale.order'].create({
            'name':'testSO',
            'partner_id':portal_user.id,
            'state':'sent',
            'require_payment':False,
        })
        self.env['sale.order.line'].create({
            'order_id':sales_order.id,
            'product_id':self.env['product.product'].create({'name':'Aproduct'}).id,
        })

        #mustbesenttotheusersohecanseeit
        email_act=sales_order.action_quotation_send()
        email_ctx=email_act.get('context',{})
        sales_order.with_context(**email_ctx).message_post_with_template(email_ctx.get('default_template_id'))

        self.start_tour("/",'sale_signature',login="portal")
