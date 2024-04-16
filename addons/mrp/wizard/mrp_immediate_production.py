#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimport_,api,fields,models
fromflectra.exceptionsimportUserError
fromflectra.toolsimportfloat_compare


classMrpImmediateProductionLine(models.TransientModel):
    _name='mrp.immediate.production.line'
    _description='ImmediateProductionLine'

    immediate_production_id=fields.Many2one('mrp.immediate.production','ImmediateProduction',required=True)
    production_id=fields.Many2one('mrp.production','Production',required=True)
    to_immediate=fields.Boolean('ToProcess')


classMrpImmediateProduction(models.TransientModel):
    _name='mrp.immediate.production'
    _description='ImmediateProduction'

    @api.model
    defdefault_get(self,fields):
        res=super().default_get(fields)
        if'immediate_production_line_ids'infields:
            ifself.env.context.get('default_mo_ids'):
                res['mo_ids']=self.env.context['default_mo_ids']
                res['immediate_production_line_ids']=[(0,0,{'to_immediate':True,'production_id':mo_id[1]})formo_idinres['mo_ids']]
        returnres

    mo_ids=fields.Many2many('mrp.production','mrp_production_production_rel')
    show_productions=fields.Boolean(compute='_compute_show_production')
    immediate_production_line_ids=fields.One2many(
        'mrp.immediate.production.line',
        'immediate_production_id',
        string="ImmediateProductionLines")

    @api.depends('immediate_production_line_ids')
    def_compute_show_production(self):
        forwizardinself:
            wizard.show_productions=len(wizard.immediate_production_line_ids.production_id)>1

    defprocess(self):
        productions_to_do=self.env['mrp.production']
        productions_not_to_do=self.env['mrp.production']
        forlineinself.immediate_production_line_ids:
            ifline.to_immediateisTrue:
                productions_to_do|=line.production_id
            else:
                productions_not_to_do|=line.production_id

        forproductioninproductions_to_do:
            error_msg=""
            ifproduction.product_trackingin('lot','serial')andnotproduction.lot_producing_id:
                production.action_generate_serial()
            ifproduction.product_tracking=='serial'andfloat_compare(production.qty_producing,1,precision_rounding=production.product_uom_id.rounding)==1:
                production.qty_producing=1
            else:
                production.qty_producing=production.product_qty-production.qty_produced
            production._set_qty_producing()
            formoveinproduction.move_raw_ids.filtered(lambdam:m.statenotin['done','cancel']):
                rounding=move.product_uom.rounding
                formove_lineinmove.move_line_ids:
                    ifmove_line.product_uom_qty:
                        move_line.qty_done=min(move_line.product_uom_qty,move_line.move_id.should_consume_qty)
                    iffloat_compare(move.quantity_done,move.should_consume_qty,precision_rounding=rounding)>=0:
                        break
                iffloat_compare(move.product_uom_qty,move.quantity_done,precision_rounding=move.product_uom.rounding)==1:
                    ifmove.has_trackingin('serial','lot'):
                        error_msg+="\n -%s"%move.product_id.display_name

            iferror_msg:
                error_msg=_('YouneedtosupplyLot/SerialNumberforproducts:')+error_msg
                raiseUserError(error_msg)

        productions_to_validate=self.env.context.get('button_mark_done_production_ids')
        ifproductions_to_validate:
            productions_to_validate=self.env['mrp.production'].browse(productions_to_validate)
            productions_to_validate=productions_to_validate-productions_not_to_do
            returnproductions_to_validate.with_context(skip_immediate=True).button_mark_done()
        returnTrue

