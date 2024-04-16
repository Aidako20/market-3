#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromcollectionsimportdefaultdict

fromflectraimportapi,fields,models,_
fromflectra.tools.sqlimportcolumn_exists,create_column


classStockLocationRoute(models.Model):
    _inherit="stock.location.route"
    sale_selectable=fields.Boolean("SelectableonSalesOrderLine")


classStockMove(models.Model):
    _inherit="stock.move"
    sale_line_id=fields.Many2one('sale.order.line','SaleLine',index=True)

    @api.model
    def_prepare_merge_moves_distinct_fields(self):
        distinct_fields=super(StockMove,self)._prepare_merge_moves_distinct_fields()
        distinct_fields.append('sale_line_id')
        returndistinct_fields

    @api.model
    def_prepare_merge_move_sort_method(self,move):
        move.ensure_one()
        keys_sorted=super(StockMove,self)._prepare_merge_move_sort_method(move)
        keys_sorted.append(move.sale_line_id.id)
        returnkeys_sorted

    def_get_related_invoices(self):
        """Overriddenfromstock_accounttoreturnthecustomerinvoices
        relatedtothisstockmove.
        """
        rslt=super(StockMove,self)._get_related_invoices()
        invoices=self.mapped('picking_id.sale_id.invoice_ids').filtered(lambdax:x.state=='posted')
        rslt+=invoices
        #rslt+=invoices.mapped('reverse_entry_ids')
        returnrslt

    def_get_source_document(self):
        res=super()._get_source_document()
        returnself.sale_line_id.order_idorres

    def_assign_picking_post_process(self,new=False):
        super(StockMove,self)._assign_picking_post_process(new=new)
        ifnew:
            picking_id=self.mapped('picking_id')
            sale_order_ids=self.mapped('sale_line_id.order_id')
            forsale_order_idinsale_order_ids:
                picking_id.message_post_with_view(
                    'mail.message_origin_link',
                    values={'self':picking_id,'origin':sale_order_id},
                    subtype_id=self.env.ref('mail.mt_note').id)


classProcurementGroup(models.Model):
    _inherit='procurement.group'

    sale_id=fields.Many2one('sale.order','SaleOrder')


classStockRule(models.Model):
    _inherit='stock.rule'

    def_get_custom_move_fields(self):
        fields=super(StockRule,self)._get_custom_move_fields()
        fields+=['sale_line_id','partner_id','sequence']
        returnfields


classStockPicking(models.Model):
    _inherit='stock.picking'

    sale_id=fields.Many2one(related="group_id.sale_id",string="SalesOrder",store=True,readonly=False)

    def_auto_init(self):
        """
        Createrelatedfieldhere,tooslow
        whencomputingitafterwardsthrough_compute_related.

        Sincegroup_id.sale_idiscreatedinthismodule,
        noneedforanUPDATEstatement.
        """
        ifnotcolumn_exists(self.env.cr,'stock_picking','sale_id'):
            create_column(self.env.cr,'stock_picking','sale_id','int4')
        returnsuper()._auto_init()

    def_action_done(self):
        res=super()._action_done()
        sale_order_lines_vals=[]
        formoveinself.move_lines:
            sale_order=move.picking_id.sale_id
            #CreatesnewSOlineonlywhenpickingslinkedtoasaleorderand
            #formoveswithqty.doneandnotalreadylinkedtoaSOline.
            ifnotsale_orderormove.location_dest_id.usage!='customer'ormove.sale_line_idornotmove.quantity_done:
                continue
            product=move.product_id
            so_line_vals={
                'move_ids':[(4,move.id,0)],
                'name':product.display_name,
                'order_id':sale_order.id,
                'product_id':product.id,
                'product_uom_qty':0,
                'qty_delivered':move.quantity_done,
                'product_uom':move.product_uom.id,
            }
            ifproduct.invoice_policy=='delivery':
                #CheckifthereisalreadyaSOlineforthisproducttoget
                #backitsunitprice(incaseitwasmanuallyupdated).
                so_line=sale_order.order_line.filtered(lambdasol:sol.product_id==product)
                ifso_line:
                    so_line_vals['price_unit']=so_line[0].price_unit
            elifproduct.invoice_policy=='order':
                #Nounitpriceiftheproductisinvoicedontheorderedqty.
                so_line_vals['price_unit']=0
            sale_order_lines_vals.append(so_line_vals)

        ifsale_order_lines_vals:
            self.env['sale.order.line'].create(sale_order_lines_vals)
        returnres

    def_log_less_quantities_than_expected(self,moves):
        """Loganactivityonsaleorderthatarelinkedtomoves.The
        notesummarizetherealproccessedquantityandpromotea
        manualaction.

        :paramdictmoves:adictwithamoveaskeyandtuplewith
        newandoldquantityasvalue.eg:{move_1:(4,5)}
        """

        def_keys_in_sorted(sale_line):
            """sortbyorder_idandthesale_personontheorder"""
            return(sale_line.order_id.id,sale_line.order_id.user_id.id)

        def_keys_in_groupby(sale_line):
            """groupbyorder_idandthesale_personontheorder"""
            return(sale_line.order_id,sale_line.order_id.user_id)

        def_render_note_exception_quantity(moves_information):
            """Generateanotewiththepickingonwhichtheaction
            occurredandasummaryonimpactedquantitythatare
            relatedtothesaleorderwherethenotewillbelogged.

            :parammoves_informationdict:
            {'move_id':['sale_order_line_id',(new_qty,old_qty)],..}

            :return:anhtmlstringwithalltheinformationencoded.
            :rtype:str
            """
            origin_moves=self.env['stock.move'].browse([move.idformove_originmoves_information.values()formoveinmove_orig[0]])
            origin_picking=origin_moves.mapped('picking_id')
            values={
                'origin_moves':origin_moves,
                'origin_picking':origin_picking,
                'moves_information':moves_information.values(),
            }
            returnself.env.ref('sale_stock.exception_on_picking')._render(values=values)

        documents=self._log_activity_get_documents(moves,'sale_line_id','DOWN',_keys_in_sorted,_keys_in_groupby)
        self._log_activity(_render_note_exception_quantity,documents)

        returnsuper(StockPicking,self)._log_less_quantities_than_expected(moves)

    def_needs_automatic_assign(self):
        self.ensure_one()
        ifself.sale_id:
            returnFalse
        returnsuper()._needs_automatic_assign()


classProductionLot(models.Model):
    _inherit='stock.production.lot'

    sale_order_ids=fields.Many2many('sale.order',string="SalesOrders",compute='_compute_sale_order_ids')
    sale_order_count=fields.Integer('Saleordercount',compute='_compute_sale_order_ids')

    @api.depends('name')
    def_compute_sale_order_ids(self):
        sale_orders=defaultdict(lambda:self.env['sale.order'])
        formove_lineinself.env['stock.move.line'].search([('lot_id','in',self.ids),('state','=','done')]):
            move=move_line.move_id
            ifmove.picking_id.location_dest_id.usage=='customer'andmove.sale_line_id.order_id:
                sale_orders[move_line.lot_id.id]|=move.sale_line_id.order_id
        forlotinself:
            lot.sale_order_ids=sale_orders[lot.id]
            lot.sale_order_count=len(lot.sale_order_ids)

    defaction_view_so(self):
        self.ensure_one()
        action=self.env["ir.actions.actions"]._for_xml_id("sale.action_orders")
        action['domain']=[('id','in',self.mapped('sale_order_ids.id'))]
        action['context']=dict(self._context,create=False)
        returnaction
