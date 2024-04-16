#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromcollectionsimportdefaultdict
fromflectraimportfields,models,_,api
fromflectra.exceptionsimportUserError
fromflectra.osvimportexpression
fromflectra.tools.float_utilsimportfloat_compare,float_is_zero


classMrpProduction(models.Model):
    _inherit='mrp.production'

    move_line_raw_ids=fields.One2many(
        'stock.move.line',string="DetailComponent",readonly=False,
        inverse='_inverse_move_line_raw_ids',compute='_compute_move_line_raw_ids'
    )
    incoming_picking=fields.Many2one(related='move_finished_ids.move_dest_ids.picking_id')

    @api.depends('name')
    defname_get(self):
        return[
            (record.id,"%s(%s)"%(record.incoming_picking.name,record.name))ifrecord.bom_id.type=='subcontract'
            else(record.id,record.name)forrecordinself
        ]

    @api.model
    def_name_search(self,name='',args=None,operator='ilike',limit=100,name_get_uid=None):
        args=list(argsor[])

        ifname==''andoperator=='ilike':
            returnself._search(args,limit=limit,access_rights_uid=name_get_uid)

        #searchthroughMO
        domain=[(self._rec_name,operator,name)]

        #searchthroughtransfers
        picking_rec_name=self.env['stock.picking']._rec_name
        picking_domain=[('bom_id.type','=','subcontract'),('incoming_picking.%s'%picking_rec_name,operator,name)]
        domain=expression.OR([domain,picking_domain])

        args=expression.AND([args,domain])
        returnself._search(args,limit=limit,access_rights_uid=name_get_uid)

    @api.depends('move_raw_ids.move_line_ids')
    def_compute_move_line_raw_ids(self):
        forproductioninself:
            production.move_line_raw_ids=production.move_raw_ids.move_line_ids

    def_inverse_move_line_raw_ids(self):
        forproductioninself:
            line_by_product=defaultdict(lambda:self.env['stock.move.line'])
            forlineinproduction.move_line_raw_ids:
                line_by_product[line.product_id]|=line
            formoveinproduction.move_raw_ids:
                move.move_line_ids=line_by_product.pop(move.product_id,self.env['stock.move.line'])
            forproduct_id,linesinline_by_product.items():
                qty=sum(line.product_uom_id._compute_quantity(line.qty_done,product_id.uom_id)forlineinlines)
                move=production._get_move_raw_values(product_id,qty,product_id.uom_id)
                move['additional']=True
                production.move_raw_ids=[(0,0,move)]
                production.move_raw_ids.filtered(lambdam:m.product_id==product_id)[:1].move_line_ids=lines

    defsubcontracting_record_component(self):
        self.ensure_one()
        assertself.env.context.get('subcontract_move_id')
        iffloat_is_zero(self.qty_producing,precision_rounding=self.product_uom_id.rounding):
            return{'type':'ir.actions.act_window_close'}
        ifself.product_tracking!='none'andnotself.lot_producing_id:
            raiseUserError(_('Youmustenteraserialnumberfor%s')%self.product_id.name)
        forsmlinself.move_raw_ids.move_line_ids:
            ifsml.tracking!='none'andnotsml.lot_id:
                raiseUserError(_('Youmustenteraserialnumberforeachlineof%s')%sml.product_id.display_name)
        self._update_finished_move()
        quantity_issues=self._get_quantity_produced_issues()
        ifquantity_issues:
            backorder=self._generate_backorder_productions(close_mo=False)
            #Noqtytoconsumetoavoidpropagateadditionalmove
            #TODOavoid:stockmovecreatedinbackorderwith0asqty
            backorder.move_raw_ids.filtered(lambdam:m.additional).product_uom_qty=0.0

            backorder.qty_producing=backorder.product_qty
            backorder._set_qty_producing()

            self.product_qty=self.qty_producing
            subcontract_move_id=self.env['stock.move'].browse(self.env.context.get('subcontract_move_id'))
            action=subcontract_move_id._action_record_components()
            action.update({'res_id':backorder.id})
            returnaction
        return{'type':'ir.actions.act_window_close'}

    defaction_subcontracting_discard_remaining_components(self):
        self.ensure_one()
        self.qty_producing=0
        return{'type':'ir.actions.act_window_close'}

    def_pre_button_mark_done(self):
        ifself.env.context.get('subcontract_move_id'):
            returnTrue
        returnsuper()._pre_button_mark_done()

    def_update_finished_move(self):
        """Afterproducing,setthemovelineonthesubcontractpicking."""
        self.ensure_one()
        subcontract_move_id=self.env.context.get('subcontract_move_id')
        ifsubcontract_move_id:
            subcontract_move_id=self.env['stock.move'].browse(subcontract_move_id)
            quantity=self.qty_producing
            ifself.lot_producing_id:
                move_lines=subcontract_move_id.move_line_ids.filtered(lambdaml:ml.lot_id==self.lot_producing_idornotml.lot_id)
            else:
                move_lines=subcontract_move_id.move_line_ids.filtered(lambdaml:notml.lot_id)
            #Updatereservationandquantitydone
            formlinmove_lines:
                rounding=ml.product_uom_id.rounding
                iffloat_compare(quantity,0,precision_rounding=rounding)<=0:
                    break
                quantity_to_process=min(quantity,ml.product_uom_qty-ml.qty_done)
                quantity-=quantity_to_process

                new_quantity_done=(ml.qty_done+quantity_to_process)

                #onwhichlotoffinishedproduct
                iffloat_compare(new_quantity_done,ml.product_uom_qty,precision_rounding=rounding)>=0:
                    ml.write({
                        'qty_done':new_quantity_done,
                        'lot_id':self.lot_producing_idandself.lot_producing_id.id,
                    })
                else:
                    new_qty_reserved=ml.product_uom_qty-new_quantity_done
                    default={
                        'product_uom_qty':new_quantity_done,
                        'qty_done':new_quantity_done,
                        'lot_id':self.lot_producing_idandself.lot_producing_id.id,
                    }
                    ml.copy(default=default)
                    ml.with_context(bypass_reservation_update=True).write({
                        'product_uom_qty':new_qty_reserved,
                        'qty_done':0
                    })

            iffloat_compare(quantity,0,precision_rounding=self.product_uom_id.rounding)>0:
                self.env['stock.move.line'].create({
                    'move_id':subcontract_move_id.id,
                    'picking_id':subcontract_move_id.picking_id.id,
                    'product_id':self.product_id.id,
                    'location_id':subcontract_move_id.location_id.id,
                    'location_dest_id':subcontract_move_id.location_dest_id.id,
                    'product_uom_qty':0,
                    'product_uom_id':self.product_uom_id.id,
                    'qty_done':quantity,
                    'lot_id':self.lot_producing_idandself.lot_producing_id.id,
                })
            ifnotself._get_quantity_to_backorder():
                ml_reserved=subcontract_move_id.move_line_ids.filtered(lambdaml:
                    float_is_zero(ml.qty_done,precision_rounding=ml.product_uom_id.rounding)and
                    notfloat_is_zero(ml.product_uom_qty,precision_rounding=ml.product_uom_id.rounding))
                ml_reserved.unlink()
                formlinsubcontract_move_id.move_line_ids:
                    ml.product_uom_qty=ml.qty_done
                subcontract_move_id._recompute_state()

    def_subcontracting_filter_to_done(self):
        """Filtersubcontractingproductionwherecomposantisalreadyrecordedandshouldbeconsidertobevalidate"""
        deffilter_in(mo):
            ifmo.statein('done','cancel'):
                returnFalse
            iffloat_is_zero(mo.qty_producing,precision_rounding=mo.product_uom_id.rounding):
                returnFalse
            ifnotall(line.lot_idforlineinmo.move_raw_ids.filtered(lambdasm:sm.has_tracking!='none').move_line_ids):
                returnFalse
            ifmo.product_tracking!='none'andnotmo.lot_producing_id:
                returnFalse
            returnTrue

        returnself.filtered(filter_in)
