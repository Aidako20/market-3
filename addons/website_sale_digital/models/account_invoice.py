#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels


classAccountInvoiceLine(models.Model):

    _inherit=['account.move.line']

    defget_digital_purchases(self):
        partner=self.env.user.partner_id

        #Getpaidinvoices
        purchases=self.sudo().search_read(
            domain=[
                ('move_id.payment_state','in',['paid','in_payment']),
                ('move_id.partner_id','=',partner.id),
                ('product_id','!=',False),
            ],
            fields=['product_id'],
        )

        #Getfreeproducts
        purchases+=self.env['sale.order.line'].sudo().search_read(
            domain=[('display_type','=',False),('order_id.partner_id','=',partner.id),'|',('price_subtotal','=',0.0),('order_id.amount_total','=',0.0)],
            fields=['product_id'],
        )

        #Ionlywantproduct_ids,butsearch_readinsistsingivingmealistof
        #(product_id:<id>,name:<productcode><template_name><attributes>)
        return[line['product_id'][0]forlineinpurchases]
