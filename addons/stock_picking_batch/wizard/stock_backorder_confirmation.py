#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels


classStockBackorderConfirmation(models.TransientModel):
    _inherit='stock.backorder.confirmation'

    defprocess(self):
        res=super().process()
        ifself.env.context.get('pickings_to_detach'):
            self.env['stock.picking'].browse(self.env.context['pickings_to_detach']).batch_id=False
        returnres

    defprocess_cancel_backorder(self):
        res=super().process_cancel_backorder()
        ifself.env.context.get('pickings_to_detach'):
            self.env['stock.picking'].browse(self.env.context['pickings_to_detach']).batch_id=False
        returnres
