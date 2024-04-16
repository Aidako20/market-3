#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classChooseDestinationLocation(models.TransientModel):
    _name='stock.package.destination'
    _description='StockPackageDestination'

    picking_id=fields.Many2one('stock.picking',required=True)
    move_line_ids=fields.Many2many('stock.move.line','Products',compute='_compute_move_line_ids',required=True)
    location_dest_id=fields.Many2one('stock.location','Destinationlocation',required=True)
    filtered_location=fields.One2many(comodel_name='stock.location',compute='_filter_location')

    @api.depends('picking_id')
    def_compute_move_line_ids(self):
        fordestinationinself:
            destination.move_line_ids=destination.picking_id.move_line_ids.filtered(lambdal:l.qty_done>0andnotl.result_package_id)

    @api.depends('move_line_ids')
    def_filter_location(self):
        fordestinationinself:
            destination.filtered_location=destination.move_line_ids.mapped('location_dest_id')

    defaction_done(self):
        #setthesamelocationoneachmovelineandpassagaininaction_put_in_pack
        self.move_line_ids.location_dest_id=self.location_dest_id
        returnself.picking_id.action_put_in_pack()
