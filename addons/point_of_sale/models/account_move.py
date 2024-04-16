#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models,api


classAccountMove(models.Model):
    _inherit='account.move'

    pos_order_ids=fields.One2many('pos.order','account_move')

    def_stock_account_get_last_step_stock_moves(self):
        stock_moves=super(AccountMove,self)._stock_account_get_last_step_stock_moves()
        forinvoiceinself.filtered(lambdax:x.move_type=='out_invoice'):
            stock_moves+=invoice.sudo().mapped('pos_order_ids.picking_ids.move_lines').filtered(lambdax:x.state=='done'andx.location_dest_id.usage=='customer')
        forinvoiceinself.filtered(lambdax:x.move_type=='out_refund'):
            stock_moves+=invoice.sudo().mapped('pos_order_ids.picking_ids.move_lines').filtered(lambdax:x.state=='done'andx.location_id.usage=='customer')
        returnstock_moves


    def_tax_tags_need_inversion(self,move,is_refund,tax_type):
        #POSorderoperationsarehandledbythetaxreportjustlikeinvoices;
        #weshouldneverinverttheirtags.
        #Don'ttakeordersorsessionswithoutmove.
        ifmove.move_type=='entry'andmove._origin.id:
            orders_count=self.env['pos.order'].search_count([('account_move','=',move._origin.id)])
            sessions_count=self.env['pos.session'].search_count([('move_id','=',move._origin.id)])
            iforders_count+sessions_count:
                returnFalse
        returnsuper()._tax_tags_need_inversion(move,is_refund,tax_type)

classAccountMoveLine(models.Model):
    _inherit='account.move.line'

    def_stock_account_get_anglo_saxon_price_unit(self):
        self.ensure_one()
        ifnotself.product_id:
            returnself.price_unit
        price_unit=super(AccountMoveLine,self)._stock_account_get_anglo_saxon_price_unit()
        order=self.move_id.pos_order_ids
        iforder:
            price_unit=order._get_pos_anglo_saxon_price_unit(self.product_id,self.move_id.partner_id.id,self.quantity)
        returnprice_unit

    def_get_not_entry_condition(self,aml):
        #OverriddensothatsaleentrymovescreatedparPOSstillhavetheiramountinverted
        #in_compute_tax_audit()
        rslt=super()._get_not_entry_condition(aml)

        sessions_count=self.env['pos.session'].search_count([('move_id','=',aml.move_id.id)])
        pos_orders_count=self.env['pos.order'].search_count([('account_move','=',aml.move_id.id)])

        returnrsltor(sessions_count+pos_orders_count)

    def_get_refund_tax_audit_condition(self,aml):
        #Overriddensothatthereturnscanbedetectedascreditnotesbythetaxauditcomputation
        rslt=super()._get_refund_tax_audit_condition(aml)

        ifaml.move_id.is_invoice():
            #Wedon'tneedtochecktheposordersforthismovelineifaninvoice
            #islinkedtoit;weknowthattheinvoicetypetellsuswhetherit'sarefund
            returnrslt

        sessions_count=self.env['pos.session'].search_count([('move_id','=',aml.move_id.id)])
        pos_orders_count=self.env['pos.order'].search_count([('account_move','=',aml.move_id.id)])

        returnrsltor(sessions_count+pos_orders_countandaml.debit>0)
