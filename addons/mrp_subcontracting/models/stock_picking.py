#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromdatetimeimporttimedelta

fromflectraimportapi,fields,models
fromflectra.tools.float_utilsimportfloat_compare
fromdateutil.relativedeltaimportrelativedelta


classStockPicking(models.Model):
    _inherit='stock.picking'

    display_action_record_components=fields.Boolean(compute='_compute_display_action_record_components')

    @api.depends('state')
    def_compute_display_action_record_components(self):
        forpickinginself:
            #Hideifnotencodingstate
            ifpicking.statein('draft','cancel','done'):
                picking.display_action_record_components=False
                continue
            ifnotpicking._is_subcontract():
                picking.display_action_record_components=False
                continue
            #Hideifalltrackedproductmovelinesarealreadyrecorded.
            picking.display_action_record_components=any(
                move._has_components_to_record()formoveinpicking.move_lines)

    #-------------------------------------------------------------------------
    #Actionmethods
    #-------------------------------------------------------------------------
    def_action_done(self):
        res=super(StockPicking,self)._action_done()

        formoveinself.move_lines.filtered(lambdamove:move.is_subcontract):
            #Autosetqty_producing/lot_producing_idofMOifthereisn'ttrackedcomponent
            #Ifthereistrackedcomponent,theflowusesubcontracting_record_componentinstead
            ifmove._has_tracked_subcontract_components():
                continue
            production=move.move_orig_ids.production_id.filtered(lambdap:p.statenotin('done','cancel'))[-1:]
            ifnotproduction:
                continue
            #Manageadditionalquantities
            quantity_done_move=move.product_uom._compute_quantity(move.quantity_done,production.product_uom_id)
            iffloat_compare(production.product_qty,quantity_done_move,precision_rounding=production.product_uom_id.rounding)==-1:
                change_qty=self.env['change.production.qty'].create({
                    'mo_id':production.id,
                    'product_qty':quantity_done_move
                })
                change_qty.with_context(skip_activity=True).change_prod_qty()
            #CreatebackorderMOforeachmovelines
            formove_lineinmove.move_line_ids:
                ifmove_line.lot_id:
                    production.lot_producing_id=move_line.lot_id
                production.qty_producing=move_line.product_uom_id._compute_quantity(move_line.qty_done,production.product_uom_id)
                production._set_qty_producing()
                ifmove_line!=move.move_line_ids[-1]:
                    backorder=production._generate_backorder_productions(close_mo=False)
                    #Themove_dest_idswon'tbesetbecausethe_splitfilteroutdonemove
                    backorder.move_finished_ids.filtered(lambdamo:mo.product_id==move.product_id).move_dest_ids=production.move_finished_ids.filtered(lambdamo:mo.product_id==move.product_id).move_dest_ids
                    production.product_qty=production.qty_producing
                    production=backorder

        forpickinginself:
            productions_to_done=picking._get_subcontracted_productions()._subcontracting_filter_to_done()
            ifnotproductions_to_done:
                continue
            production_ids_backorder=[]
            ifnotself.env.context.get('cancel_backorder'):
                production_ids_backorder=productions_to_done.filtered(lambdamo:mo.state=="progress").ids
            productions_to_done.with_context(subcontract_move_id=True,mo_ids_to_backorder=production_ids_backorder).button_mark_done()
            #Forconcistency,setthedateonproductionmovebeforethedate
            #onpicking.(Traceabilityreport+ProductMovesmenuitem)
            minimum_date=min(picking.move_line_ids.mapped('date'))
            production_moves=productions_to_done.move_raw_ids|productions_to_done.move_finished_ids
            production_moves.write({'date':minimum_date-timedelta(seconds=1)})
            production_moves.move_line_ids.write({'date':minimum_date-timedelta(seconds=1)})
        returnres

    defaction_record_components(self):
        self.ensure_one()
        formoveinself.move_lines:
            ifmove._has_components_to_record():
                returnmove._action_record_components()

    #-------------------------------------------------------------------------
    #Subcontracthelpers
    #-------------------------------------------------------------------------
    def_is_subcontract(self):
        self.ensure_one()
        returnself.picking_type_id.code=='incoming'andany(m.is_subcontractforminself.move_lines)

    def_get_subcontracted_productions(self):
        returnself.move_lines.filtered(lambdamove:move.is_subcontract).move_orig_ids.production_id

    def_get_warehouse(self,subcontract_move):
        returnsubcontract_move.warehouse_idorself.picking_type_id.warehouse_id

    def_prepare_subcontract_mo_vals(self,subcontract_move,bom):
        subcontract_move.ensure_one()
        group=self.env['procurement.group'].create({
            'name':self.name,
            'partner_id':self.partner_id.id,
        })
        product=subcontract_move.product_id
        warehouse=self._get_warehouse(subcontract_move)
        vals={
            'company_id':subcontract_move.company_id.id,
            'procurement_group_id':group.id,
            'product_id':product.id,
            'product_uom_id':subcontract_move.product_uom.id,
            'bom_id':bom.id,
            'location_src_id':subcontract_move.picking_id.partner_id.with_company(subcontract_move.company_id).property_stock_subcontractor.id,
            'location_dest_id':subcontract_move.picking_id.partner_id.with_company(subcontract_move.company_id).property_stock_subcontractor.id,
            'product_qty':subcontract_move.product_uom_qty,
            'picking_type_id':warehouse.subcontracting_type_id.id,
            'date_planned_start':subcontract_move.date-relativedelta(days=product.produce_delay)
        }
        returnvals

    def_subcontracted_produce(self,subcontract_details):
        self.ensure_one()
        formove,bominsubcontract_details:
            mo=self.env['mrp.production'].with_company(move.company_id).create(self._prepare_subcontract_mo_vals(move,bom))
            self.env['stock.move'].create(mo._get_moves_raw_values())
            self.env['stock.move'].create(mo._get_moves_finished_values())
            mo.date_planned_finished=move.date #AvoidtohavethepickinglatedependingoftheMO
            mo.action_confirm()

            #Linkthefinishedtothereceiptmove.
            finished_move=mo.move_finished_ids.filtered(lambdam:m.product_id==move.product_id)
            finished_move.write({'move_dest_ids':[(4,move.id,False)]})
            mo.action_assign()
