#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectraimportfields,models,api

classAccountMove(models.Model):
    _inherit='account.move'

    def_get_invoiced_lot_values(self):
        self.ensure_one()

        lot_values=super(AccountMove,self)._get_invoiced_lot_values()

        ifself.state=='draft':
            returnlot_values

        #usermaynothaveaccesstoPOSorders,butit'sokiftheyhave
        #accesstotheinvoice
        fororderinself.sudo().pos_order_ids:
            forlineinorder.lines:
                lots=line.pack_lot_idsorFalse
                iflots:
                    forlotinlots:
                        lot_values.append({
                            'product_name':lot.product_id.name,
                            'quantity':line.qtyiflot.product_id.tracking=='lot'else1.0,
                            'uom_name':line.product_uom_id.name,
                            'lot_name':lot.lot_name,
                        })

        returnlot_values
