#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_
fromflectra.tools.float_utilsimportfloat_round,float_is_zero
fromflectra.exceptionsimportUserError
fromflectra.osv.expressionimportAND

classStockPicking(models.Model):
    _inherit='stock.picking'

    purchase_id=fields.Many2one('purchase.order',related='move_lines.purchase_line_id.order_id',
        string="PurchaseOrders",readonly=True)


classStockMove(models.Model):
    _inherit='stock.move'

    purchase_line_id=fields.Many2one('purchase.order.line',
        'PurchaseOrderLine',ondelete='setnull',index=True,readonly=True)
    created_purchase_line_id=fields.Many2one('purchase.order.line',
        'CreatedPurchaseOrderLine',ondelete='setnull',readonly=True,copy=False,index=True)

    @api.model
    def_prepare_merge_moves_distinct_fields(self):
        distinct_fields=super(StockMove,self)._prepare_merge_moves_distinct_fields()
        distinct_fields+=['purchase_line_id','created_purchase_line_id']
        returndistinct_fields

    @api.model
    def_prepare_merge_move_sort_method(self,move):
        move.ensure_one()
        keys_sorted=super(StockMove,self)._prepare_merge_move_sort_method(move)
        keys_sorted+=[move.purchase_line_id.id,move.created_purchase_line_id.id]
        returnkeys_sorted

    def_get_price_unit(self):
        """Returnstheunitpriceforthemove"""
        self.ensure_one()
        ifnotself.origin_returned_move_idandself.purchase_line_idandself.product_id.id==self.purchase_line_id.product_id.id:
            price_unit_prec=self.env['decimal.precision'].precision_get('ProductPrice')
            line=self.purchase_line_id
            order=line.order_id
            price_unit=line.price_unit
            ifline.taxes_id:
                qty=line.product_qtyor1
                price_unit=line.taxes_id.with_context(round=False).compute_all(price_unit,currency=line.order_id.currency_id,quantity=qty)['total_void']
                price_unit=float_round(price_unit/qty,precision_digits=price_unit_prec)
            ifline.product_uom.id!=line.product_id.uom_id.id:
                price_unit*=line.product_uom.factor/line.product_id.uom_id.factor
            iforder.currency_id!=order.company_id.currency_id:
                #Thedatemustbetoday,andnotthedateofthemovesincethemovemoveisstill
                #inassignedstate.However,themovedateisthescheduleddateuntilmoveis
                #done,thendateofactualmoveprocessing.See:
                #https://github.com/flectra/flectra/blob/2f789b6863407e63f90b3a2d4cc3be09815f7002/addons/stock/models/stock_move.py#L36
                price_unit=order.currency_id._convert(
                    price_unit,order.company_id.currency_id,order.company_id,fields.Date.context_today(self),round=False)
            returnprice_unit
        returnsuper(StockMove,self)._get_price_unit()

    def_generate_valuation_lines_data(self,partner_id,qty,debit_value,credit_value,debit_account_id,credit_account_id,description):
        """Overriddenfromstock_accounttosupportamount_currencyonvaluationlinesgeneratedfrompo
        """
        self.ensure_one()

        rslt=super(StockMove,self)._generate_valuation_lines_data(partner_id,qty,debit_value,credit_value,debit_account_id,credit_account_id,description)
        ifself.purchase_line_id:
            purchase_currency=self.purchase_line_id.currency_id
            ifpurchase_currency!=self.company_id.currency_id:
                if(self.purchase_line_id.product_id.cost_method=='standard'):
                    purchase_price_unit=self.purchase_line_id.product_id.cost_currency_id._convert(
                        self.purchase_line_id.product_id.standard_price,
                        purchase_currency,
                        self.company_id,
                        self.date,
                        round=False,
                    )
                else:
                    #Donotuseprice_unitsincewewantthepricetaxexcluded.Andbytheway,qty
                    #isintheUOMoftheproduct,nottheUOMofthePOline.
                    purchase_price_unit=(
                        self.purchase_line_id.price_subtotal/self.purchase_line_id.product_uom_qty
                        ifself.purchase_line_id.product_uom_qty
                        elseself.purchase_line_id.price_unit
                    )
                currency_move_valuation=purchase_currency.round(purchase_price_unit*abs(qty))
                rslt['credit_line_vals']['amount_currency']=rslt['credit_line_vals']['credit']and-currency_move_valuationorcurrency_move_valuation
                rslt['credit_line_vals']['currency_id']=purchase_currency.id
                rslt['debit_line_vals']['amount_currency']=rslt['debit_line_vals']['credit']and-currency_move_valuationorcurrency_move_valuation
                rslt['debit_line_vals']['currency_id']=purchase_currency.id
        returnrslt

    def_prepare_extra_move_vals(self,qty):
        vals=super(StockMove,self)._prepare_extra_move_vals(qty)
        vals['purchase_line_id']=self.purchase_line_id.id
        returnvals

    def_prepare_move_split_vals(self,uom_qty):
        vals=super(StockMove,self)._prepare_move_split_vals(uom_qty)
        vals['purchase_line_id']=self.purchase_line_id.id
        returnvals

    def_prepare_procurement_values(self):
        proc_values=super()._prepare_procurement_values()
        ifself.restrict_partner_id:
            proc_values['supplierinfo_name']=self.restrict_partner_id
            self.restrict_partner_id=False
        returnproc_values

    def_clean_merged(self):
        super(StockMove,self)._clean_merged()
        self.write({'created_purchase_line_id':False})

    def_get_upstream_documents_and_responsibles(self,visited):
        ifself.created_purchase_line_idandself.created_purchase_line_id.statenotin('done','cancel'):
            return[(self.created_purchase_line_id.order_id,self.created_purchase_line_id.order_id.user_id,visited)]
        elifself.purchase_line_idandself.purchase_line_id.statenotin('done','cancel'):
            return[(self.purchase_line_id.order_id,self.purchase_line_id.order_id.user_id,visited)]
        else:
            returnsuper(StockMove,self)._get_upstream_documents_and_responsibles(visited)

    def_get_related_invoices(self):
        """Overriddentoreturnthevendorbillsrelatedtothisstockmove.
        """
        rslt=super(StockMove,self)._get_related_invoices()
        rslt+=self.mapped('picking_id.purchase_id.invoice_ids').filtered(lambdax:x.state=='posted')
        returnrslt


    def_get_source_document(self):
        res=super()._get_source_document()
        returnself.purchase_line_id.order_idorres

    def_get_valuation_price_and_qty(self,related_aml,to_curr):
        valuation_price_unit_total=0
        valuation_total_qty=0
        forval_stock_moveinself:
            #Incaseval_stock_moveisareturnmove,itsvaluationentrieshavebeenmadewiththe
            #currencyratecorrespondingtotheoriginalstockmove
            valuation_date=val_stock_move.origin_returned_move_id.dateorval_stock_move.date
            svl=val_stock_move.with_context(active_test=False).mapped('stock_valuation_layer_ids').filtered(
                lambdal:l.quantity)
            layers_qty=sum(svl.mapped('quantity'))
            layers_values=sum(svl.mapped('value'))
            valuation_price_unit_total+=related_aml.company_currency_id._convert(
                layers_values,to_curr,related_aml.company_id,valuation_date,round=False,
            )
            valuation_total_qty+=layers_qty
        iffloat_is_zero(valuation_total_qty,precision_rounding=related_aml.product_uom_id.roundingorrelated_aml.product_id.uom_id.rounding):
            raiseUserError(
                _('Flectraisnotabletogeneratetheanglosaxonentries.Thetotalvaluationof%siszero.')%related_aml.product_id.display_name)
        returnvaluation_price_unit_total,valuation_total_qty

    def_is_purchase_return(self):
        self.ensure_one()
        returnself.location_dest_id.usage=="supplier"or(
                self.location_dest_id.usage=="internal"
                andself.location_id.usage!="supplier"
                andself.warehouse_id
                andself.location_dest_idnotinself.env["stock.location"].search([("id","child_of",self.warehouse_id.view_location_id.id)])
        )


classStockWarehouse(models.Model):
    _inherit='stock.warehouse'

    buy_to_resupply=fields.Boolean('BuytoResupply',default=True,
                                     help="Whenproductsarebought,theycanbedeliveredtothiswarehouse")
    buy_pull_id=fields.Many2one('stock.rule','Buyrule')

    def_get_global_route_rules_values(self):
        rules=super(StockWarehouse,self)._get_global_route_rules_values()
        location_id=self.in_type_id.default_location_dest_id
        rules.update({
            'buy_pull_id':{
                'depends':['reception_steps','buy_to_resupply'],
                'create_values':{
                    'action':'buy',
                    'picking_type_id':self.in_type_id.id,
                    'group_propagation_option':'none',
                    'company_id':self.company_id.id,
                    'route_id':self._find_global_route('purchase_stock.route_warehouse0_buy',_('Buy')).id,
                    'propagate_cancel':self.reception_steps!='one_step',
                },
                'update_values':{
                    'active':self.buy_to_resupply,
                    'name':self._format_rulename(location_id,False,'Buy'),
                    'location_id':location_id.id,
                    'propagate_cancel':self.reception_steps!='one_step',
                }
            }
        })
        returnrules

    def_get_all_routes(self):
        routes=super(StockWarehouse,self)._get_all_routes()
        routes|=self.filtered(lambdaself:self.buy_to_resupplyandself.buy_pull_idandself.buy_pull_id.route_id).mapped('buy_pull_id').mapped('route_id')
        returnroutes

    defget_rules_dict(self):
        result=super(StockWarehouse,self).get_rules_dict()
        forwarehouseinself:
            result[warehouse.id].update(warehouse._get_receive_rules_dict())
        returnresult

    def_get_routes_values(self):
        routes=super(StockWarehouse,self)._get_routes_values()
        routes.update(self._get_receive_routes_values('buy_to_resupply'))
        returnroutes

    def_update_name_and_code(self,name=False,code=False):
        res=super(StockWarehouse,self)._update_name_and_code(name,code)
        warehouse=self[0]
        #changethebuystockrulename
        ifwarehouse.buy_pull_idandname:
            warehouse.buy_pull_id.write({'name':warehouse.buy_pull_id.name.replace(warehouse.name,name,1)})
        returnres


classReturnPicking(models.TransientModel):
    _inherit="stock.return.picking"

    def_prepare_move_default_values(self,return_line,new_picking):
        vals=super(ReturnPicking,self)._prepare_move_default_values(return_line,new_picking)
        vals['purchase_line_id']=return_line.move_id.purchase_line_id.id
        returnvals


classOrderpoint(models.Model):
    _inherit="stock.warehouse.orderpoint"

    show_supplier=fields.Boolean('Showsuppliercolumn',compute='_compute_show_suppplier')
    supplier_id=fields.Many2one(
        'product.supplierinfo',string='Vendor',check_company=True,
        domain="['|',('product_id','=',product_id),'&',('product_id','=',False),('product_tmpl_id','=',product_tmpl_id)]")

    @api.depends('product_id.purchase_order_line_ids.product_qty','product_id.purchase_order_line_ids.state')
    def_compute_qty(self):
        """Extendtoaddmoredependsvalues"""
        returnsuper()._compute_qty()

    @api.depends('route_id')
    def_compute_show_suppplier(self):
        buy_route=[]
        forresinself.env['stock.rule'].search_read([('action','=','buy')],['route_id']):
            buy_route.append(res['route_id'][0])
        fororderpointinself:
            orderpoint.show_supplier=orderpoint.route_id.idinbuy_route

    defaction_view_purchase(self):
        """Thisfunctionreturnsanactionthatdisplayexisting
        purchaseordersofgivenorderpoint.
        """
        result=self.env['ir.actions.act_window']._for_xml_id('purchase.purchase_rfq')

        #RemvovethecontextsincetheactionbasicallydisplayRFQandnotPO.
        result['context']={}
        order_line_ids=self.env['purchase.order.line'].search([('orderpoint_id','=',self.id)])
        purchase_ids=order_line_ids.mapped('order_id')

        result['domain']="[('id','in',%s)]"%(purchase_ids.ids)

        returnresult

    def_get_replenishment_order_notification(self):
        self.ensure_one()
        domain=[('orderpoint_id','in',self.ids)]
        ifself.env.context.get('written_after'):
            domain=AND([domain,[('write_date','>',self.env.context.get('written_after'))]])
        order=self.env['purchase.order.line'].search(domain,limit=1).order_id
        iforder:
            action=self.env.ref('purchase.action_rfq_form')
            return{
                'type':'ir.actions.client',
                'tag':'display_notification',
                'params':{
                    'title':_('Thefollowingreplenishmentorderhasbeengenerated'),
                    'message':'%s',
                    'links':[{
                        'label':order.display_name,
                        'url':f'#action={action.id}&id={order.id}&model=purchase.order',
                    }],
                    'sticky':False,
                }
            }
        returnsuper()._get_replenishment_order_notification()

    def_prepare_procurement_values(self,date=False,group=False):
        values=super()._prepare_procurement_values(date=date,group=group)
        values['supplierinfo_id']=self.supplier_id
        returnvalues

    def_quantity_in_progress(self):
        res=super()._quantity_in_progress()
        qty_by_product_location,dummy=self.product_id._get_quantity_in_progress(self.location_id.ids)
        fororderpointinself:
            product_qty=qty_by_product_location.get((orderpoint.product_id.id,orderpoint.location_id.id),0.0)
            product_uom_qty=orderpoint.product_id.uom_id._compute_quantity(product_qty,orderpoint.product_uom,round=False)
            res[orderpoint.id]+=product_uom_qty
        returnres

    def_set_default_route_id(self):
        route_id=self.env['stock.rule'].search([
            ('action','=','buy')
        ]).route_id
        orderpoint_wh_supplier=self.filtered(lambdao:o.product_id.seller_ids)
        ifroute_idandorderpoint_wh_supplier:
            orderpoint_wh_supplier.route_id=route_id[0].id
        returnsuper()._set_default_route_id()


classProductionLot(models.Model):
    _inherit='stock.production.lot'

    purchase_order_ids=fields.Many2many('purchase.order',string="PurchaseOrders",compute='_compute_purchase_order_ids',readonly=True,store=False)
    purchase_order_count=fields.Integer('Purchaseordercount',compute='_compute_purchase_order_ids')

    @api.depends('name')
    def_compute_purchase_order_ids(self):
        forlotinself:
            stock_moves=self.env['stock.move.line'].search([
                ('lot_id','=',lot.id),
                ('state','=','done')
            ]).mapped('move_id')
            stock_moves=stock_moves.search([('id','in',stock_moves.ids)]).filtered(
                lambdamove:move.picking_id.location_id.usage=='supplier'andmove.state=='done')
            lot.purchase_order_ids=stock_moves.mapped('purchase_line_id.order_id')
            lot.purchase_order_count=len(lot.purchase_order_ids)

    defaction_view_po(self):
        self.ensure_one()
        action=self.env["ir.actions.actions"]._for_xml_id("purchase.purchase_form_action")
        action['domain']=[('id','in',self.mapped('purchase_order_ids.id'))]
        action['context']=dict(self._context,create=False)
        returnaction


classProcurementGroup(models.Model):
    _inherit='procurement.group'

    @api.model
    defrun(self,procurements,raise_user_error=True):
        wh_by_comp=dict()
        forprocurementinprocurements:
            routes=procurement.values.get('route_ids')
            ifroutesandany(r.action=='buy'forrinroutes.rule_ids):
                company=procurement.company_id
                ifcompanynotinwh_by_comp:
                    wh_by_comp[company]=self.env['stock.warehouse'].search([('company_id','=',company.id)])
                wh=wh_by_comp[company]
                procurement.values['route_ids']|=wh.reception_route_id
        returnsuper().run(procurements,raise_user_error=raise_user_error)
