#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,models


classChooseDestinationLocation(models.TransientModel):
    _inherit="stock.package.destination"

    def_compute_move_line_ids(self):
        destination_without_batch=self.env['stock.package.destination']
        fordestinationinself:
            ifnotdestination.picking_id.batch_id:
                destination_without_batch|=destination
                continue
            destination.move_line_ids=destination.picking_id.batch_id.move_line_ids.filtered(lambdal:l.qty_done>0andnotl.result_package_id)
        super(ChooseDestinationLocation,destination_without_batch)._compute_move_line_ids()

    defaction_done(self):
        ifself.picking_id.batch_id:
            #setthesamelocationoneachmovelineandpassagaininaction_put_in_pack
            self.move_line_ids.location_dest_id=self.location_dest_id
            returnself.picking_id.batch_id.action_put_in_pack()
        else:
            returnsuper().action_done()
