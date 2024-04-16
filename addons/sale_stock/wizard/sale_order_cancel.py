#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classSaleOrderCancel(models.TransientModel):
    _inherit='sale.order.cancel'

    display_delivery_alert=fields.Boolean('DeliveryAlert',compute='_compute_display_delivery_alert')

    @api.depends('order_id')
    def_compute_display_delivery_alert(self):
        forwizardinself:
            wizard.display_delivery_alert=bool(any(picking.state=='done'forpickinginwizard.order_id.picking_ids))
