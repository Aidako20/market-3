#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectraimportapi,fields,models,SUPERUSER_ID,_
fromflectra.tools.float_utilsimportfloat_compare,float_round
fromdatetimeimportdatetime
fromdateutil.relativedeltaimportrelativedelta
fromflectra.exceptionsimportUserError

fromflectra.addons.purchase.models.purchaseimportPurchaseOrderasPurchase


classPurchaseOrder(models.Model):
    _inherit='purchase.order'

    @api.model
    def_default_picking_type(self):
        returnself._get_picking_type(self.env.context.get('company_id')orself.env.company.id)

    incoterm_id=fields.Many2one('account.incoterms','Incoterm',states={'done':[('readonly',True)]},help="InternationalCommercialTermsareaseriesofpredefinedcommercialtermsusedininternationaltransactions.")

    picking_count=fields.Integer(compute='_compute_picking',string='Pickingcount',default=0,store=True)
    picking_ids=fields.Many2many('stock.picking',compute='_compute_picking',string='Receptions',copy=False,store=True)

    picking_type_id=fields.Many2one('stock.picking.type','DeliverTo',states=Purchase.READONLY_STATES,required=True,default=_default_picking_type,domain="['|',('warehouse_id','=',False),('warehouse_id.company_id','=',company_id)]",
        help="Thiswilldetermineoperationtypeofincomingshipment")
    default_location_dest_id_usage=fields.Selection(related='picking_type_id.default_location_dest_id.usage',string='DestinationLocationType',
        help="TechnicalfieldusedtodisplaytheDropShipAddress",readonly=True)
    group_id=fields.Many2one('procurement.group',string="ProcurementGroup",copy=False)
    is_shipped=fields.Boolean(compute="_compute_is_shipped")
    effective_date=fields.Datetime("EffectiveDate",compute='_compute_effective_date',store=True,copy=False,
        help="Completiondateofthefirstreceiptorder.")
    on_time_rate=fields.Float(related='partner_id.on_time_rate',compute_sudo=False)

    @api.depends('order_line.move_ids.picking_id')
    def_compute_picking(self):
        fororderinself:
            pickings=order.order_line.mapped('move_ids.picking_id')
            order.picking_ids=pickings
            order.picking_count=len(pickings)

    @api.depends('picking_ids.date_done')
    def_compute_effective_date(self):
        fororderinself:
            pickings=order.picking_ids.filtered(lambdax:x.state=='done'andx.location_dest_id.usage=='internal'andx.date_done)
            order.effective_date=min(pickings.mapped('date_done'),default=False)

    @api.depends('picking_ids','picking_ids.state')
    def_compute_is_shipped(self):
        fororderinself:
            iforder.picking_idsandall(x.statein['done','cancel']forxinorder.picking_ids):
                order.is_shipped=True
            else:
                order.is_shipped=False

    @api.onchange('picking_type_id')
    def_onchange_picking_type_id(self):
        ifself.picking_type_id.default_location_dest_id.usage!='customer':
            self.dest_address_id=False

    @api.onchange('company_id')
    def_onchange_company_id(self):
        p_type=self.picking_type_id
        ifnot(p_typeandp_type.code=='incoming'and(p_type.warehouse_id.company_id==self.company_idornotp_type.warehouse_id)):
            self.picking_type_id=self._get_picking_type(self.company_id.id)

    #--------------------------------------------------
    #CRUD
    #--------------------------------------------------

    defwrite(self,vals):
        ifvals.get('order_line')andself.state=='purchase':
            fororderinself:
                pre_order_line_qty={order_line:order_line.product_qtyfororder_lineinorder.mapped('order_line')}
        res=super(PurchaseOrder,self).write(vals)
        ifvals.get('order_line')andself.state=='purchase':
            fororderinself:
                to_log={}
                fororder_lineinorder.order_line:
                    ifpre_order_line_qty.get(order_line,False)andfloat_compare(pre_order_line_qty[order_line],order_line.product_qty,precision_rounding=order_line.product_uom.rounding)>0:
                        to_log[order_line]=(order_line.product_qty,pre_order_line_qty[order_line])
                ifto_log:
                    order._log_decrease_ordered_quantity(to_log)
        returnres

    #--------------------------------------------------
    #Actions
    #--------------------------------------------------

    defbutton_approve(self,force=False):
        result=super(PurchaseOrder,self).button_approve(force=force)
        self._create_picking()
        returnresult

    defbutton_cancel(self):
        fororderinself:
            formoveinorder.order_line.mapped('move_ids'):
                ifmove.state=='done':
                    raiseUserError(_('Unabletocancelpurchaseorder%sassomereceptionshavealreadybeendone.')%(order.name))
            #IftheproductisMTO,changetheprocure_methodoftheclosestmovetopurchasetoMTS.
            #Thepurposeistolinkthepothattheuserwillmanuallygeneratetotheexistingmoves'schain.
            iforder.statein('draft','sent','toapprove','purchase'):
                fororder_lineinorder.order_line:
                    order_line.move_ids._action_cancel()
                    iforder_line.move_dest_ids:
                        move_dest_ids=order_line.move_dest_ids
                        iforder_line.propagate_cancel:
                            move_dest_ids._action_cancel()
                        else:
                            move_dest_ids.write({'procure_method':'make_to_stock'})
                            move_dest_ids._recompute_state()

            forpickinorder.picking_ids.filtered(lambdar:r.state!='cancel'):
                pick.action_cancel()

            order.order_line.write({'move_dest_ids':[(5,0,0)]})

        returnsuper(PurchaseOrder,self).button_cancel()

    defaction_view_picking(self):
        """Thisfunctionreturnsanactionthatdisplayexistingpickingordersofgivenpurchaseorderids.Whenonlyonefound,showthepickingimmediately.
        """
        result=self.env["ir.actions.actions"]._for_xml_id('stock.action_picking_tree_all')
        #overridethecontexttogetridofthedefaultfilteringonoperationtype
        result['context']={'default_partner_id':self.partner_id.id,'default_origin':self.name,'default_picking_type_id':self.picking_type_id.id}
        pick_ids=self.mapped('picking_ids')
        #choosetheview_modeaccordingly
        ifnotpick_idsorlen(pick_ids)>1:
            result['domain']="[('id','in',%s)]"%(pick_ids.ids)
        eliflen(pick_ids)==1:
            res=self.env.ref('stock.view_picking_form',False)
            form_view=[(resandres.idorFalse,'form')]
            if'views'inresult:
                result['views']=form_view+[(state,view)forstate,viewinresult['views']ifview!='form']
            else:
                result['views']=form_view
            result['res_id']=pick_ids.id
        returnresult

    def_prepare_invoice(self):
        invoice_vals=super()._prepare_invoice()
        invoice_vals['invoice_incoterm_id']=self.incoterm_id.id
        returninvoice_vals

    #--------------------------------------------------
    #Businessmethods
    #--------------------------------------------------

    def_log_decrease_ordered_quantity(self,purchase_order_lines_quantities):

        def_keys_in_sorted(move):
            """sortbypickingandtheresponsiblefortheproductthe
            move.
            """
            return(move.picking_id.id,move.product_id.responsible_id.id)

        def_keys_in_groupby(move):
            """groupbypickingandtheresponsiblefortheproductthe
            move.
            """
            return(move.picking_id,move.product_id.responsible_id)

        def_render_note_exception_quantity_po(order_exceptions):
            order_line_ids=self.env['purchase.order.line'].browse([order_line.idfororderinorder_exceptions.values()fororder_lineinorder[0]])
            purchase_order_ids=order_line_ids.mapped('order_id')
            move_ids=self.env['stock.move'].concat(*rendering_context.keys())
            impacted_pickings=move_ids.mapped('picking_id')._get_impacted_pickings(move_ids)-move_ids.mapped('picking_id')
            values={
                'purchase_order_ids':purchase_order_ids,
                'order_exceptions':order_exceptions.values(),
                'impacted_pickings':impacted_pickings,
            }
            returnself.env.ref('purchase_stock.exception_on_po')._render(values=values)

        documents=self.env['stock.picking']._log_activity_get_documents(purchase_order_lines_quantities,'move_ids','DOWN',_keys_in_sorted,_keys_in_groupby)
        filtered_documents={}
        for(parent,responsible),rendering_contextindocuments.items():
            ifparent._name=='stock.picking':
                ifparent.statein['cancel','done']:
                    continue
            filtered_documents[(parent,responsible)]=rendering_context
        self.env['stock.picking']._log_activity(_render_note_exception_quantity_po,filtered_documents)

    def_get_destination_location(self):
        self.ensure_one()
        ifself.dest_address_id:
            returnself.dest_address_id.property_stock_customer.id
        returnself.picking_type_id.default_location_dest_id.id

    @api.model
    def_get_picking_type(self,company_id):
        picking_type=self.env['stock.picking.type'].search([('code','=','incoming'),('warehouse_id.company_id','=',company_id)])
        ifnotpicking_type:
            picking_type=self.env['stock.picking.type'].search([('code','=','incoming'),('warehouse_id','=',False)])
        returnpicking_type[:1]

    def_prepare_picking(self):
        ifnotself.group_id:
            self.group_id=self.group_id.create({
                'name':self.name,
                'partner_id':self.partner_id.id
            })
        ifnotself.partner_id.property_stock_supplier.id:
            raiseUserError(_("YoumustsetaVendorLocationforthispartner%s",self.partner_id.name))
        return{
            'picking_type_id':self.picking_type_id.id,
            'partner_id':self.partner_id.id,
            'user_id':False,
            'date':self.date_order,
            'origin':self.name,
            'location_dest_id':self._get_destination_location(),
            'location_id':self.partner_id.property_stock_supplier.id,
            'company_id':self.company_id.id,
        }

    def_create_picking(self):
        StockPicking=self.env['stock.picking']
        fororderinself.filtered(lambdapo:po.statein('purchase','done')):
            ifany(product.typein['product','consu']forproductinorder.order_line.product_id):
                order=order.with_company(order.company_id)
                pickings=order.picking_ids.filtered(lambdax:x.statenotin('done','cancel'))
                ifnotpickings:
                    res=order._prepare_picking()
                    picking=StockPicking.with_user(SUPERUSER_ID).create(res)
                else:
                    picking=pickings[0]
                moves=order.order_line._create_stock_moves(picking)
                moves=moves.filtered(lambdax:x.statenotin('done','cancel'))._action_confirm()
                seq=0
                formoveinsorted(moves,key=lambdamove:move.date):
                    seq+=5
                    move.sequence=seq
                moves._action_assign()
                picking.message_post_with_view('mail.message_origin_link',
                    values={'self':picking,'origin':order},
                    subtype_id=self.env.ref('mail.mt_note').id)
        returnTrue

    def_add_picking_info(self,activity):
        """HelpermethodtoaddpickinginfototheDateUpdatedactivitywhen
        venderupdatesdate_plannedofthepolines.
        """
        validated_picking=self.picking_ids.filtered(lambdap:p.state=='done')
        ifvalidated_picking:
            activity.note+=_("<p>Thosedatescouldn’tbemodifiedaccordinglyonthereceipt%swhichhadalreadybeenvalidated.</p>")%validated_picking[0].name
        elifnotself.picking_ids:
            activity.note+=_("<p>Correspondingreceiptnotfound.</p>")
        else:
            activity.note+=_("<p>Thosedateshavebeenupdatedaccordinglyonthereceipt%s.</p>")%self.picking_ids[0].name

    def_create_update_date_activity(self,updated_dates):
        activity=super()._create_update_date_activity(updated_dates)
        self._add_picking_info(activity)

    def_update_update_date_activity(self,updated_dates,activity):
        #removeoldpickinginfotoupdateit
        note_lines=activity.note.split('<p>')
        note_lines.pop()
        activity.note='<p>'.join(note_lines)
        super()._update_update_date_activity(updated_dates,activity)
        self._add_picking_info(activity)

    @api.model
    def_get_orders_to_remind(self):
        """Whenautosendingremindermails,don'tsendforpurchaseorderwith
        validatedreceipts."""
        returnsuper()._get_orders_to_remind().filtered(lambdap:notp.effective_date)


classPurchaseOrderLine(models.Model):
    _inherit='purchase.order.line'

    qty_received_method=fields.Selection(selection_add=[('stock_moves','StockMoves')])

    move_ids=fields.One2many('stock.move','purchase_line_id',string='Reservation',readonly=True,copy=False)
    orderpoint_id=fields.Many2one('stock.warehouse.orderpoint','Orderpoint',copy=False,index=True)
    move_dest_ids=fields.One2many('stock.move','created_purchase_line_id','DownstreamMoves')
    product_description_variants=fields.Char('CustomDescription')
    propagate_cancel=fields.Boolean('Propagatecancellation',default=True)

    def_compute_qty_received_method(self):
        super(PurchaseOrderLine,self)._compute_qty_received_method()
        forlineinself.filtered(lambdal:notl.display_type):
            ifline.product_id.typein['consu','product']:
                line.qty_received_method='stock_moves'

    @api.depends('move_ids.state','move_ids.product_uom_qty','move_ids.product_uom')
    def_compute_qty_received(self):
        from_stock_lines=self.filtered(lambdaorder_line:order_line.qty_received_method=='stock_moves')
        super(PurchaseOrderLine,self-from_stock_lines)._compute_qty_received()
        forlineinself:
            ifline.qty_received_method=='stock_moves':
                total=0.0
                #IncaseofaBOMinkit,theproductsdelivereddonotcorrespondtotheproductsin
                #thePO.Therefore,wecanskipthemsincetheywillbehandledlateron.
                formoveinline.move_ids.filtered(lambdam:m.product_id==line.product_id):
                    ifmove.state=='done':
                        ifmove._is_purchase_return():
                            ifmove.to_refund:
                                total-=move.product_uom._compute_quantity(move.product_uom_qty,line.product_uom,rounding_method='HALF-UP')
                        elifmove.origin_returned_move_idandmove.origin_returned_move_id._is_dropshipped()andnotmove._is_dropshipped_returned():
                            #Edgecase:thedropshipisreturnedtothestock,notothesupplier.
                            #Inthiscase,thereceivedquantityonthePOissetalthoughwedidn't
                            #receivetheproductphysicallyinourstock.Toavoidcountingthe
                            #quantitytwice,wedonothing.
                            pass
                        else:
                            total+=move.product_uom._compute_quantity(move.product_uom_qty,line.product_uom,rounding_method='HALF-UP')
                line._track_qty_received(total)
                line.qty_received=total

    @api.model_create_multi
    defcreate(self,vals_list):
        lines=super(PurchaseOrderLine,self).create(vals_list)
        lines.filtered(lambdal:l.order_id.state=='purchase')._create_or_update_picking()
        returnlines

    defwrite(self,values):
        forlineinself.filtered(lambdal:notl.display_type):
            #POdate_plannedoverridesanyPOlinedate_plannedvalues
            ifvalues.get('date_planned'):
                new_date=fields.Datetime.to_datetime(values['date_planned'])
                self._update_move_date_deadline(new_date)
        lines=self.filtered(lambdal:l.order_id.state=='purchase')
        previous_product_uom_qty={line.id:line.product_uom_qtyforlineinlines}
        previous_product_qty={line.id:line.product_qtyforlineinlines}
        result=super(PurchaseOrderLine,self).write(values)
        if'price_unit'invalues:
            forlineinlines:
                #Avoidupdatingkitcomponents'stock.move
                moves=line.move_ids.filtered(lambdas:s.statenotin('cancel','done')ands.product_id==line.product_id)
                moves.write({'price_unit':line._get_stock_move_price_unit()})
        if'product_qty'invalues:
            lines=lines.filtered(lambdal:float_compare(previous_product_qty[l.id],l.product_qty,precision_rounding=l.product_uom.rounding)!=0)
            lines.with_context(previous_product_qty=previous_product_uom_qty)._create_or_update_picking()
        returnresult

    defunlink(self):
        self.move_ids._action_cancel()

        ppg_cancel_lines=self.filtered(lambdaline:line.propagate_cancel)
        ppg_cancel_lines.move_dest_ids._action_cancel()

        not_ppg_cancel_lines=self.filtered(lambdaline:notline.propagate_cancel)
        not_ppg_cancel_lines.move_dest_ids.write({'procure_method':'make_to_stock'})
        not_ppg_cancel_lines.move_dest_ids._recompute_state()

        returnsuper().unlink()

    #--------------------------------------------------
    #Businessmethods
    #--------------------------------------------------

    def_update_move_date_deadline(self,new_date):
        """Updatescorrespondingmovepickinglinedeadlinedatesthatarenotyetcompleted."""
        moves_to_update=self.move_ids.filtered(lambdam:m.statenotin('done','cancel'))
        ifnotmoves_to_update:
            moves_to_update=self.move_dest_ids.filtered(lambdam:m.statenotin('done','cancel'))
        formoveinmoves_to_update:
            move.date_deadline=new_date+relativedelta(days=move.company_id.po_lead)

    def_create_or_update_picking(self):
        forlineinself:
            ifline.product_idandline.product_id.typein('product','consu'):
                #Preventdecreasingbelowreceivedquantity
                iffloat_compare(line.product_qty,line.qty_received,line.product_uom.rounding)<0:
                    raiseUserError(_('Youcannotdecreasetheorderedquantitybelowthereceivedquantity.\n'
                                      'Createareturnfirst.'))

                iffloat_compare(line.product_qty,line.qty_invoiced,line.product_uom.rounding)==-1:
                    #Ifthequantityisnowbelowtheinvoicedquantity,createanactivityonthevendorbill
                    #invitingtheusertocreatearefund.
                    line.invoice_lines[0].move_id.activity_schedule(
                        'mail.mail_activity_data_warning',
                        note=_('Thequantitiesonyourpurchaseorderindicatelessthanbilled.Youshouldaskforarefund.'))

                #Iftheuserincreasedquantityofexistinglineorcreatedanewline
                pickings=line.order_id.picking_ids.filtered(lambdax:x.statenotin('done','cancel')andx.location_dest_id.usagein('internal','transit','customer'))
                picking=pickingsandpickings[0]orFalse
                ifnotpicking:
                    res=line.order_id._prepare_picking()
                    picking=self.env['stock.picking'].create(res)

                moves=line._create_stock_moves(picking)
                moves._action_confirm()._action_assign()

    def_get_stock_move_price_unit(self):
        self.ensure_one()
        line=self[0]
        order=line.order_id
        price_unit=line.price_unit
        price_unit_prec=self.env['decimal.precision'].precision_get('ProductPrice')
        ifline.taxes_id:
            qty=line.product_qtyor1
            price_unit=line.taxes_id.with_context(round=False).compute_all(
                price_unit,currency=line.order_id.currency_id,quantity=qty,product=line.product_id,partner=line.order_id.partner_id
            )['total_void']
            price_unit=float_round(price_unit/qty,precision_digits=price_unit_prec)
        ifline.product_uom.id!=line.product_id.uom_id.id:
            price_unit*=line.product_uom.factor/line.product_id.uom_id.factor
        iforder.currency_id!=order.company_id.currency_id:
            price_unit=order.currency_id._convert(
                price_unit,order.company_id.currency_id,self.company_id,self.date_orderorfields.Date.today(),round=False)
        returnprice_unit

    def_prepare_stock_moves(self,picking):
        """Preparethestockmovesdataforoneorderline.Thisfunctionreturnsalistof
        dictionaryreadytobeusedinstock.move'screate()
        """
        self.ensure_one()
        res=[]
        ifself.product_id.typenotin['product','consu']:
            returnres

        price_unit=self._get_stock_move_price_unit()
        qty=self._get_qty_procurement()

        move_dests=self.move_dest_ids
        ifnotmove_dests:
            move_dests=self.move_ids.move_dest_ids.filtered(lambdam:m.state!='cancel'andnotm.location_dest_id.usage=='supplier')

        ifnotmove_dests:
            qty_to_attach=0
            qty_to_push=self.product_qty-qty
        else:
            move_dests_initial_demand=self.product_id.uom_id._compute_quantity(
                sum(move_dests.filtered(lambdam:m.state!='cancel'andnotm.location_dest_id.usage=='supplier').mapped('product_qty')),
                self.product_uom,rounding_method='HALF-UP')
            qty_to_attach=min(self.product_qty,move_dests_initial_demand)-qty
            qty_to_push=self.product_qty-move_dests_initial_demand

        iffloat_compare(qty_to_attach,0.0,precision_rounding=self.product_uom.rounding)>0:
            product_uom_qty,product_uom=self.product_uom._adjust_uom_quantities(qty_to_attach,self.product_id.uom_id)
            res.append(self._prepare_stock_move_vals(picking,price_unit,product_uom_qty,product_uom))
        iffloat_compare(qty_to_push,0.0,precision_rounding=self.product_uom.rounding)>0:
            product_uom_qty,product_uom=self.product_uom._adjust_uom_quantities(qty_to_push,self.product_id.uom_id)
            extra_move_vals=self._prepare_stock_move_vals(picking,price_unit,product_uom_qty,product_uom)
            extra_move_vals['move_dest_ids']=False #don'tattach
            res.append(extra_move_vals)
        returnres

    def_get_qty_procurement(self):
        self.ensure_one()
        qty=0.0
        outgoing_moves,incoming_moves=self._get_outgoing_incoming_moves()
        formoveinoutgoing_moves:
            qty-=move.product_uom._compute_quantity(move.product_uom_qty,self.product_uom,rounding_method='HALF-UP')
        formoveinincoming_moves:
            qty+=move.product_uom._compute_quantity(move.product_uom_qty,self.product_uom,rounding_method='HALF-UP')
        returnqty

    def_check_orderpoint_picking_type(self):
        warehouse_loc=self.order_id.picking_type_id.warehouse_id.view_location_id
        dest_loc=self.move_dest_ids.location_idorself.orderpoint_id.location_id
        ifwarehouse_locanddest_locanddest_loc.get_warehouse()andnotwarehouse_loc.parent_pathindest_loc[0].parent_path:
            raiseUserError(_('Fortheproduct%s,thewarehouseoftheoperationtype(%s)isinconsistentwiththelocation(%s)ofthereorderingrule(%s).Changetheoperationtypeorcanceltherequestforquotation.',
                              self.product_id.display_name,self.order_id.picking_type_id.display_name,self.orderpoint_id.location_id.display_name,self.orderpoint_id.display_name))

    def_prepare_stock_move_vals(self,picking,price_unit,product_uom_qty,product_uom):
        self.ensure_one()
        self._check_orderpoint_picking_type()
        product=self.product_id.with_context(lang=self.order_id.dest_address_id.langorself.env.user.lang)
        description_picking=product._get_description(self.order_id.picking_type_id)
        ifself.product_description_variants:
            description_picking+="\n"+self.product_description_variants
        date_planned=self.date_plannedorself.order_id.date_planned
        return{
            #truncateto2000toavoidtriggeringindexlimiterror
            #TODO:removeindexinmaster?
            'name':(self.product_id.display_nameor'')[:2000],
            'product_id':self.product_id.id,
            'date':date_planned,
            'date_deadline':date_planned+relativedelta(days=self.order_id.company_id.po_lead),
            'location_id':self.order_id.partner_id.property_stock_supplier.id,
            'location_dest_id':(self.orderpoint_idandnot(self.move_ids|self.move_dest_ids))andself.orderpoint_id.location_id.idorself.order_id._get_destination_location(),
            'picking_id':picking.id,
            'partner_id':self.order_id.dest_address_id.id,
            'move_dest_ids':[(4,x)forxinself.move_dest_ids.ids],
            'state':'draft',
            'purchase_line_id':self.id,
            'company_id':self.order_id.company_id.id,
            'price_unit':price_unit,
            'picking_type_id':self.order_id.picking_type_id.id,
            'group_id':self.order_id.group_id.id,
            'origin':self.order_id.name,
            'description_picking':description_picking,
            'propagate_cancel':self.propagate_cancel,
            'warehouse_id':self.order_id.picking_type_id.warehouse_id.id,
            'product_uom_qty':product_uom_qty,
            'product_uom':product_uom.id,
            'sequence':self.sequence,
        }

    @api.model
    def_prepare_purchase_order_line_from_procurement(self,product_id,product_qty,product_uom,company_id,values,po):
        line_description=''
        ifvalues.get('product_description_variants'):
            line_description=values['product_description_variants']
        supplier=values.get('supplier')
        res=self._prepare_purchase_order_line(product_id,product_qty,product_uom,company_id,supplier,po)
        #Weneedtokeepthevendornamesetin_prepare_purchase_order_line.Toavoidredundancy
        #inthelinename,weaddtheline_descriptiononlyifdifferentfromtheproductname.
        #Thisway,weshoudnotloseanyvaluableinformation.
        ifline_descriptionandproduct_id.name!=line_description:
            res['name']+='\n'+line_description
        res['move_dest_ids']=[(4,x.id)forxinvalues.get('move_dest_ids',[])]
        res['orderpoint_id']=values.get('orderpoint_id',False)andvalues.get('orderpoint_id').id
        res['propagate_cancel']=values.get('propagate_cancel')
        res['product_description_variants']=values.get('product_description_variants')
        returnres

    def_create_stock_moves(self,picking):
        values=[]
        forlineinself.filtered(lambdal:notl.display_type):
            forvalinline._prepare_stock_moves(picking):
                values.append(val)
            line.move_dest_ids.created_purchase_line_id=False

        returnself.env['stock.move'].create(values)

    def_find_candidate(self,product_id,product_qty,product_uom,location_id,name,origin,company_id,values):
        """Returntherecordinselfwheretheprocumentwithvaluespassedas
        argscanbemerged.Ifitreturnsanemptyrecordthenanewlinewill
        becreated.
        """
        description_picking=''
        ifvalues.get('product_description_variants'):
            description_picking=values['product_description_variants']
        lines=self.filtered(
            lambdal:l.propagate_cancel==values['propagate_cancel']
            and(l.orderpoint_id==values['orderpoint_id']ifvalues['orderpoint_id']andnotvalues['move_dest_ids']elseTrue)
        )

        #Incase'product_description_variants'isinthevalues,wealsofilteronthePOline
        #name.Thisway,wecanmergelineswiththesamedescription.Todoso,weneedthe
        #productnameinthecontextofthePOpartner.
        iflinesandvalues.get('product_description_variants'):
            partner=self.mapped('order_id.partner_id')[:1]
            product_lang=product_id.with_context(
                lang=partner.lang,
                partner_id=partner.id,
            )
            name=product_lang.display_name
            ifproduct_lang.description_purchase:
                name+='\n'+product_lang.description_purchase
            lines=lines.filtered(lambdal:l.name==name+'\n'+description_picking)
            iflines:
                returnlines[0]

        returnlinesandlines[0]orself.env['purchase.order.line']

    def_get_outgoing_incoming_moves(self):
        outgoing_moves=self.env['stock.move']
        incoming_moves=self.env['stock.move']

        formoveinself.move_ids.filtered(lambdar:r.state!='cancel'andnotr.scrappedandself.product_id==r.product_id):
            ifmove.location_dest_id.usage=="supplier"andmove.to_refund:
                outgoing_moves|=move
            elifmove.location_dest_id.usage!="supplier":
                ifnotmove.origin_returned_move_idor(move.origin_returned_move_idandmove.to_refund):
                    incoming_moves|=move

        returnoutgoing_moves,incoming_moves

    def_update_date_planned(self,updated_date):
        move_to_update=self.move_ids.filtered(lambdam:m.statenotin['done','cancel'])
        ifnotself.move_idsormove_to_update: #Onlychangethedateifthereisnomovedoneornone
            super()._update_date_planned(updated_date)
        ifmove_to_update:
            self._update_move_date_deadline(updated_date)

    @api.model
    def_update_qty_received_method(self):
        """Updateqty_received_methodforoldPObeforeinstallthismodule."""
        self.search(['!',('state','in',['purchase','done'])])._compute_qty_received_method()
