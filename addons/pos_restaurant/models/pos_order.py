#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectra.toolsimportgroupby
fromreimportsearch
fromfunctoolsimportpartial

fromflectraimportapi,fields,models


classPosOrderLine(models.Model):
    _inherit='pos.order.line'

    note=fields.Char('Noteaddedbythewaiter.')
    mp_skip=fields.Boolean('Skiplinewhensendingtickettokitchenprinters.')
    mp_dirty=fields.Boolean()


classPosOrder(models.Model):
    _inherit='pos.order'

    table_id=fields.Many2one('restaurant.table',string='Table',help='Thetablewherethisorderwasserved',index=True)
    customer_count=fields.Integer(string='Guests',help='Theamountofcustomersthathavebeenservedbythisorder.')
    multiprint_resume=fields.Char()

    def_get_pack_lot_lines(self,order_lines):
        """Addpack_lot_linestotheorder_lines.

        Thefunctiondoesn'treturnanythingbutaddstheresultsdirectlytotheorder_lines.

        :paramorder_lines:order_linesforwhichthepack_lot_linesaretoberequested.
        :typeorder_lines:pos.order.line.
        """
        pack_lots=self.env['pos.pack.operation.lot'].search_read(
                domain=[('pos_order_line_id','in',[order_line['id']fororder_lineinorder_lines])],
                fields=[
                    'id',
                    'lot_name',
                    'pos_order_line_id'
                    ])
        forpack_lotinpack_lots:
            pack_lot['order_line']=pack_lot['pos_order_line_id'][0]
            pack_lot['server_id']=pack_lot['id']

            delpack_lot['pos_order_line_id']
            delpack_lot['id']

        fororder_line_id,pack_lot_idsingroupby(pack_lots,key=lambdax:x['order_line']):
            next(order_linefororder_lineinorder_linesiforder_line['id']==order_line_id)['pack_lot_ids']=list(pack_lot_ids)

    def_get_fields_for_order_line(self):
        return[
            'id',
            'discount',
            'product_id',
            'price_unit',
            'order_id',
            'qty',
            'note',
            'mp_skip',
            'mp_dirty',
            'full_product_name',
        ]

    def_get_order_lines(self,orders):
        """Addpos_order_linestotheorders.

        Thefunctiondoesn'treturnanythingbutaddstheresultsdirectlytotheorders.

        :paramorders:ordersforwhichtheorder_linesaretoberequested.
        :typeorders:pos.order.
        """
        order_lines=self.env['pos.order.line'].search_read(
                domain=[('order_id','in',[to['id']fortoinorders])],
                fields=self._get_fields_for_order_line())

        iforder_lines!=[]:
            self._get_pack_lot_lines(order_lines)

        extended_order_lines=[]
        fororder_lineinorder_lines:
            order_line['product_id']=order_line['product_id'][0]
            order_line['server_id']=order_line['id']

            delorder_line['id']
            ifnot'pack_lot_ids'inorder_line:
                order_line['pack_lot_ids']=[]
            else:
                order_line['pack_lot_ids']=[[0,0,lot]forlotinorder_line['pack_lot_ids']]
            extended_order_lines.append([0,0,order_line])

        fororder_id,order_linesingroupby(extended_order_lines,key=lambdax:x[2]['order_id']):
            next(orderfororderinordersiforder['id']==order_id[0])['lines']=list(order_lines)

    def_get_fields_for_payment_lines(self):
        return[
            'id',
            'amount',
            'pos_order_id',
            'payment_method_id',
            'card_type',
            'cardholder_name',
            'transaction_id',
            'payment_status'
            ]

    def_get_payment_lines(self,orders):
        """Addaccount_bank_statement_linestotheorders.

        Thefunctiondoesn'treturnanythingbutaddstheresultsdirectlytotheorders.

        :paramorders:ordersforwhichthepayment_linesaretoberequested.
        :typeorders:pos.order.
        """
        payment_lines=self.env['pos.payment'].search_read(
                domain=[('pos_order_id','in',[po['id']forpoinorders])],
                fields=self._get_fields_for_payment_lines())

        extended_payment_lines=[]
        forpayment_lineinpayment_lines:
            payment_line['server_id']=payment_line['id']
            payment_line['payment_method_id']=payment_line['payment_method_id'][0]

            delpayment_line['id']
            extended_payment_lines.append([0,0,payment_line])
        fororder_id,payment_linesingroupby(extended_payment_lines,key=lambdax:x[2]['pos_order_id']):
            next(orderfororderinordersiforder['id']==order_id[0])['statement_ids']=list(payment_lines)

    def_get_fields_for_draft_order(self):
        fields=super(PosOrder,self)._get_fields_for_draft_order()
        fields.extend([
                    'id',
                    'pricelist_id',
                    'partner_id',
                    'sequence_number',
                    'session_id',
                    'pos_reference',
                    'create_uid',
                    'create_date',
                    'customer_count',
                    'fiscal_position_id',
                    'table_id',
                    'to_invoice',
                    'multiprint_resume',
                    ])
        returnfields

    @api.model
    defget_table_draft_orders(self,table_id):
        """Generateanobjectofalldraftordersforthegiventable.

        GenerateandreturnanJSONobjectwithalldraftordersforthegiventable,tosendtothe
        frontendapplication.

        :paramtable_id:Idoftheselectedtable.
        :typetable_id:int.
        :returns:list--listofdictrepresentingthetableorders
        """
        table_orders=self.search_read(
                domain=[('state','=','draft'),('table_id','=',table_id)],
                fields=self._get_fields_for_draft_order())

        self._get_order_lines(table_orders)
        self._get_payment_lines(table_orders)

        fororderintable_orders:
            order['pos_session_id']=order['session_id'][0]
            order['uid']=search(r"\d{5,}-\d{3,}-\d{4,}",order['pos_reference']).group(0)
            order['name']=order['pos_reference']
            order['creation_date']=order['create_date']
            order['server_id']=order['id']
            iforder['fiscal_position_id']:
                order['fiscal_position_id']=order['fiscal_position_id'][0]
            iforder['pricelist_id']:
                order['pricelist_id']=order['pricelist_id'][0]
            iforder['partner_id']:
                order['partner_id']=order['partner_id'][0]
            iforder['table_id']:
                order['table_id']=order['table_id'][0]
            if'employee_id'inorder:
                order['employee_id']=order['employee_id'][0]iforder['employee_id']elseFalse

            ifnot'lines'inorder:
                order['lines']=[]
            ifnot'statement_ids'inorder:
                order['statement_ids']=[]

            delorder['id']
            delorder['session_id']
            delorder['pos_reference']
            delorder['create_date']

        returntable_orders

    defset_tip(self,tip_line_vals):
        """Settipto`self`basedonvaluesin`tip_line_vals`."""

        self.ensure_one()
        PosOrderLine=self.env['pos.order.line']
        process_line=partial(PosOrderLine._order_line_fields,session_id=self.session_id.id)

        #1.add/modifytiporderline
        processed_tip_line_vals=process_line([0,0,tip_line_vals])[2]
        processed_tip_line_vals.update({"order_id":self.id})
        tip_line=self.lines.filtered(lambdaline:line.product_id==self.session_id.config_id.tip_product_id)
        ifnottip_line:
            tip_line=PosOrderLine.create(processed_tip_line_vals)
        else:
            tip_line.write(processed_tip_line_vals)

        #2.modifypayment
        payment_line=self.payment_ids.filtered(lambdaline:notline.is_change)[0]
        #TODOitwouldbebettertothrowerroriftherearemultiplepaymentlines
        #thenasktheusertoselectwhichpaymenttoupdate,no?
        payment_line._update_payment_line_for_tip(tip_line.price_subtotal_incl)

        #3.flagorderastippedandupdateorderfields
        self.write({
            "is_tipped":True,
            "tip_amount":tip_line.price_subtotal_incl,
            "amount_total":self.amount_total+tip_line.price_subtotal_incl,
            "amount_paid":self.amount_paid+tip_line.price_subtotal_incl,
        })

    defset_no_tip(self):
        """Overridethismethodtointroduceactionwhensettingnotip."""
        self.ensure_one()
        self.write({
            "is_tipped":True,
            "tip_amount":0,
        })

    @api.model
    def_order_fields(self,ui_order):
        order_fields=super(PosOrder,self)._order_fields(ui_order)
        order_fields['table_id']=ui_order.get('table_id',False)
        order_fields['customer_count']=ui_order.get('customer_count',0)
        order_fields['multiprint_resume']=ui_order.get('multiprint_resume',False)
        returnorder_fields

    def_export_for_ui(self,order):
        result=super(PosOrder,self)._export_for_ui(order)
        result['table_id']=order.table_id.id
        returnresult
