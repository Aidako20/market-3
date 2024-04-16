#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importjson
importlogging
fromdatetimeimportdatetime,timedelta
fromcollectionsimportdefaultdict

fromflectraimportapi,fields,models,_
fromflectra.toolsimportDEFAULT_SERVER_DATETIME_FORMAT,float_compare,float_round
fromflectra.tools.float_utilsimportfloat_repr
fromflectra.tools.miscimportformat_date
fromflectra.exceptionsimportUserError


_logger=logging.getLogger(__name__)


classSaleOrder(models.Model):
    _inherit="sale.order"

    @api.model
    def_default_warehouse_id(self):
        #!!!Anychangetothedefaultvaluemayhavetoberepercuted
        #on_init_column()below.
        returnself.env.user._get_default_warehouse_id()

    incoterm=fields.Many2one(
        'account.incoterms','Incoterm',
        help="InternationalCommercialTermsareaseriesofpredefinedcommercialtermsusedininternationaltransactions.")
    picking_policy=fields.Selection([
        ('direct','Assoonaspossible'),
        ('one','Whenallproductsareready')],
        string='ShippingPolicy',required=True,readonly=True,default='direct',
        states={'draft':[('readonly',False)],'sent':[('readonly',False)]}
        ,help="Ifyoudeliverallproductsatonce,thedeliveryorderwillbescheduledbasedonthegreatest"
        "productleadtime.Otherwise,itwillbebasedontheshortest.")
    warehouse_id=fields.Many2one(
        'stock.warehouse',string='Warehouse',
        required=True,readonly=True,states={'draft':[('readonly',False)],'sent':[('readonly',False)]},
        default=_default_warehouse_id,check_company=True)
    picking_ids=fields.One2many('stock.picking','sale_id',string='Transfers')
    delivery_count=fields.Integer(string='DeliveryOrders',compute='_compute_picking_ids')
    procurement_group_id=fields.Many2one('procurement.group','ProcurementGroup',copy=False)
    effective_date=fields.Date("EffectiveDate",compute='_compute_effective_date',store=True,help="Completiondateofthefirstdeliveryorder.")
    expected_date=fields.Datetime(help="Deliverydateyoucanpromisetothecustomer,computedfromtheminimumleadtimeof"
                                          "theorderlinesincaseofServiceproducts.Incaseofshipping,theshippingpolicyof"
                                          "theorderwillbetakenintoaccounttoeitherusetheminimumormaximumleadtimeof"
                                          "theorderlines.")
    json_popover=fields.Char('JSONdataforthepopoverwidget',compute='_compute_json_popover')
    show_json_popover=fields.Boolean('Haslatepicking',compute='_compute_json_popover')

    def_init_column(self,column_name):
        """Ensurethedefaultwarehouse_idiscorrectlyassigned

        Atcolumninitialization,their.model.fieldsforres.users.property_warehouse_idisn'tcreated,
        whichmeanstryingtoreadthepropertyfieldtogetthedefaultvaluewillcrash.
        Wethereforeenforcethedefaulthere,withoutgoingthrough
        thedefaultfunctiononthewarehouse_idfield.
        """
        ifcolumn_name!="warehouse_id":
            returnsuper(SaleOrder,self)._init_column(column_name)
        field=self._fields[column_name]
        default=self.env['stock.warehouse'].search([('company_id','=',self.env.company.id)],limit=1)
        value=field.convert_to_write(default,self)
        value=field.convert_to_column(value,self)
        ifvalueisnotNone:
            _logger.debug("Table'%s':settingdefaultvalueofnewcolumn%sto%r",
                self._table,column_name,value)
            query='UPDATE"%s"SET"%s"=%sWHERE"%s"ISNULL'%(
                self._table,column_name,field.column_format,column_name)
            self._cr.execute(query,(value,))

    @api.depends('picking_ids.date_done')
    def_compute_effective_date(self):
        fororderinself:
            pickings=order.picking_ids.filtered(lambdax:x.state=='done'andx.location_dest_id.usage=='customer')
            dates_list=[datefordateinpickings.mapped('date_done')ifdate]
            order.effective_date=fields.Date.context_today(order,min(dates_list))ifdates_listelseFalse

    @api.depends('picking_policy')
    def_compute_expected_date(self):
        super(SaleOrder,self)._compute_expected_date()
        fororderinself:
            dates_list=[]
            forlineinorder.order_line.filtered(lambdax:x.state!='cancel'andnotx._is_delivery()andnotx.display_type):
                dt=line._expected_date()
                dates_list.append(dt)
            ifdates_list:
                expected_date=min(dates_list)iforder.picking_policy=='direct'elsemax(dates_list)
                order.expected_date=fields.Datetime.to_string(expected_date)

    @api.model
    defcreate(self,vals):
        if'warehouse_id'notinvalsand'company_id'invals:
            user=self.env['res.users'].browse(vals.get('user_id',False))
            vals['warehouse_id']=user.with_company(vals.get('company_id'))._get_default_warehouse_id().id
        returnsuper().create(vals)

    defwrite(self,values):
        ifvalues.get('order_line')andself.state=='sale':
            fororderinself:
                pre_order_line_qty={order_line:order_line.product_uom_qtyfororder_lineinorder.mapped('order_line')ifnotorder_line.is_expense}

        ifvalues.get('partner_shipping_id'):
            new_partner=self.env['res.partner'].browse(values.get('partner_shipping_id'))
            forrecordinself:
                picking=record.mapped('picking_ids').filtered(lambdax:x.statenotin('done','cancel'))
                addresses=(record.partner_shipping_id.display_name,new_partner.display_name)
                message=_("""ThedeliveryaddresshasbeenchangedontheSalesOrder<br/>
                        From<strong>"%s"</strong>To<strong>"%s"</strong>,
                        Youshouldprobablyupdatethepartneronthisdocument.""")%addresses
                picking.activity_schedule('mail.mail_activity_data_warning',note=message,user_id=self.env.user.id)

        ifvalues.get('commitment_date'):
            #protagatecommitment_dateasthedeadlineoftherelatedstockmove.
            #TODO:Loganoteoneachdowndocument
            self.order_line.move_ids.date_deadline=fields.Datetime.to_datetime(values.get('commitment_date'))

        res=super(SaleOrder,self).write(values)
        ifvalues.get('order_line')andself.state=='sale':
            rounding=self.env['decimal.precision'].precision_get('ProductUnitofMeasure')
            fororderinself:
                to_log={}
                fororder_lineinorder.order_line:
                    iforder_line.display_type:
                        continue
                    iffloat_compare(order_line.product_uom_qty,pre_order_line_qty.get(order_line,0.0),precision_rounding=order_line.product_uom.roundingorrounding)<0:
                        to_log[order_line]=(order_line.product_uom_qty,pre_order_line_qty.get(order_line,0.0))
                ifto_log:
                    documents=self.env['stock.picking']._log_activity_get_documents(to_log,'move_ids','UP')
                    documents={k:vfork,vindocuments.items()ifk[0].state!='cancel'}
                    order._log_decrease_ordered_quantity(documents)
        returnres

    def_compute_json_popover(self):
        fororderinself:
            late_stock_picking=order.picking_ids.filtered(lambdap:p.delay_alert_date)
            order.json_popover=json.dumps({
                'popoverTemplate':'sale_stock.DelayAlertWidget',
                'late_elements':[{
                        'id':late_move.id,
                        'name':late_move.display_name,
                        'model':'stock.picking',
                    }forlate_moveinlate_stock_picking
                ]
            })
            order.show_json_popover=bool(late_stock_picking)

    def_action_confirm(self):
        self.order_line._action_launch_stock_rule()
        returnsuper(SaleOrder,self)._action_confirm()

    @api.depends('picking_ids')
    def_compute_picking_ids(self):
        fororderinself:
            order.delivery_count=len(order.picking_ids)

    @api.onchange('company_id')
    def_onchange_company_id(self):
        ifself.company_id:
            warehouse_id=self.env['ir.default'].get_model_defaults('sale.order').get('warehouse_id')
            self.warehouse_id=warehouse_idorself.user_id.with_company(self.company_id.id)._get_default_warehouse_id().id

    @api.onchange('user_id')
    defonchange_user_id(self):
        super().onchange_user_id()
        ifself.statein['draft','sent']:
            self.warehouse_id=self.user_id.with_company(self.company_id.id)._get_default_warehouse_id().id

    @api.onchange('partner_shipping_id')
    def_onchange_partner_shipping_id(self):
        res={}
        pickings=self.picking_ids.filtered(
            lambdap:p.statenotin['done','cancel']andp.partner_id!=self.partner_shipping_id
        )
        ifpickings:
            res['warning']={
                'title':_('Warning!'),
                'message':_(
                    'Donotforgettochangethepartneronthefollowingdeliveryorders:%s'
                )%(','.join(pickings.mapped('name')))
            }
        returnres

    defaction_view_delivery(self):
        '''
        Thisfunctionreturnsanactionthatdisplayexistingdeliveryorders
        ofgivensalesorderids.Itcaneitherbeainalistorinaform
        view,ifthereisonlyonedeliveryordertoshow.
        '''
        action=self.env["ir.actions.actions"]._for_xml_id("stock.action_picking_tree_all")

        pickings=self.mapped('picking_ids')
        iflen(pickings)>1:
            action['domain']=[('id','in',pickings.ids)]
        elifpickings:
            form_view=[(self.env.ref('stock.view_picking_form').id,'form')]
            if'views'inaction:
                action['views']=form_view+[(state,view)forstate,viewinaction['views']ifview!='form']
            else:
                action['views']=form_view
            action['res_id']=pickings.id
        #Preparethecontext.
        picking_id=pickings.filtered(lambdal:l.picking_type_id.code=='outgoing')
        ifpicking_id:
            picking_id=picking_id[0]
        else:
            picking_id=pickings[0]
        action['context']=dict(self._context,default_partner_id=self.partner_id.id,default_picking_type_id=picking_id.picking_type_id.id,default_origin=self.name,default_group_id=picking_id.group_id.id)
        returnaction

    def_action_cancel(self):
        documents=None
        forsale_orderinself:
            ifsale_order.state=='sale'andsale_order.order_line:
                sale_order_lines_quantities={order_line:(order_line.product_uom_qty,0)fororder_lineinsale_order.order_line}
                documents=self.env['stock.picking']._log_activity_get_documents(sale_order_lines_quantities,'move_ids','UP')
        self.picking_ids.filtered(lambdap:p.state!='done').action_cancel()
        ifdocuments:
            filtered_documents={}
            for(parent,responsible),rendering_contextindocuments.items():
                ifparent._name=='stock.picking':
                    ifparent.state=='cancel':
                        continue
                filtered_documents[(parent,responsible)]=rendering_context
            self._log_decrease_ordered_quantity(filtered_documents,cancel=True)
        returnsuper()._action_cancel()

    def_prepare_invoice(self):
        invoice_vals=super(SaleOrder,self)._prepare_invoice()
        invoice_vals['invoice_incoterm_id']=self.incoterm.id
        returninvoice_vals

    @api.model
    def_get_customer_lead(self,product_tmpl_id):
        super(SaleOrder,self)._get_customer_lead(product_tmpl_id)
        returnproduct_tmpl_id.sale_delay

    def_log_decrease_ordered_quantity(self,documents,cancel=False):

        def_render_note_exception_quantity_so(rendering_context):
            order_exceptions,visited_moves=rendering_context
            visited_moves=list(visited_moves)
            visited_moves=self.env[visited_moves[0]._name].concat(*visited_moves)
            order_line_ids=self.env['sale.order.line'].browse([order_line.idfororderinorder_exceptions.values()fororder_lineinorder[0]])
            sale_order_ids=order_line_ids.mapped('order_id')
            impacted_pickings=visited_moves.filtered(lambdam:m.statenotin('done','cancel')).mapped('picking_id')
            values={
                'sale_order_ids':sale_order_ids,
                'order_exceptions':order_exceptions.values(),
                'impacted_pickings':impacted_pickings,
                'cancel':cancel
            }
            returnself.env.ref('sale_stock.exception_on_so')._render(values=values)

        self.env['stock.picking']._log_activity(_render_note_exception_quantity_so,documents)

    def_show_cancel_wizard(self):
        res=super(SaleOrder,self)._show_cancel_wizard()
        fororderinself:
            ifany(picking.state=='done'forpickinginorder.picking_ids)andnotorder._context.get('disable_cancel_warning'):
                returnTrue
        returnres

classSaleOrderLine(models.Model):
    _inherit='sale.order.line'

    qty_delivered_method=fields.Selection(selection_add=[('stock_move','StockMoves')])
    product_packaging=fields.Many2one('product.packaging',string='Package',default=False,check_company=True)
    route_id=fields.Many2one('stock.location.route',string='Route',domain=[('sale_selectable','=',True)],ondelete='restrict',check_company=True)
    move_ids=fields.One2many('stock.move','sale_line_id',string='StockMoves')
    product_type=fields.Selection(related='product_id.type')
    virtual_available_at_date=fields.Float(compute='_compute_qty_at_date',digits='ProductUnitofMeasure')
    scheduled_date=fields.Datetime(compute='_compute_qty_at_date')
    forecast_expected_date=fields.Datetime(compute='_compute_qty_at_date')
    free_qty_today=fields.Float(compute='_compute_qty_at_date',digits='ProductUnitofMeasure')
    qty_available_today=fields.Float(compute='_compute_qty_at_date')
    warehouse_id=fields.Many2one(related='order_id.warehouse_id')
    qty_to_deliver=fields.Float(compute='_compute_qty_to_deliver',digits='ProductUnitofMeasure')
    is_mto=fields.Boolean(compute='_compute_is_mto')
    display_qty_widget=fields.Boolean(compute='_compute_qty_to_deliver')

    @api.depends('product_type','product_uom_qty','qty_delivered','state','move_ids','product_uom')
    def_compute_qty_to_deliver(self):
        """Computethevisibilityoftheinventorywidget."""
        forlineinself:
            line.qty_to_deliver=line.product_uom_qty-line.qty_delivered
            ifline.statein('draft','sent','sale')andline.product_type=='product'andline.product_uomandline.qty_to_deliver>0:
                ifline.state=='sale'andnotline.move_ids:
                    line.display_qty_widget=False
                else:
                    line.display_qty_widget=True
            else:
                line.display_qty_widget=False

    @api.depends(
        'product_id','customer_lead','product_uom_qty','product_uom','order_id.commitment_date',
        'move_ids','move_ids.forecast_expected_date','move_ids.forecast_availability')
    def_compute_qty_at_date(self):
        """Computethequantityforecastedofproductatdeliverydate.Thereare
        twocases:
         1.Thequotationhasacommitment_date,wetakeitasdeliverydate
         2.Thequotationhasn'tcommitment_date,wecomputetheestimateddelivery
            datebasedonleadtime"""
        treated=self.browse()
        #Ifthestateisalreadyinsalethepickingiscreatedandasimpleforecastedquantityisn'tenough
        #Thenusedtheforecasteddataoftherelatedstock.move
        forlineinself.filtered(lambdal:l.state=='sale'):
            ifnotline.display_qty_widget:
                continue
            moves=line.move_ids.filtered(lambdam:m.product_id==line.product_id)
            line.forecast_expected_date=max(moves.filtered("forecast_expected_date").mapped("forecast_expected_date"),default=False)
            line.qty_available_today=0
            line.free_qty_today=0
            formoveinmoves:
                line.qty_available_today+=move.product_uom._compute_quantity(move.reserved_availability,line.product_uom)
                line.free_qty_today+=move.product_id.uom_id._compute_quantity(move.forecast_availability,line.product_uom)
            line.scheduled_date=line.order_id.commitment_dateorline._expected_date()
            line.virtual_available_at_date=False
            treated|=line

        qty_processed_per_product=defaultdict(lambda:0)
        grouped_lines=defaultdict(lambda:self.env['sale.order.line'])
        #WefirstloopovertheSOlinestogroupthembywarehouseandschedule
        #dateinordertobatchthereadofthequantitiescomputedfield.
        forlineinself.filtered(lambdal:l.statein('draft','sent')):
            ifnot(line.product_idandline.display_qty_widget):
                continue
            grouped_lines[(line.warehouse_id.id,line.order_id.commitment_dateorline._expected_date())]|=line

        for(warehouse,scheduled_date),linesingrouped_lines.items():
            product_qties=lines.mapped('product_id').with_context(to_date=scheduled_date,warehouse=warehouse).read([
                'qty_available',
                'free_qty',
                'virtual_available',
            ])
            qties_per_product={
                product['id']:(product['qty_available'],product['free_qty'],product['virtual_available'])
                forproductinproduct_qties
            }
            forlineinlines:
                line.scheduled_date=scheduled_date
                qty_available_today,free_qty_today,virtual_available_at_date=qties_per_product[line.product_id.id]
                line.qty_available_today=qty_available_today-qty_processed_per_product[line.product_id.id]
                line.free_qty_today=free_qty_today-qty_processed_per_product[line.product_id.id]
                line.virtual_available_at_date=virtual_available_at_date-qty_processed_per_product[line.product_id.id]
                line.forecast_expected_date=False
                product_qty=line.product_uom_qty
                ifline.product_uomandline.product_id.uom_idandline.product_uom!=line.product_id.uom_id:
                    line.qty_available_today=line.product_id.uom_id._compute_quantity(line.qty_available_today,line.product_uom)
                    line.free_qty_today=line.product_id.uom_id._compute_quantity(line.free_qty_today,line.product_uom)
                    line.virtual_available_at_date=line.product_id.uom_id._compute_quantity(line.virtual_available_at_date,line.product_uom)
                    product_qty=line.product_uom._compute_quantity(product_qty,line.product_id.uom_id)
                qty_processed_per_product[line.product_id.id]+=product_qty
            treated|=lines
        remaining=(self-treated)
        remaining.virtual_available_at_date=False
        remaining.scheduled_date=False
        remaining.forecast_expected_date=False
        remaining.free_qty_today=False
        remaining.qty_available_today=False

    @api.depends('product_id','route_id','order_id.warehouse_id','product_id.route_ids')
    def_compute_is_mto(self):
        """Verifytherouteoftheproductbasedonthewarehouse
            set'is_available'atTrueiftheproductavailibilityinstockdoes
            notneedtobeverified,whichisthecaseinMTO,Cross-DockorDrop-Shipping
        """
        self.is_mto=False
        forlineinself:
            ifnotline.display_qty_widget:
                continue
            product=line.product_id
            product_routes=line.route_idor(product.route_ids+product.categ_id.total_route_ids)

            #CheckMTO
            mto_route=line.order_id.warehouse_id.mto_pull_id.route_id
            ifnotmto_route:
                try:
                    mto_route=self.env['stock.warehouse']._find_global_route('stock.route_warehouse0_mto',_('MakeToOrder'))
                exceptUserError:
                    #ifrouteMTOnotfoundinir_model_data,wetreattheproductasinMTS
                    pass

            ifmto_routeandmto_routeinproduct_routes:
                line.is_mto=True
            else:
                line.is_mto=False

    @api.depends('product_id')
    def_compute_qty_delivered_method(self):
        """Stockmodulecomputedeliveredqtyforproduct[('type','in',['consu','product'])]
            ForSOlinecomingfromexpense,nopickingshouldbegenerate:wedon'tmanagestockfor
            thoseslines,eveniftheproductisastorable.
        """
        super(SaleOrderLine,self)._compute_qty_delivered_method()

        forlineinself:
            ifnotline.is_expenseandline.product_id.typein['consu','product']:
                line.qty_delivered_method='stock_move'

    @api.depends('move_ids.state','move_ids.scrapped','move_ids.product_uom_qty','move_ids.product_uom')
    def_compute_qty_delivered(self):
        super(SaleOrderLine,self)._compute_qty_delivered()

        forlineinself: #TODO:maybeoneday,thisshouldbedoneinSQLforperformancesake
            ifline.qty_delivered_method=='stock_move':
                qty=0.0
                outgoing_moves,incoming_moves=line._get_outgoing_incoming_moves()
                formoveinoutgoing_moves:
                    ifmove.state!='done':
                        continue
                    qty+=move.product_uom._compute_quantity(move.product_uom_qty,line.product_uom,rounding_method='HALF-UP')
                formoveinincoming_moves:
                    ifmove.state!='done':
                        continue
                    qty-=move.product_uom._compute_quantity(move.product_uom_qty,line.product_uom,rounding_method='HALF-UP')
                line.qty_delivered=qty

    @api.model_create_multi
    defcreate(self,vals_list):
        lines=super(SaleOrderLine,self).create(vals_list)
        lines.filtered(lambdaline:line.state=='sale')._action_launch_stock_rule()
        returnlines

    defwrite(self,values):
        lines=self.env['sale.order.line']
        if'product_uom_qty'invalues:
            precision=self.env['decimal.precision'].precision_get('ProductUnitofMeasure')
            lines=self.filtered(
                lambdar:r.state=='sale'andnotr.is_expenseandfloat_compare(r.product_uom_qty,values['product_uom_qty'],precision_digits=precision)==-1)
        previous_product_uom_qty={line.id:line.product_uom_qtyforlineinlines}
        res=super(SaleOrderLine,self).write(values)
        iflines:
            lines._action_launch_stock_rule(previous_product_uom_qty)
        if'customer_lead'invaluesandself.state=='sale'andnotself.order_id.commitment_date:
            #Propagatedeadlineonrelatedstockmove
            self.move_ids.date_deadline=self.order_id.date_order+timedelta(days=self.customer_leador0.0)
        returnres

    @api.depends('order_id.state')
    def_compute_invoice_status(self):
        defcheck_moves_state(moves):
            #Allmovesstatesareeither'done'or'cancel',andthereisatleastone'done'
            at_least_one_done=False
            formoveinmoves:
                ifmove.statenotin['done','cancel']:
                    returnFalse
                at_least_one_done=at_least_one_doneormove.state=='done'
            returnat_least_one_done
        super(SaleOrderLine,self)._compute_invoice_status()
        forlineinself:
            #Wehandlethefollowingspecificsituation:aphysicalproductispartiallydelivered,
            #butwewouldliketosetitsinvoicestatusto'FullyInvoiced'.Theusecaseisfor
            #productssoldbyweight,wherethedeliveredquantityrarelymatchesexactlythe
            #quantityordered.
            ifline.order_id.state=='done'\
                    andline.invoice_status=='no'\
                    andline.product_id.typein['consu','product']\
                    andline.product_id.invoice_policy=='delivery'\
                    andline.move_ids\
                    andcheck_moves_state(line.move_ids):
                line.invoice_status='invoiced'

    @api.depends('move_ids')
    def_compute_product_updatable(self):
        forlineinself:
            ifnotline.move_ids.filtered(lambdam:m.state!='cancel'):
                super(SaleOrderLine,line)._compute_product_updatable()
            else:
                line.product_updatable=False

    @api.onchange('product_id')
    def_onchange_product_id_set_customer_lead(self):
        self.customer_lead=self.product_id.sale_delay

    @api.onchange('product_packaging')
    def_onchange_product_packaging(self):
        ifself.product_packaging:
            returnself._check_package()

    @api.onchange('product_uom_qty')
    def_onchange_product_uom_qty(self):
        #Whenmodifyingaone2many,_origindoesn'tguaranteethatitsvalueswillbetheones
        #indatabase.Hence,weneedtoexplicitlyreadthemfromthere.
        ifself._origin:
            product_uom_qty_origin=self._origin.read(["product_uom_qty"])[0]["product_uom_qty"]
        else:
            product_uom_qty_origin=0

        ifself.state=='sale'andself.product_id.typein['product','consu']andself.product_uom_qty<product_uom_qty_origin:
            #Donotdisplaythiswarningifthenewquantityisbelowthedelivered
            #one;the`write`willraisean`UserError`anyway.
            ifself.product_uom_qty<self.qty_delivered:
                return{}
            warning_mess={
                'title':_('Orderedquantitydecreased!'),
                'message':_('Youaredecreasingtheorderedquantity!Donotforgettomanuallyupdatethedeliveryorderifneeded.'),
            }
            return{'warning':warning_mess}
        ifself.product_packaging:
            returnself._check_package()
        return{}

    def_prepare_procurement_values(self,group_id=False):
        """Preparespecifickeyformovesorothercomponentsthatwillbecreatedfromastockrule
        commingfromasaleorderline.Thismethodcouldbeoverrideinordertoaddothercustomkeythatcould
        beusedinmove/pocreation.
        """
        values=super(SaleOrderLine,self)._prepare_procurement_values(group_id)
        self.ensure_one()
        #Usethedeliverydateifthereiselseusedate_orderandleadtime
        date_deadline=self.order_id.commitment_dateor(self.order_id.date_order+timedelta(days=self.customer_leador0.0))
        date_planned=date_deadline-timedelta(days=self.order_id.company_id.security_lead)
        values.update({
            'group_id':group_id,
            'sale_line_id':self.id,
            'date_planned':date_planned,
            'date_deadline':date_deadline,
            'route_ids':self.route_id,
            'warehouse_id':self.order_id.warehouse_idorFalse,
            'partner_id':self.order_id.partner_shipping_id.id,
            'product_description_variants':self.with_context(lang=self.order_id.partner_id.lang)._get_sale_order_line_multiline_description_variants(),
            'company_id':self.order_id.company_id,
            'sequence':self.sequence,
        })
        returnvalues

    def_get_qty_procurement(self,previous_product_uom_qty=False):
        self.ensure_one()
        qty=0.0
        outgoing_moves,incoming_moves=self._get_outgoing_incoming_moves()
        formoveinoutgoing_moves:
            qty+=move.product_uom._compute_quantity(move.product_uom_qty,self.product_uom,rounding_method='HALF-UP')
        formoveinincoming_moves:
            qty-=move.product_uom._compute_quantity(move.product_uom_qty,self.product_uom,rounding_method='HALF-UP')
        returnqty

    def_get_outgoing_incoming_moves(self):
        outgoing_moves=self.env['stock.move']
        incoming_moves=self.env['stock.move']

        formoveinself.move_ids.filtered(lambdar:r.state!='cancel'andnotr.scrappedandself.product_id==r.product_id):
            ifmove.location_dest_id.usage=="customer":
                ifnotmove.origin_returned_move_idor(move.origin_returned_move_idandmove.to_refund):
                    outgoing_moves|=move
            elifmove.location_dest_id.usage!="customer"andmove.to_refund:
                incoming_moves|=move

        returnoutgoing_moves,incoming_moves

    def_get_procurement_group(self):
        returnself.order_id.procurement_group_id

    def_prepare_procurement_group_vals(self):
        return{
            'name':self.order_id.name,
            'move_type':self.order_id.picking_policy,
            'sale_id':self.order_id.id,
            'partner_id':self.order_id.partner_shipping_id.id,
        }

    def_action_launch_stock_rule(self,previous_product_uom_qty=False):
        """
        Launchprocurementgrouprunmethodwithrequired/customfieldsgenratedbya
        saleorderline.procurementgroupwilllaunch'_run_pull','_run_buy'or'_run_manufacture'
        dependingonthesaleorderlineproductrule.
        """
        precision=self.env['decimal.precision'].precision_get('ProductUnitofMeasure')
        procurements=[]
        forlineinself:
            line=line.with_company(line.company_id)
            ifline.state!='sale'ornotline.product_id.typein('consu','product'):
                continue
            qty=line._get_qty_procurement(previous_product_uom_qty)
            iffloat_compare(qty,line.product_uom_qty,precision_digits=precision)>=0:
                continue

            group_id=line._get_procurement_group()
            ifnotgroup_id:
                group_id=self.env['procurement.group'].create(line._prepare_procurement_group_vals())
                line.order_id.procurement_group_id=group_id
            else:
                #Incasetheprocurementgroupisalreadycreatedandtheorderwas
                #cancelled,weneedtoupdatecertainvaluesofthegroup.
                updated_vals={}
                ifgroup_id.partner_id!=line.order_id.partner_shipping_id:
                    updated_vals.update({'partner_id':line.order_id.partner_shipping_id.id})
                ifgroup_id.move_type!=line.order_id.picking_policy:
                    updated_vals.update({'move_type':line.order_id.picking_policy})
                ifupdated_vals:
                    group_id.write(updated_vals)

            values=line._prepare_procurement_values(group_id=group_id)
            product_qty=line.product_uom_qty-qty

            line_uom=line.product_uom
            quant_uom=line.product_id.uom_id
            product_qty,procurement_uom=line_uom._adjust_uom_quantities(product_qty,quant_uom)
            procurements.append(self.env['procurement.group'].Procurement(
                line.product_id,product_qty,procurement_uom,
                line.order_id.partner_shipping_id.property_stock_customer,
                line.product_id.display_name,line.order_id.name,line.order_id.company_id,values))
        ifprocurements:
            self.env['procurement.group'].run(procurements)
        returnTrue

    def_check_package(self):
        default_uom=self.product_id.uom_id
        pack=self.product_packaging
        qty=self.product_uom_qty
        q=default_uom._compute_quantity(pack.qty,self.product_uom)
        #Wedonotusethemodulooperatortocheckifqtyisamltipleofq.Indeedthequantity
        #perpackagemightbeafloat,leadingtoincorrectresults.Forexample:
        #8%1.6=1.5999999999999996
        #5.4%1.8=2.220446049250313e-16
        if(
            qty
            andq
            andfloat_compare(
                qty/q,float_round(qty/q,precision_rounding=1.0),precision_rounding=0.001
            )
            !=0
        ):
            newqty=qty-(qty%q)+q
            return{
                'warning':{
                    'title':_('Warning'),
                    'message':_(
                        "Thisproductispackagedby%(pack_size).2f%(pack_name)s.Youshouldsell%(quantity).2f%(unit)s.",
                        pack_size=pack.qty,
                        pack_name=default_uom.name,
                        quantity=newqty,
                        unit=self.product_uom.name
                    ),
                },
            }
        return{}

    def_update_line_quantity(self,values):
        precision=self.env['decimal.precision'].precision_get('ProductUnitofMeasure')
        line_products=self.filtered(lambdal:l.product_id.typein['product','consu'])
        ifline_products.mapped('qty_delivered')andfloat_compare(values['product_uom_qty'],max(line_products.mapped('qty_delivered')),precision_digits=precision)==-1:
            raiseUserError(_('Youcannotdecreasetheorderedquantitybelowthedeliveredquantity.\n'
                              'Createareturnfirst.'))
        super(SaleOrderLine,self)._update_line_quantity(values)
