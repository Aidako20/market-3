#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromcollectionsimportdefaultdict

fromflectraimportfields,models,_
fromflectra.exceptionsimportUserError
fromflectra.tools.float_utilsimportfloat_compare,float_is_zero


classStockMove(models.Model):
    _inherit='stock.move'

    is_subcontract=fields.Boolean('Themoveisasubcontractreceipt')
    show_subcontracting_details_visible=fields.Boolean(
        compute='_compute_show_subcontracting_details_visible'
    )

    def_compute_show_subcontracting_details_visible(self):
        """Computeiftheactionbuttoninordertoseemovesrawisvisible"""
        formoveinself:
            ifmove.is_subcontractandmove._has_tracked_subcontract_components()and\
                    notfloat_is_zero(move.quantity_done,precision_rounding=move.product_uom.rounding):
                move.show_subcontracting_details_visible=True
            else:
                move.show_subcontracting_details_visible=False

    def_compute_show_details_visible(self):
        """Ifthemoveissubcontractandthecomponentsaretracked.Thenthe
        showdetailsbuttonisvisible.
        """
        res=super(StockMove,self)._compute_show_details_visible()
        formoveinself:
            ifnotmove.is_subcontract:
                continue
            ifnotmove._has_tracked_subcontract_components():
                continue
            move.show_details_visible=True
        returnres

    defcopy(self,default=None):
        self.ensure_one()
        ifnotself.is_subcontractor'location_id'indefault:
            returnsuper(StockMove,self).copy(default=default)
        ifnotdefault:
            default={}
        default['location_id']=self.picking_id.location_id.id
        returnsuper(StockMove,self).copy(default=default)

    defwrite(self,values):
        """Iftheinitialdemandisupdatedthenalsoupdatethelinked
        subcontractordertothenewquantity.
        """
        if'product_uom_qty'invaluesandself.env.context.get('cancel_backorder')isnotFalse:
            self.filtered(lambdam:m.is_subcontractandm.statenotin['draft','cancel','done'])._update_subcontract_order_qty(values['product_uom_qty'])
        res=super().write(values)
        if'date'invalues:
            formoveinself:
                ifmove.statein('done','cancel')ornotmove.is_subcontract:
                    continue
                move.move_orig_ids.production_id.filtered(lambdap:p.statenotin('done','cancel')).write({
                    'date_planned_finished':move.date,
                    'date_planned_start':move.date,
                })
        returnres

    defaction_show_details(self):
        """Opentheproducewizardinordertoregistertrackedcomponentsfor
        subcontractedproduct.Otherwiseusestandardbehavior.
        """
        self.ensure_one()
        ifself._has_components_to_record():
            returnself._action_record_components()
        action=super(StockMove,self).action_show_details()
        ifself.is_subcontractandself._has_tracked_subcontract_components():
            action['views']=[(self.env.ref('stock.view_stock_move_operations').id,'form')]
            action['context'].update({
                'show_lots_m2o':self.has_tracking!='none',
                'show_lots_text':False,
            })
        returnaction

    defaction_show_subcontract_details(self):
        """Displaymovesrawforsubcontractedproductself."""
        moves=self.move_orig_ids.production_id.move_raw_ids
        tree_view=self.env.ref('mrp_subcontracting.mrp_subcontracting_move_tree_view')
        form_view=self.env.ref('mrp_subcontracting.mrp_subcontracting_move_form_view')
        ctx=dict(self._context,search_default_by_product=True,subcontract_move_id=self.id)
        return{
            'name':_('RawMaterialsfor%s')%(self.product_id.display_name),
            'type':'ir.actions.act_window',
            'res_model':'stock.move',
            'views':[(tree_view.id,'list'),(form_view.id,'form')],
            'target':'current',
            'domain':[('id','in',moves.ids)],
            'context':ctx
        }

    def_action_cancel(self):
        formoveinself:
            ifmove.is_subcontract:
                active_production=move.move_orig_ids.production_id.filtered(lambdap:p.statenotin('done','cancel'))
                moves=self.env.context.get('moves_todo')
                ifnotmovesoractive_productionnotinmoves.move_orig_ids.production_id:
                    active_production.with_context(skip_activity=True).action_cancel()
        returnsuper()._action_cancel()

    def_action_confirm(self,merge=True,merge_into=False):
        subcontract_details_per_picking=defaultdict(list)
        move_to_not_merge=self.env['stock.move']
        formoveinself:
            ifmove.location_id.usage!='supplier'ormove.location_dest_id.usage=='supplier':
                continue
            ifmove.move_orig_ids.production_id:
                continue
            bom=move._get_subcontract_bom()
            ifnotbom:
                continue
            iffloat_is_zero(move.product_qty,precision_rounding=move.product_uom.rounding)and\
                    move.picking_id.immediate_transferisTrue:
                raiseUserError(_("Tosubcontract,useaplannedtransfer."))
            subcontract_details_per_picking[move.picking_id].append((move,bom))
            move.write({
                'is_subcontract':True,
                'location_id':move.picking_id.partner_id.with_company(move.company_id).property_stock_subcontractor.id
            })
            move_to_not_merge|=move
        forpicking,subcontract_detailsinsubcontract_details_per_picking.items():
            picking._subcontracted_produce(subcontract_details)

        #Weavoidmergingmoveduetocomplicationwithstock.rule.
        res=super(StockMove,move_to_not_merge)._action_confirm(merge=False)
        res|=super(StockMove,self-move_to_not_merge)._action_confirm(merge=merge,merge_into=merge_into)
        ifsubcontract_details_per_picking:
            self.env['stock.picking'].concat(*list(subcontract_details_per_picking.keys())).action_assign()
        returnres.exists()

    def_action_record_components(self):
        self.ensure_one()
        production=self.move_orig_ids.production_id[-1:]
        view=self.env.ref('mrp_subcontracting.mrp_production_subcontracting_form_view')
        return{
            'name':_('Subcontract'),
            'type':'ir.actions.act_window',
            'view_mode':'form',
            'res_model':'mrp.production',
            'views':[(view.id,'form')],
            'view_id':view.id,
            'target':'new',
            'res_id':production.id,
            'context':dict(self.env.context,subcontract_move_id=self.id),
        }

    def_get_subcontract_bom(self):
        self.ensure_one()
        bom=self.env['mrp.bom'].sudo()._bom_subcontract_find(
            product=self.product_id,
            picking_type=self.picking_type_id,
            company_id=self.company_id.id,
            bom_type='subcontract',
            subcontractor=self.picking_id.partner_id,
        )
        returnbom

    def_has_components_to_record(self):
        """Returnstrueifthemovehasstillsometrackedcomponentstorecord."""
        self.ensure_one()
        ifnotself.is_subcontract:
            returnFalse
        rounding=self.product_uom.rounding
        production=self.move_orig_ids.production_id[-1:]
        returnself._has_tracked_subcontract_components()and\
            float_compare(production.qty_produced,production.product_uom_qty,precision_rounding=rounding)<0and\
            float_compare(self.quantity_done,self.product_uom_qty,precision_rounding=rounding)<0

    def_has_tracked_subcontract_components(self):
        self.ensure_one()
        returnany(m.has_tracking!='none'forminself.move_orig_ids.production_id.move_raw_ids)

    def_prepare_extra_move_vals(self,qty):
        vals=super(StockMove,self)._prepare_extra_move_vals(qty)
        vals['location_id']=self.location_id.id
        returnvals

    def_prepare_move_split_vals(self,qty):
        vals=super(StockMove,self)._prepare_move_split_vals(qty)
        vals['location_id']=self.location_id.id
        returnvals

    def_should_bypass_set_qty_producing(self):
        ifself.env.context.get('subcontract_move_id'):
            returnFalse
        returnsuper()._should_bypass_set_qty_producing()

    def_should_bypass_reservation(self):
        """Ifthemoveissubcontractedthenignorethereservation."""
        should_bypass_reservation=super(StockMove,self)._should_bypass_reservation()
        ifnotshould_bypass_reservationandself.is_subcontract:
            returnTrue
        returnshould_bypass_reservation

    def_update_subcontract_order_qty(self,new_quantity):
        formoveinself:
            quantity_to_remove=move.product_uom_qty-new_quantity
            productions=move.move_orig_ids.production_id.filtered(lambdap:p.statenotin('done','cancel'))[::-1]
            #Cancelproductionsuntilreachnew_quantity
            forproductioninproductions:
                ifquantity_to_remove<=0.0:
                    break
                ifquantity_to_remove>=production.product_qty:
                    quantity_to_remove-=production.product_qty
                    production.with_context(skip_activity=True).action_cancel()
                else:
                    self.env['change.production.qty'].with_context(skip_activity=True).create({
                        'mo_id':production.id,
                        'product_qty':production.product_uom_qty-quantity_to_remove
                    }).change_prod_qty()
