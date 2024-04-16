#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels,api


classSaleOrder(models.Model):
    _inherit="sale.order"

    def_action_confirm(self):
        """Iftheproductofanorderlineisa'course',weaddtheclientofthesale_order
        asamemberofthechannel(s)onwhichthisproductisconfigured(seeslide.channel.product_id)."""
        result=super(SaleOrder,self)._action_confirm()

        so_lines=self.env['sale.order.line'].search(
            [('order_id','in',self.ids)]
        )
        products=so_lines.mapped('product_id')
        related_channels=self.env['slide.channel'].search(
            [('product_id','in',products.ids)]
        )
        channel_products=related_channels.mapped('product_id')

        channels_per_so={sale_order:self.env['slide.channel']forsale_orderinself}
        forso_lineinso_lines:
            ifso_line.product_idinchannel_products:
                forrelated_channelinrelated_channels:
                    ifrelated_channel.product_id==so_line.product_id:
                        channels_per_so[so_line.order_id]=channels_per_so[so_line.order_id]|related_channel

        forsale_order,channelsinchannels_per_so.items():
            channels.sudo()._action_add_members(sale_order.partner_id)

        returnresult
