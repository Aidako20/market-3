#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimport_,api,fields,models
fromflectra.exceptionsimportUserError
fromflectra.tools.float_utilsimportfloat_round


classReturnPickingLine(models.TransientModel):
    _name="stock.return.picking.line"
    _rec_name='product_id'
    _description='ReturnPickingLine'

    product_id=fields.Many2one('product.product',string="Product",required=True,domain="[('id','=',product_id)]")
    quantity=fields.Float("Quantity",digits='ProductUnitofMeasure',required=True)
    uom_id=fields.Many2one('uom.uom',string='UnitofMeasure',related='product_id.uom_id')
    wizard_id=fields.Many2one('stock.return.picking',string="Wizard")
    move_id=fields.Many2one('stock.move',"Move")


classReturnPicking(models.TransientModel):
    _name='stock.return.picking'
    _description='ReturnPicking'

    @api.model
    defdefault_get(self,fields):
        iflen(self.env.context.get('active_ids',list()))>1:
            raiseUserError(_("Youmayonlyreturnonepickingatatime."))
        res=super(ReturnPicking,self).default_get(fields)
        ifself.env.context.get('active_id')andself.env.context.get('active_model')=='stock.picking':
            picking=self.env['stock.picking'].browse(self.env.context.get('active_id'))
            ifpicking.exists():
                res.update({'picking_id':picking.id})
        returnres

    picking_id=fields.Many2one('stock.picking')
    product_return_moves=fields.One2many('stock.return.picking.line','wizard_id','Moves')
    move_dest_exists=fields.Boolean('ChainedMoveExists',readonly=True)
    original_location_id=fields.Many2one('stock.location')
    parent_location_id=fields.Many2one('stock.location')
    company_id=fields.Many2one(related='picking_id.company_id')
    location_id=fields.Many2one(
        'stock.location','ReturnLocation',
        domain="['|',('id','=',original_location_id),'|','&',('return_location','=',True),('company_id','=',False),'&',('return_location','=',True),('company_id','=',company_id)]")

    @api.onchange('picking_id')
    def_onchange_picking_id(self):
        move_dest_exists=False
        product_return_moves=[(5,)]
        ifself.picking_idandself.picking_id.state!='done':
            raiseUserError(_("YoumayonlyreturnDonepickings."))
        #Incasewewanttosetspecificdefaultvalues(e.g.'to_refund'),wemustfetchthe
        #defaultvaluesforcreation.
        line_fields=[fforfinself.env['stock.return.picking.line']._fields.keys()]
        product_return_moves_data_tmpl=self.env['stock.return.picking.line'].default_get(line_fields)
        formoveinself.picking_id.move_lines:
            ifmove.state=='cancel':
                continue
            ifmove.scrapped:
                continue
            ifmove.move_dest_ids:
                move_dest_exists=True
            product_return_moves_data=dict(product_return_moves_data_tmpl)
            product_return_moves_data.update(self._prepare_stock_return_picking_line_vals_from_move(move))
            product_return_moves.append((0,0,product_return_moves_data))
        ifself.picking_idandnotproduct_return_moves:
            raiseUserError(_("Noproductstoreturn(onlylinesinDonestateandnotfullyreturnedyetcanbereturned)."))
        ifself.picking_id:
            self.product_return_moves=product_return_moves
            self.move_dest_exists=move_dest_exists
            self.parent_location_id=self.picking_id.picking_type_id.warehouse_idandself.picking_id.picking_type_id.warehouse_id.view_location_id.idorself.picking_id.location_id.location_id.id
            self.original_location_id=self.picking_id.location_id.id
            location_id=self.picking_id.location_id.id
            ifself.picking_id.picking_type_id.return_picking_type_id.default_location_dest_id.return_location:
                location_id=self.picking_id.picking_type_id.return_picking_type_id.default_location_dest_id.id
            self.location_id=location_id

    @api.model
    def_prepare_stock_return_picking_line_vals_from_move(self,stock_move):
        quantity=stock_move.product_qty
        formoveinstock_move.move_dest_ids:
            ifnotmove.origin_returned_move_idormove.origin_returned_move_id!=stock_move:
                continue
            ifmove.statein('partially_available','assigned'):
                quantity-=sum(move.move_line_ids.mapped('product_qty'))
            elifmove.statein('done'):
                quantity-=move.product_qty
        quantity=float_round(quantity,precision_rounding=stock_move.product_id.uom_id.rounding)
        return{
            'product_id':stock_move.product_id.id,
            'quantity':quantity,
            'move_id':stock_move.id,
            'uom_id':stock_move.product_id.uom_id.id,
        }

    def_prepare_move_default_values(self,return_line,new_picking):
        vals={
            'product_id':return_line.product_id.id,
            'product_uom_qty':return_line.quantity,
            'product_uom':return_line.product_id.uom_id.id,
            'picking_id':new_picking.id,
            'state':'draft',
            'date':fields.Datetime.now(),
            'location_id':return_line.move_id.location_dest_id.id,
            'location_dest_id':self.location_id.idorreturn_line.move_id.location_id.id,
            'picking_type_id':new_picking.picking_type_id.id,
            'warehouse_id':self.picking_id.picking_type_id.warehouse_id.id,
            'origin_returned_move_id':return_line.move_id.id,
            'procure_method':'make_to_stock',
        }
        returnvals

    def_create_returns(self):
        #TODOsle:theunreserveofthenextmovescouldbelessbrutal
        forreturn_moveinself.product_return_moves.mapped('move_id'):
            return_move.move_dest_ids.filtered(lambdam:m.statenotin('done','cancel'))._do_unreserve()

        #createnewpickingforreturnedproducts
        picking_type_id=self.picking_id.picking_type_id.return_picking_type_id.idorself.picking_id.picking_type_id.id
        new_picking=self.picking_id.copy({
            'move_lines':[],
            'picking_type_id':picking_type_id,
            'state':'draft',
            'origin':_("Returnof%s",self.picking_id.name),
            'location_id':self.picking_id.location_dest_id.id,
            'location_dest_id':self.location_id.id})
        new_picking.message_post_with_view('mail.message_origin_link',
            values={'self':new_picking,'origin':self.picking_id},
            subtype_id=self.env.ref('mail.mt_note').id)
        returned_lines=0
        forreturn_lineinself.product_return_moves:
            ifnotreturn_line.move_id:
                raiseUserError(_("Youhavemanuallycreatedproductlines,pleasedeletethemtoproceed."))
            #TODOsle:float_is_zero?
            ifreturn_line.quantity:
                returned_lines+=1
                vals=self._prepare_move_default_values(return_line,new_picking)
                r=return_line.move_id.copy(vals)
                vals={}

                #+--------------------------------------------------------------------------------------------------------+
                #|      picking_pick    <--MoveOrig--   picking_pack    --MoveDest-->  picking_ship
                #|             |returned_move_ids             ↑                                 |returned_move_ids
                #|             ↓                               |return_line.move_id             ↓
                #|      returnpick(Addasdest)         returntoLink                   returnship(Addasorig)
                #+--------------------------------------------------------------------------------------------------------+
                move_orig_to_link=return_line.move_id.move_dest_ids.mapped('returned_move_ids')
                #linktooriginalmove
                move_orig_to_link|=return_line.move_id
                #linktosiblingsoforiginalmove,ifany
                move_orig_to_link|=return_line.move_id\
                    .mapped('move_dest_ids').filtered(lambdam:m.statenotin('cancel'))\
                    .mapped('move_orig_ids').filtered(lambdam:m.statenotin('cancel'))
                move_dest_to_link=return_line.move_id.move_orig_ids.mapped('returned_move_ids')
                #linktochildrenoforiginallyreturnedmoves,ifany.Notethattheuseof
                #'return_line.move_id.move_orig_ids.returned_move_ids.move_orig_ids.move_dest_ids'
                #insteadof'return_line.move_id.move_orig_ids.move_dest_ids'preventslinkinga
                #returndirectlytothedestinationmovesofitsparents.However,thereturnof
                #thereturnwillbelinkedtothedestinationmoves.
                move_dest_to_link|=return_line.move_id.move_orig_ids.mapped('returned_move_ids')\
                    .mapped('move_orig_ids').filtered(lambdam:m.statenotin('cancel'))\
                    .mapped('move_dest_ids').filtered(lambdam:m.statenotin('cancel'))
                vals['move_orig_ids']=[(4,m.id)forminmove_orig_to_link]
                vals['move_dest_ids']=[(4,m.id)forminmove_dest_to_link]
                r.write(vals)
        ifnotreturned_lines:
            raiseUserError(_("Pleasespecifyatleastonenon-zeroquantity."))

        new_picking.action_confirm()
        new_picking.action_assign()
        returnnew_picking.id,picking_type_id

    defcreate_returns(self):
        forwizardinself:
            new_picking_id,pick_type_id=wizard._create_returns()
        #Overridethecontexttodisableallthepotentialfiltersthatcouldhavebeensetpreviously
        ctx=dict(self.env.context)
        ctx.update({
            'default_partner_id':self.picking_id.partner_id.id,
            'search_default_picking_type_id':pick_type_id,
            'search_default_draft':False,
            'search_default_assigned':False,
            'search_default_confirmed':False,
            'search_default_ready':False,
            'search_default_planning_issues':False,
            'search_default_available':False,
        })
        return{
            'name':_('ReturnedPicking'),
            'view_mode':'form,tree,calendar',
            'res_model':'stock.picking',
            'res_id':new_picking_id,
            'type':'ir.actions.act_window',
            'context':ctx,
        }
