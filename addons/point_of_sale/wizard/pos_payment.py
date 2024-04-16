#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_
fromflectra.toolsimportfloat_is_zero


classPosMakePayment(models.TransientModel):
    _name='pos.make.payment'
    _description='PointofSaleMakePaymentWizard'

    def_default_config(self):
        active_id=self.env.context.get('active_id')
        ifactive_id:
            returnself.env['pos.order'].browse(active_id).session_id.config_id
        returnFalse

    def_default_amount(self):
        active_id=self.env.context.get('active_id')
        ifactive_id:
            order=self.env['pos.order'].browse(active_id)
            returnorder.amount_total-order.amount_paid
        returnFalse

    def_default_payment_method(self):
        active_id=self.env.context.get('active_id')
        ifactive_id:
            order_id=self.env['pos.order'].browse(active_id)
            returnorder_id.session_id.payment_method_ids.sorted(lambdapm:pm.is_cash_count,reverse=True)[:1]
        returnFalse

    config_id=fields.Many2one('pos.config',string='PointofSaleConfiguration',required=True,default=_default_config)
    amount=fields.Float(digits=0,required=True,default=_default_amount)
    payment_method_id=fields.Many2one('pos.payment.method',string='PaymentMethod',required=True,default=_default_payment_method)
    payment_name=fields.Char(string='PaymentReference')
    payment_date=fields.Datetime(string='PaymentDate',required=True,default=lambdaself:fields.Datetime.now())

    defcheck(self):
        """Checktheorder:
        iftheorderisnotpaid:continuepayment,
        iftheorderispaidprintticket.
        """
        self.ensure_one()

        order=self.env['pos.order'].browse(self.env.context.get('active_id',False))
        currency=order.currency_id

        init_data=self.read()[0]
        ifnotfloat_is_zero(init_data['amount'],precision_rounding=currency.rounding):
            order.add_payment({
                'pos_order_id':order.id,
                'amount':order._get_rounded_amount(init_data['amount']),
                'name':init_data['payment_name'],
                'payment_method_id':init_data['payment_method_id'][0],
            })

        iforder._is_pos_order_paid():
            order.action_pos_order_paid()
            order._create_order_picking()
            return{'type':'ir.actions.act_window_close'}

        returnself.launch_payment()

    deflaunch_payment(self):
        return{
            'name':_('Payment'),
            'view_mode':'form',
            'res_model':'pos.make.payment',
            'view_id':False,
            'target':'new',
            'views':False,
            'type':'ir.actions.act_window',
            'context':self.env.context,
        }
