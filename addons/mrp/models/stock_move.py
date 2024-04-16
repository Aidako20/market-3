#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,exceptions,fields,models,_
fromflectra.exceptionsimportUserError
fromflectra.toolsimportfloat_compare,float_round,float_is_zero,OrderedSet


classStockMoveLine(models.Model):
    _inherit='stock.move.line'

    workorder_id=fields.Many2one('mrp.workorder','WorkOrder',check_company=True)
    production_id=fields.Many2one('mrp.production','ProductionOrder',check_company=True)

    @api.model_create_multi
    defcreate(self,values):
        res=super(StockMoveLine,self).create(values)
        forlineinres:
            #Ifthelineisaddedinadoneproduction,weneedtomapit
            #manuallytotheproducedmovelinesinordertoseetheminthe
            #traceabilityreport
            ifline.move_id.raw_material_production_idandline.state=='done':
                mo=line.move_id.raw_material_production_id
                finished_lots=mo.lot_producing_id
                finished_lots|=mo.move_finished_ids.filtered(lambdam:m.product_id!=mo.product_id).move_line_ids.lot_id
                iffinished_lots:
                    produced_move_lines=mo.move_finished_ids.move_line_ids.filtered(lambdasml:sml.lot_idinfinished_lots)
                    line.produce_line_ids=[(6,0,produced_move_lines.ids)]
                else:
                    produced_move_lines=mo.move_finished_ids.move_line_ids
                    line.produce_line_ids=[(6,0,produced_move_lines.ids)]
        returnres

    def_get_similar_move_lines(self):
        lines=super(StockMoveLine,self)._get_similar_move_lines()
        ifself.move_id.production_id:
            finished_moves=self.move_id.production_id.move_finished_ids
            finished_move_lines=finished_moves.mapped('move_line_ids')
            lines|=finished_move_lines.filtered(lambdaml:ml.product_id==self.product_idand(ml.lot_idorml.lot_name))
        ifself.move_id.raw_material_production_id:
            raw_moves=self.move_id.raw_material_production_id.move_raw_ids
            raw_moves_lines=raw_moves.mapped('move_line_ids')
            lines|=raw_moves_lines.filtered(lambdaml:ml.product_id==self.product_idand(ml.lot_idorml.lot_name))
        returnlines

    def_reservation_is_updatable(self,quantity,reserved_quant):
        self.ensure_one()
        ifself.produce_line_ids.lot_id:
            ml_remaining_qty=self.qty_done-self.product_uom_qty
            ml_remaining_qty=self.product_uom_id._compute_quantity(ml_remaining_qty,self.product_id.uom_id,rounding_method="HALF-UP")
            iffloat_compare(ml_remaining_qty,quantity,precision_rounding=self.product_id.uom_id.rounding)<0:
                returnFalse
        returnsuper(StockMoveLine,self)._reservation_is_updatable(quantity,reserved_quant)

    defwrite(self,vals):
        formove_lineinself:
            production=move_line.move_id.production_idormove_line.move_id.raw_material_production_id
            ifproductionandmove_line.state=='done'andany(fieldinvalsforfieldin('lot_id','location_id','qty_done')):
                move_line._log_message(production,move_line,'mrp.track_production_move_template',vals)
        returnsuper(StockMoveLine,self).write(vals)

    def_get_aggregated_product_quantities(self,**kwargs):
        """Returnsdictionaryofproductsandcorrespondingvaluesofinterestgroupedbyoptionalkit_name

        Removesdescriptionswheredescription==kit_name.kit_nameisexpectedtobepassedasa
        kwargsvaluebecausethisisnotdirectlystoredinmove_line_ids.Unfortunatelybecausewe
        areworkingwithaggregateddata,wehavetoloopthroughtheaggregationtodothisremoval.

        arguments:kit_name(optional):stringvalueofakitnamepassedasakwarg
        returns:dictionary{same_key_as_super:{same_values_as_super,...}
        """
        aggregated_move_lines=super()._get_aggregated_product_quantities(**kwargs)
        kit_name=kwargs.get('kit_name')
        ifkit_name:
            foraggregated_move_lineinaggregated_move_lines:
                ifaggregated_move_lines[aggregated_move_line]['description']==kit_name:
                    aggregated_move_lines[aggregated_move_line]['description']=""
        returnaggregated_move_lines


classStockMove(models.Model):
    _inherit='stock.move'

    created_production_id=fields.Many2one('mrp.production','CreatedProductionOrder',check_company=True)
    production_id=fields.Many2one(
        'mrp.production','ProductionOrderforfinishedproducts',check_company=True,index=True)
    raw_material_production_id=fields.Many2one(
        'mrp.production','ProductionOrderforcomponents',check_company=True,index=True)
    unbuild_id=fields.Many2one(
        'mrp.unbuild','DisassemblyOrder',check_company=True)
    consume_unbuild_id=fields.Many2one(
        'mrp.unbuild','ConsumedDisassemblyOrder',check_company=True)
    allowed_operation_ids=fields.Many2many('mrp.routing.workcenter',compute='_compute_allowed_operation_ids')
    operation_id=fields.Many2one(
        'mrp.routing.workcenter','OperationToConsume',check_company=True,
        domain="[('id','in',allowed_operation_ids)]")
    workorder_id=fields.Many2one(
        'mrp.workorder','WorkOrderToConsume',copy=False,check_company=True)
    #Quantitiestoprocess,innormalizedUoMs
    bom_line_id=fields.Many2one('mrp.bom.line','BoMLine',check_company=True)
    byproduct_id=fields.Many2one(
        'mrp.bom.byproduct','By-products',check_company=True,
        help="By-productlinethatgeneratedthemoveinamanufacturingorder")
    unit_factor=fields.Float('UnitFactor',compute='_compute_unit_factor',store=True)
    is_done=fields.Boolean(
        'Done',compute='_compute_is_done',
        store=True,
        help='TechnicalFieldtoordermoves')
    order_finished_lot_ids=fields.Many2many('stock.production.lot',string="FinishedLot/SerialNumber",compute='_compute_order_finished_lot_ids')
    should_consume_qty=fields.Float('QuantityToConsume',compute='_compute_should_consume_qty',digits='ProductUnitofMeasure')

    @api.depends('raw_material_production_id.priority')
    def_compute_priority(self):
        super()._compute_priority()
        formoveinself:
            move.priority=move.raw_material_production_id.priorityormove.priorityor'0'

    @api.depends('raw_material_production_id.lot_producing_id')
    def_compute_order_finished_lot_ids(self):
        formoveinself:
            move.order_finished_lot_ids=move.raw_material_production_id.lot_producing_id

    @api.depends('raw_material_production_id.bom_id')
    def_compute_allowed_operation_ids(self):
        formoveinself:
            if(
                notmove.raw_material_production_idor
                notmove.raw_material_production_id.bom_idornot
                move.raw_material_production_id.bom_id.operation_ids
            ):
                move.allowed_operation_ids=self.env['mrp.routing.workcenter']
            else:
                operation_domain=[
                    ('id','in',move.raw_material_production_id.bom_id.operation_ids.ids),
                    '|',
                        ('company_id','=',move.company_id.id),
                        ('company_id','=',False)
                ]
                move.allowed_operation_ids=self.env['mrp.routing.workcenter'].search(operation_domain)

    @api.depends('raw_material_production_id.is_locked','production_id.is_locked')
    def_compute_is_locked(self):
        super(StockMove,self)._compute_is_locked()
        formoveinself:
            ifmove.raw_material_production_id:
                move.is_locked=move.raw_material_production_id.is_locked
            ifmove.production_id:
                move.is_locked=move.production_id.is_locked

    @api.depends('state')
    def_compute_is_done(self):
        formoveinself:
            move.is_done=(move.statein('done','cancel'))

    @api.depends('product_uom_qty',
        'raw_material_production_id','raw_material_production_id.product_qty','raw_material_production_id.qty_produced',
        'production_id','production_id.product_qty','production_id.qty_produced')
    def_compute_unit_factor(self):
        formoveinself:
            mo=move.raw_material_production_idormove.production_id
            ifmo:
                move.unit_factor=move.product_uom_qty/((mo.product_qty-mo.qty_produced)or1)
            else:
                move.unit_factor=1.0

    @api.depends('raw_material_production_id','raw_material_production_id.name','production_id','production_id.name')
    def_compute_reference(self):
        moves_with_reference=self.env['stock.move']
        formoveinself:
            ifmove.raw_material_production_idandmove.raw_material_production_id.name:
                move.reference=move.raw_material_production_id.name
                moves_with_reference|=move
            ifmove.production_idandmove.production_id.name:
                move.reference=move.production_id.name
                moves_with_reference|=move
        super(StockMove,self-moves_with_reference)._compute_reference()

    @api.depends('raw_material_production_id.qty_producing','product_uom_qty','product_uom')
    def_compute_should_consume_qty(self):
        formoveinself:
            mo=move.raw_material_production_id
            ifnotmoornotmove.product_uom:
                move.should_consume_qty=0
                continue
            move.should_consume_qty=float_round((mo.qty_producing-mo.qty_produced)*move.unit_factor,precision_rounding=move.product_uom.rounding)

    @api.onchange('product_uom_qty')
    def_onchange_product_uom_qty(self):
        ifself.raw_material_production_idandself.has_tracking=='none':
            mo=self.raw_material_production_id
            self._update_quantity_done(mo)

    @api.model
    defdefault_get(self,fields_list):
        defaults=super(StockMove,self).default_get(fields_list)
        ifself.env.context.get('default_raw_material_production_id')orself.env.context.get('default_production_id'):
            production_id=self.env['mrp.production'].browse(self.env.context.get('default_raw_material_production_id')orself.env.context.get('default_production_id'))
            ifproduction_id.statenotin('draft','cancel'):
                ifproduction_id.state!='done':
                    defaults['state']='draft'
                else:
                    defaults['state']='done'
                    defaults['additional']=True
                defaults['product_uom_qty']=0.0
            elifproduction_id.state=='draft':
                defaults['group_id']=production_id.procurement_group_id.id
                defaults['reference']=production_id.name
        returndefaults

    defwrite(self,vals):
        if'product_uom_qty'invalsand'move_line_ids'invals:
            #firstupdatelinesthenproduct_uom_qtyasthelaterwillunreserve
            #sopossiblyunlinklines
            move_line_vals=vals.pop('move_line_ids')
            super().write({'move_line_ids':move_line_vals})
        returnsuper().write(vals)

    defunlink(self):
        #AvoiddeletingmoverelatedtoactiveMO
        formoveinself:
            ifmove.production_idandmove.production_id.statenotin('draft','cancel'):
                raiseUserError(_('PleasecanceltheManufactureOrderfirst.'))
        returnsuper(StockMove,self).unlink()

    def_action_assign(self):
        res=super(StockMove,self)._action_assign()
        formoveinself.filtered(lambdax:x.production_idorx.raw_material_production_id):
            ifmove.move_line_ids:
                move.move_line_ids.write({'production_id':move.raw_material_production_id.id,
                                               'workorder_id':move.workorder_id.id,})
        returnres

    def_action_confirm(self,merge=True,merge_into=False):
        moves=self.action_explode()
        merge_into=merge_intoandmerge_into.action_explode()
        #wegofurtherwiththelistofidspotentiallychangedbyaction_explode
        returnsuper(StockMove,moves)._action_confirm(merge=merge,merge_into=merge_into)

    defaction_explode(self):
        """Explodespickings"""
        #inordertoexplodeamove,wemusthaveapicking_type_idonthatmovebecauseotherwisethemove
        #won'tbeassignedtoapickinganditwouldbeweirdtoexplodeamoveintoseveraliftheyaren't
        #allgroupedinthesamepicking.
        moves_ids_to_return=OrderedSet()
        moves_ids_to_unlink=OrderedSet()
        phantom_moves_vals_list=[]
        formoveinself:
            ifnotmove.picking_type_idor(move.production_idandmove.production_id.product_id==move.product_id):
                moves_ids_to_return.add(move.id)
                continue
            bom=self.env['mrp.bom'].sudo()._bom_find(product=move.product_id,company_id=move.company_id.id,bom_type='phantom')
            ifnotbom:
                moves_ids_to_return.add(move.id)
                continue
            ifmove.picking_id.immediate_transferorfloat_is_zero(move.product_uom_qty,precision_rounding=move.product_uom.rounding):
                factor=move.product_uom._compute_quantity(move.quantity_done,bom.product_uom_id)/bom.product_qty
            else:
                factor=move.product_uom._compute_quantity(move.product_uom_qty,bom.product_uom_id)/bom.product_qty
            boms,lines=bom.sudo().explode(move.product_id,factor,picking_type=bom.picking_type_id)
            forbom_line,line_datainlines:
                ifmove.picking_id.immediate_transferorfloat_is_zero(move.product_uom_qty,precision_rounding=move.product_uom.rounding):
                    phantom_moves_vals_list+=move._generate_move_phantom(bom_line,0,line_data['qty'])
                else:
                    phantom_moves_vals_list+=move._generate_move_phantom(bom_line,line_data['qty'],0)
            #deletethemovewithoriginalproductwhichisnotrelevantanymore
            moves_ids_to_unlink.add(move.id)

        move_to_unlink=self.env['stock.move'].browse(moves_ids_to_unlink).sudo()
        move_to_unlink.quantity_done=0
        move_to_unlink._action_cancel()
        move_to_unlink.unlink()
        ifphantom_moves_vals_list:
            phantom_moves=self.env['stock.move'].create(phantom_moves_vals_list)
            phantom_moves._adjust_procure_method()
            moves_ids_to_return|=phantom_moves.action_explode().ids
        returnself.env['stock.move'].browse(moves_ids_to_return)

    defaction_show_details(self):
        self.ensure_one()
        action=super().action_show_details()
        ifself.raw_material_production_id:
            action['views']=[(self.env.ref('mrp.view_stock_move_operations_raw').id,'form')]
            action['context']['show_destination_location']=False
            action['context']['active_mo_id']=self.raw_material_production_id.id
        elifself.production_id:
            action['views']=[(self.env.ref('mrp.view_stock_move_operations_finished').id,'form')]
            action['context']['show_source_location']=False
        returnaction

    def_action_cancel(self):
        res=super(StockMove,self)._action_cancel()
        forproductioninself.mapped('raw_material_production_id'):
            ifproduction.state!='cancel':
                continue
            production._action_cancel()
        returnres

    def_prepare_move_split_vals(self,qty):
        defaults=super()._prepare_move_split_vals(qty)
        defaults['workorder_id']=False
        returndefaults

    def_prepare_procurement_origin(self):
        self.ensure_one()
        ifself.raw_material_production_idandself.raw_material_production_id.orderpoint_id:
            returnself.origin
        returnsuper()._prepare_procurement_origin()

    def_prepare_phantom_move_values(self,bom_line,product_qty,quantity_done):
        return{
            'picking_id':self.picking_id.idifself.picking_idelseFalse,
            'product_id':bom_line.product_id.id,
            'product_uom':bom_line.product_uom_id.id,
            'product_uom_qty':product_qty,
            'quantity_done':quantity_done,
            'state':'draft', #willbeconfirmedbelow
            'name':self.name,
            'bom_line_id':bom_line.id,
        }

    def_generate_move_phantom(self,bom_line,product_qty,quantity_done):
        vals=[]
        ifbom_line.product_id.typein['product','consu']:
            vals=self.copy_data(default=self._prepare_phantom_move_values(bom_line,product_qty,quantity_done))
            ifself.state=='assigned':
                forvinvals:
                    v['state']='assigned'
        returnvals

    @api.model
    def_consuming_picking_types(self):
        res=super()._consuming_picking_types()
        res.append('mrp_operation')
        returnres

    def_get_source_document(self):
        res=super()._get_source_document()
        returnresorself.production_idorself.raw_material_production_id

    def_get_upstream_documents_and_responsibles(self,visited):
        ifself.production_idandself.production_id.statenotin('done','cancel'):
            return[(self.production_id,self.production_id.user_id,visited)]
        else:
            returnsuper(StockMove,self)._get_upstream_documents_and_responsibles(visited)

    def_delay_alert_get_documents(self):
        res=super(StockMove,self)._delay_alert_get_documents()
        productions=self.raw_material_production_id|self.production_id
        returnres+list(productions)

    def_should_be_assigned(self):
        res=super(StockMove,self)._should_be_assigned()
        returnbool(resandnot(self.production_idorself.raw_material_production_id))

    def_should_bypass_set_qty_producing(self):
        ifself.statein('done','cancel'):
            returnTrue
        #Donotupdateextraproductquantities
        iffloat_is_zero(self.product_uom_qty,precision_rounding=self.product_uom.rounding):
            returnTrue
        ifself.has_tracking!='none'orself.state=='done':
            returnTrue
        returnFalse

    def_should_bypass_reservation(self):
        res=super(StockMove,self)._should_bypass_reservation()
        returnbool(resandnotself.production_id)

    def_key_assign_picking(self):
        keys=super(StockMove,self)._key_assign_picking()
        returnkeys+(self.created_production_id,)

    @api.model
    def_prepare_merge_moves_distinct_fields(self):
        distinct_fields=super()._prepare_merge_moves_distinct_fields()
        distinct_fields.append('created_production_id')
        ifself.bom_line_idand("phantom"inself.bom_line_id.bom_id.mapped('type')):
            distinct_fields.append('bom_line_id')
        returndistinct_fields

    @api.model
    def_prepare_merge_move_sort_method(self,move):
        keys_sorted=super()._prepare_merge_move_sort_method(move)
        keys_sorted.append(move.created_production_id.id)
        keys_sorted.append(move.bom_line_id.id)
        returnkeys_sorted

    def_compute_kit_quantities(self,product_id,kit_qty,kit_bom,filters):
        """Computesthequantitydeliveredorreceivedwhenakitissoldorpurchased.
        Aratio'qty_processed/qty_needed'iscomputedforeachcomponent,andthelowestoneiskept
        todefinethekit'squantitydeliveredorreceived.
        :paramproduct_id:Thekititselfa.k.a.thefinishedproduct
        :paramkit_qty:Thequantityfromtheorderline
        :paramkit_bom:Thekit'sBoM
        :paramfilters:Dictoflambdaexpressiontodefinethemovestoconsiderandtheonestoignore
        :return:Thequantitydeliveredorreceived
        """
        qty_ratios=[]
        boms,bom_sub_lines=kit_bom.explode(product_id,kit_qty)
        forbom_line,bom_line_datainbom_sub_lines:
            #skipservicesinceweneverdeliverthem
            ifbom_line.product_id.type=='service':
                continue
            iffloat_is_zero(bom_line_data['qty'],precision_rounding=bom_line.product_uom_id.rounding):
                #AsBoMsallowcomponentswith0qty,a.k.a.optionnalcomponents,wesimplyskipthose
                #toavoidadivisionbyzero.
                continue
            bom_line_moves=self.filtered(lambdam:m.bom_line_id==bom_line)
            ifbom_line_moves:
                #Wecomputethequantitiesneededofeachcomponentstomakeonekit.
                #Then,wecollecteveryrelevantmovesrelatedtoaspecificcomponent
                #toknowhowmanyareconsidereddelivered.
                uom_qty_per_kit=bom_line_data['qty']/bom_line_data['original_qty']
                qty_per_kit=bom_line.product_uom_id._compute_quantity(uom_qty_per_kit,bom_line.product_id.uom_id,round=False)
                ifnotqty_per_kit:
                    continue
                incoming_moves=bom_line_moves.filtered(filters['incoming_moves'])
                outgoing_moves=bom_line_moves.filtered(filters['outgoing_moves'])
                qty_processed=sum(incoming_moves.mapped('product_qty'))-sum(outgoing_moves.mapped('product_qty'))
                #Wecomputearatiotoknowhowmanykitswecanproducewiththisquantityofthatspecificcomponent
                qty_ratios.append(float_round(qty_processed/qty_per_kit,precision_rounding=bom_line.product_id.uom_id.rounding))
            else:
                return0.0
        ifqty_ratios:
            #Nowthatwehaveeveryratiobycomponents,wekeepthelowestonetoknowhowmanykitswecanproduce
            #withthequantitiesdeliveredofeachcomponent.Weusethefloordivisionherebecausea'partialkit'
            #doesn'tmakesense.
            returnmin(qty_ratios)//1
        else:
            return0.0

    def_show_details_in_draft(self):
        self.ensure_one()
        production=self.raw_material_production_idorself.production_id
        ifproductionand(self.state!='draft'orproduction.state!='draft'):
            returnTrue
        elifproduction:
            returnFalse
        else:
            returnsuper()._show_details_in_draft()

    def_update_quantity_done(self,mo):
        self.ensure_one()
        new_qty=float_round((mo.qty_producing-mo.qty_produced)*self.unit_factor,precision_rounding=self.product_uom.rounding)
        ifnotself.is_quantity_done_editable:
            self.move_line_ids.filtered(lambdaml:ml.statenotin('done','cancel')).qty_done=0
            self.move_line_ids=self._set_quantity_done_prepare_vals(new_qty)
        else:
            self.quantity_done=new_qty
