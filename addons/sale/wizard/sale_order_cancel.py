#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classSaleOrderCancel(models.TransientModel):
    _name='sale.order.cancel'
    _description="SalesOrderCancel"

    order_id=fields.Many2one('sale.order',string='SaleOrder',required=True,ondelete='cascade')
    display_invoice_alert=fields.Boolean('InvoiceAlert',compute='_compute_display_invoice_alert')

    @api.depends('order_id')
    def_compute_display_invoice_alert(self):
        forwizardinself:
            wizard.display_invoice_alert=bool(wizard.order_id.invoice_ids.filtered(lambdainv:inv.state=='draft'))

    defaction_cancel(self):
        returnself.order_id.with_context({'disable_cancel_warning':True}).action_cancel()
