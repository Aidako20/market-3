#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models
fromflectra.tools.float_utilsimportfloat_compare


classStockBackorderConfirmationLine(models.TransientModel):
    _name='stock.backorder.confirmation.line'
    _description='BackorderConfirmationLine'

    backorder_confirmation_id=fields.Many2one('stock.backorder.confirmation','ImmediateTransfer')
    picking_id=fields.Many2one('stock.picking','Transfer')
    to_backorder=fields.Boolean('ToBackorder')


classStockBackorderConfirmation(models.TransientModel):
    _name='stock.backorder.confirmation'
    _description='BackorderConfirmation'

    pick_ids=fields.Many2many('stock.picking','stock_picking_backorder_rel')
    show_transfers=fields.Boolean()
    backorder_confirmation_line_ids=fields.One2many(
        'stock.backorder.confirmation.line',
        'backorder_confirmation_id',
        string="BackorderConfirmationLines")

    @api.model
    defdefault_get(self,fields):
        res=super().default_get(fields)
        if'backorder_confirmation_line_ids'infieldsandres.get('pick_ids'):
            res['backorder_confirmation_line_ids']=[
                (0,0,{'to_backorder':True,'picking_id':pick_id})
                forpick_idinres['pick_ids'][0][2]
            ]
            #default_getreturnsx2mvaluesas[(6,0,ids)]
            #becauseofwebclientlimitations
        returnres

    def_check_less_quantities_than_expected(self,pickings):
        forpick_idinpickings:
            moves_to_log={}
            formoveinpick_id.move_lines:
                iffloat_compare(move.product_uom_qty,
                                 move.quantity_done,
                                 precision_rounding=move.product_uom.rounding)>0:
                    moves_to_log[move]=(move.quantity_done,move.product_uom_qty)
            ifmoves_to_log:
                pick_id._log_less_quantities_than_expected(moves_to_log)

    defprocess(self):
        pickings_to_do=self.env['stock.picking']
        pickings_not_to_do=self.env['stock.picking']
        forlineinself.backorder_confirmation_line_ids:
            ifline.to_backorderisTrue:
                pickings_to_do|=line.picking_id
            else:
                pickings_not_to_do|=line.picking_id

        pickings_to_validate=self.env.context.get('button_validate_picking_ids')
        ifpickings_to_validate:
            pickings_to_validate=self.env['stock.picking'].browse(pickings_to_validate).with_context(skip_backorder=True)
            ifpickings_not_to_do:
                self._check_less_quantities_than_expected(pickings_not_to_do)
                pickings_to_validate=pickings_to_validate.with_context(picking_ids_not_to_backorder=pickings_not_to_do.ids)
            returnpickings_to_validate.button_validate()
        returnTrue

    defprocess_cancel_backorder(self):
        pickings_to_validate_ids=self.env.context.get('button_validate_picking_ids')
        ifpickings_to_validate_ids:
            pickings_to_validate=self.env['stock.picking'].browse(pickings_to_validate_ids)
            self._check_less_quantities_than_expected(pickings_to_validate)
            returnpickings_to_validate\
                .with_context(skip_backorder=True,picking_ids_not_to_backorder=self.pick_ids.ids)\
                .button_validate()
        returnTrue

