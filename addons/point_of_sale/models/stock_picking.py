#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models
fromflectra.exceptionsimportUserError,ValidationError
fromflectra.toolsimportfloat_is_zero,float_compare

fromitertoolsimportgroupby
fromcollectionsimportdefaultdict

classStockPicking(models.Model):
    _inherit='stock.picking'

    pos_session_id=fields.Many2one('pos.session',index=True)
    pos_order_id=fields.Many2one('pos.order',index=True)

    def_prepare_picking_vals(self,partner,picking_type,location_id,location_dest_id):
        return{
            'partner_id':partner.idifpartnerelseFalse,
            'user_id':False,
            'picking_type_id':picking_type.id,
            'move_type':'direct',
            'location_id':location_id,
            'location_dest_id':location_dest_id,
        }


    @api.model
    def_create_picking_from_pos_order_lines(self,location_dest_id,lines,picking_type,partner=False):
        """We'llcreatesomepickingbasedonorder_lines"""

        pickings=self.env['stock.picking']
        stockable_lines=lines.filtered(lambdal:l.product_id.typein['product','consu']andnotfloat_is_zero(l.qty,precision_rounding=l.product_id.uom_id.rounding))
        ifnotstockable_lines:
            returnpickings
        positive_lines=stockable_lines.filtered(lambdal:l.qty>0)
        negative_lines=stockable_lines-positive_lines

        ifpositive_lines:
            location_id=picking_type.default_location_src_id.id
            positive_picking=self.env['stock.picking'].create(
                self._prepare_picking_vals(partner,picking_type,location_id,location_dest_id)
            )

            positive_picking._create_move_from_pos_order_lines(positive_lines)
            self.env['base'].flush()
            try:
                withself.env.cr.savepoint():
                    positive_picking._action_done()
            except(UserError,ValidationError):
                pass

            pickings|=positive_picking
        ifnegative_lines:
            ifpicking_type.return_picking_type_id:
                return_picking_type=picking_type.return_picking_type_id
                return_location_id=return_picking_type.default_location_dest_id.id
            else:
                return_picking_type=picking_type
                return_location_id=picking_type.default_location_src_id.id

            negative_picking=self.env['stock.picking'].create(
                self._prepare_picking_vals(partner,return_picking_type,location_dest_id,return_location_id)
            )
            negative_picking._create_move_from_pos_order_lines(negative_lines)
            self.env['base'].flush()
            try:
                withself.env.cr.savepoint():
                    negative_picking._action_done()
            except(UserError,ValidationError):
                pass
            pickings|=negative_picking
        returnpickings

    def_prepare_stock_move_vals(self,first_line,order_lines):
        return{
            'name':first_line.name,
            'product_uom':first_line.product_id.uom_id.id,
            'picking_id':self.id,
            'picking_type_id':self.picking_type_id.id,
            'product_id':first_line.product_id.id,
            'product_uom_qty':abs(sum(order_lines.mapped('qty'))),
            'state':'draft',
            'location_id':self.location_id.id,
            'location_dest_id':self.location_dest_id.id,
            'company_id':self.company_id.id,
        }

    @api.model
    def_create_move_lines_for_pos_order(self,moves,set_quantity_done_on_move=False):
        moves._action_assign()
        formove_lineinmoves.move_line_ids:
            move_line.qty_done=move_line.product_uom_qty
        mls_vals=[]
        moves_to_set=set()
        formoveinmoves:
            iffloat_compare(move.product_uom_qty,move.quantity_done,precision_rounding=move.product_uom.rounding)>0:
                remaining_qty=move.product_uom_qty-move.quantity_done
                mls_vals.append(dict(move._prepare_move_line_vals(),qty_done=remaining_qty))
                moves_to_set.add(move.id)
        self.env['stock.move.line'].create(mls_vals)
        ifset_quantity_done_on_move:
            formoveinself.env['stock.move'].browse(moves_to_set):
                move.quantity_done=move.product_uom_qty

    def_create_production_lots_for_pos_order(self,lines):
        '''Searchforexistinglotsandcreatemissingones.

            :paramlines:posorderlineswithpacklotids.
            :typelines:pos.order.linerecordset.

            :returnstock.production.lotrecordset.
        '''
        self.ensure_one()
        valid_lots=self.env['stock.production.lot']
        ifself.picking_type_id.use_existing_lots:
            lots=lines.pack_lot_ids.filtered(lambdal:l.lot_name)
            lots_data=set(lots.mapped(lambdal:(l.product_id.id,l.lot_name)))
            existing_lots=self.env['stock.production.lot'].search([
                ('company_id','=',self.company_id.id),
                ('product_id','in',lines.mapped('product_id').ids),
                ('name','in',lots.mapped('lot_name')),
            ])
            #Theprevioussearchmayreturn(product_id.id,lot_name)combinationsthathavenomatchinginlines.pack_lot_ids.
            forlotinexisting_lots:
                if(lot.product_id.id,lot.name)inlots_data:
                    valid_lots|=lot
                    lots_data.remove((lot.product_id.id,lot.name))

            ifself.picking_type_id.use_create_lots:
                missing_lot_values=[]
                forlot_product_id,lot_nameinlots_data:
                    missing_lot_values.append({'company_id':self.company_id.id,'product_id':lot_product_id,'name':lot_name})
                valid_lots|=self.env['stock.production.lot'].create(missing_lot_values)
        returnvalid_lots

    def_create_move_from_pos_order_lines(self,lines):
        self.ensure_one()
        lines_by_product=groupby(sorted(lines,key=lambdal:l.product_id.id),key=lambdal:l.product_id.id)
        move_vals=[]
        lines_data=defaultdict(dict)
        forproduct_id,olinesinlines_by_product:
            order_lines=self.env['pos.order.line'].concat(*olines)
            move_vals.append(self._prepare_stock_move_vals(order_lines[0],order_lines))
            lines_data[product_id].update({'order_lines':order_lines})
        moves=self.env['stock.move'].create(move_vals)
        formoveinmoves:
            lines_data[move.product_id.id].update({'move':move})
        confirmed_moves=moves._action_confirm()
        #Confirmedmoveswithproduct_idnotinlines.Thiscanhappene.g.whenproduct_idhasaphantom-typebom.
        confirmed_moves_to_assign=confirmed_moves.filtered(lambdam:m.product_id.idnotinlines_dataorm.product_id.tracking=='none')
        self._create_move_lines_for_pos_order(confirmed_moves_to_assign,set_quantity_done_on_move=True)
        confirmed_moves_remaining=confirmed_moves-confirmed_moves_to_assign
        ifself.picking_type_id.use_existing_lotsorself.picking_type_id.use_create_lots:
            existing_lots=self._create_production_lots_for_pos_order(lines)
            move_lines_to_create=[]
            formoveinconfirmed_moves_remaining:
                forlineinlines_data[move.product_id.id]['order_lines']:
                    sum_of_lots=0
                    forlotinline.pack_lot_ids.filtered(lambdal:l.lot_name):
                        ifline.product_id.tracking=='serial':
                            qty=1
                        else:
                            qty=abs(line.qty)
                        ml_vals=dict(move._prepare_move_line_vals(),qty_done=qty)
                        ifexisting_lots:
                            existing_lot=existing_lots.filtered_domain([('product_id','=',line.product_id.id),('name','=',lot.lot_name)])
                            quant=self.env['stock.quant']
                            ifexisting_lot:
                                quant=self.env['stock.quant'].search(
                                    [('lot_id','=',existing_lot.id),('quantity','>','0.0'),('location_id','child_of',move.location_id.id)],
                                    order='iddesc',
                                    limit=1
                                )
                            ml_vals.update({
                                'lot_id':existing_lot.id,
                                'location_id':quant.location_id.idormove.location_id.id,
                                'owner_id':quant.owner_id.idorFalse,
                            })
                        else:
                            ml_vals.update({'lot_name':lot.lot_name})
                        move_lines_to_create.append(ml_vals)
                        sum_of_lots+=qty
                    ifabs(line.qty)!=sum_of_lots:
                        difference_qty=abs(line.qty)-sum_of_lots
                        ml_vals=lines_data[move.product_id.id]['move']._prepare_move_line_vals()
                        ifline.product_id.tracking=='serial':
                            ml_vals.update({'qty_done':1})
                            move_lines_to_create.extend([ml_valsforiinrange(int(difference_qty))])
                        else:
                            ml_vals.update({'qty_done':difference_qty})
                            move_lines_to_create.append(ml_vals)
            self.env['stock.move.line'].create(move_lines_to_create)
        else:
            self._create_move_lines_for_pos_order(confirmed_moves_remaining)

    def_send_confirmation_email(self):
        #AvoidsendingMail/SMSforPOSdeliveries
        pickings=self.filtered(lambdap:p.picking_type_id!=p.picking_type_id.warehouse_id.pos_type_id)
        returnsuper(StockPicking,pickings)._send_confirmation_email()
