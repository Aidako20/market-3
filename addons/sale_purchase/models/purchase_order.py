#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_


classPurchaseOrder(models.Model):
    _inherit="purchase.order"

    sale_order_count=fields.Integer(
        "NumberofSourceSale",
        compute='_compute_sale_order_count',
        groups='sales_team.group_sale_salesman')

    @api.depends('order_line.sale_order_id')
    def_compute_sale_order_count(self):
        forpurchaseinself:
            purchase.sale_order_count=len(purchase._get_sale_orders())

    defaction_view_sale_orders(self):
        self.ensure_one()
        sale_order_ids=self._get_sale_orders().ids
        action={
            'res_model':'sale.order',
            'type':'ir.actions.act_window',
        }
        iflen(sale_order_ids)==1:
            action.update({
                'view_mode':'form',
                'res_id':sale_order_ids[0],
            })
        else:
            action.update({
                'name':_('SourcesSaleOrders%s',self.name),
                'domain':[('id','in',sale_order_ids)],
                'view_mode':'tree,form',
            })
        returnaction

    defbutton_cancel(self):
        result=super(PurchaseOrder,self).button_cancel()
        self.sudo()._activity_cancel_on_sale()
        returnresult

    def_get_sale_orders(self):
        returnself.order_line.sale_order_id

    def_activity_cancel_on_sale(self):
        """IfsomePOarecancelled,weneedtoputanactivityontheiroriginSO(onlytheopenones).SinceaPOcanhave
            beenmodifiedbyseveralSO,whencancellingonePO,manynextactivitiescanbescheduldedondifferentSO.
        """
        sale_to_notify_map={} #mapSO->recordsetofPOas{sale.order:set(purchase.order.line)}
        fororderinself:
            forpurchase_lineinorder.order_line:
                ifpurchase_line.sale_line_id:
                    sale_order=purchase_line.sale_line_id.order_id
                    sale_to_notify_map.setdefault(sale_order,self.env['purchase.order.line'])
                    sale_to_notify_map[sale_order]|=purchase_line

        forsale_order,purchase_order_linesinsale_to_notify_map.items():
            sale_order._activity_schedule_with_view('mail.mail_activity_data_warning',
                user_id=sale_order.user_id.idorself.env.uid,
                views_or_xmlid='sale_purchase.exception_sale_on_purchase_cancellation',
                render_context={
                    'purchase_orders':purchase_order_lines.mapped('order_id'),
                    'purchase_order_lines':purchase_order_lines,
            })


classPurchaseOrderLine(models.Model):
    _inherit='purchase.order.line'

    sale_order_id=fields.Many2one(related='sale_line_id.order_id',string="SaleOrder",store=True,readonly=True)
    sale_line_id=fields.Many2one('sale.order.line',string="OriginSaleItem",index=True,copy=False)
