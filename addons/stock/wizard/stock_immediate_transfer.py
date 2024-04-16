#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimport_,api,fields,models
fromflectra.exceptionsimportUserError


classStockImmediateTransferLine(models.TransientModel):
    _name='stock.immediate.transfer.line'
    _description='ImmediateTransferLine'

    immediate_transfer_id=fields.Many2one('stock.immediate.transfer','ImmediateTransfer',required=True)
    picking_id=fields.Many2one('stock.picking','Transfer',required=True)
    to_immediate=fields.Boolean('ToProcess')


classStockImmediateTransfer(models.TransientModel):
    _name='stock.immediate.transfer'
    _description='ImmediateTransfer'

    pick_ids=fields.Many2many('stock.picking','stock_picking_transfer_rel')
    show_transfers=fields.Boolean()
    immediate_transfer_line_ids=fields.One2many(
        'stock.immediate.transfer.line',
        'immediate_transfer_id',
        string="ImmediateTransferLines")

    @api.model
    defdefault_get(self,fields):
        res=super().default_get(fields)
        if'immediate_transfer_line_ids'infieldsandres.get('pick_ids'):
            res['immediate_transfer_line_ids']=[
                (0,0,{'to_immediate':True,'picking_id':pick_id})
                forpick_idinres['pick_ids'][0][2]
            ]
            #default_getreturnsx2mvaluesas[(6,0,ids)]
            #becauseofwebclientlimitations
        returnres

    defprocess(self):
        pickings_to_do=self.env['stock.picking']
        pickings_not_to_do=self.env['stock.picking']
        forlineinself.immediate_transfer_line_ids:
            ifline.to_immediateisTrue:
                pickings_to_do|=line.picking_id
            else:
                pickings_not_to_do|=line.picking_id

        forpickinginpickings_to_do:
            #Ifstillindraft=>confirmandassign
            ifpicking.state=='draft':
                picking.action_confirm()
                ifpicking.state!='assigned':
                    picking.action_assign()
                    ifpicking.state!='assigned':
                        raiseUserError(_("Couldnotreserveallrequestedproducts.Pleaseusethe\'MarkasTodo\'buttontohandlethereservationmanually."))
            formoveinpicking.move_lines.filtered(lambdam:m.statenotin['done','cancel']):
                formove_lineinmove.move_line_ids:
                    move_line.qty_done=move_line.product_uom_qty

        pickings_to_validate=self.env.context.get('button_validate_picking_ids')
        ifpickings_to_validate:
            pickings_to_validate=self.env['stock.picking'].browse(pickings_to_validate)
            pickings_to_validate=pickings_to_validate-pickings_not_to_do
            returnpickings_to_validate.with_context(skip_immediate=True).button_validate()
        returnTrue

