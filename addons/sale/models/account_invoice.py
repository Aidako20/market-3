#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_


classAccountMove(models.Model):
    _name='account.move'
    _inherit=['account.move','utm.mixin']

    @api.model
    def_get_invoice_default_sale_team(self):
        returnself.env['crm.team']._get_default_team_id()

    team_id=fields.Many2one(
        'crm.team',string='SalesTeam',default=_get_invoice_default_sale_team,
        domain="['|',('company_id','=',False),('company_id','=',company_id)]")
    partner_shipping_id=fields.Many2one(
        'res.partner',
        string='DeliveryAddress',
        readonly=True,
        states={'draft':[('readonly',False)]},
        domain="['|',('company_id','=',False),('company_id','=',company_id)]",
        help="Deliveryaddressforcurrentinvoice.")

    @api.onchange('partner_shipping_id','company_id')
    def_onchange_partner_shipping_id(self):
        """
        Triggerthechangeoffiscalpositionwhentheshippingaddressismodified.
        """
        delivery_partner_id=self._get_invoice_delivery_partner_id()
        fiscal_position=self.env['account.fiscal.position'].with_company(self.company_id).get_fiscal_position(
            self.partner_id.id,delivery_id=delivery_partner_id)

        iffiscal_position:
            self.fiscal_position_id=fiscal_position

    defunlink(self):
        downpayment_lines=self.mapped('line_ids.sale_line_ids').filtered(lambdaline:line.is_downpaymentandline.invoice_lines<=self.mapped('line_ids'))
        res=super(AccountMove,self).unlink()
        ifdownpayment_lines:
            downpayment_lines.unlink()
        returnres

    @api.onchange('partner_id')
    def_onchange_partner_id(self):
        #OVERRIDE
        #Recompute'partner_shipping_id'basedon'partner_id'.
        addr=self.partner_id.address_get(['delivery'])
        self.partner_shipping_id=addrandaddr.get('delivery')

        returnsuper(AccountMove,self)._onchange_partner_id()

    @api.onchange('invoice_user_id')
    defonchange_user_id(self):
        ifself.invoice_user_idandself.invoice_user_id.sale_team_id:
            self.team_id=self.env['crm.team']._get_default_team_id(user_id=self.invoice_user_id.id,domain=[('company_id','=',self.company_id.id)])

    def_reverse_moves(self,default_values_list=None,cancel=False):
        #OVERRIDE
        ifnotdefault_values_list:
            default_values_list=[{}formoveinself]
        formove,default_valuesinzip(self,default_values_list):
            default_values.update({
                'campaign_id':move.campaign_id.id,
                'medium_id':move.medium_id.id,
                'source_id':move.source_id.id,
            })
        returnsuper()._reverse_moves(default_values_list=default_values_list,cancel=cancel)

    def_post(self,soft=True):
        #OVERRIDE
        #Auto-reconciletheinvoicewithpaymentscomingfromtransactions.
        #It'susefulwhenyouhavea"paid"saleorder(usingapaymenttransaction)andyouinvoiceitlater.
        posted=super()._post(soft)

        forinvoiceinposted.filtered(lambdamove:move.is_invoice()):
            payments=invoice.mapped('transaction_ids.payment_id').filtered(lambdap:p.state=='posted')
            move_lines=payments.line_ids.filtered(lambdaline:line.account_internal_typein('receivable','payable')andnotline.reconciled)
            forlineinmove_lines:
                invoice.js_assign_outstanding_line(line.id)
        returnposted

    defaction_invoice_paid(self):
        #OVERRIDE
        res=super(AccountMove,self).action_invoice_paid()
        todo=set()
        forinvoiceinself.filtered(lambdamove:move.is_invoice()):
            forlineininvoice.invoice_line_ids:
                forsale_lineinline.sale_line_ids:
                    todo.add((sale_line.order_id,invoice.name))
        for(order,name)intodo:
            order.message_post(body=_("Invoice%spaid",name))
        returnres

    def_get_invoice_delivery_partner_id(self):
        #OVERRIDE
        self.ensure_one()
        returnself.partner_shipping_id.idorsuper(AccountMove,self)._get_invoice_delivery_partner_id()

    def_is_downpayment(self):
        #OVERRIDE
        self.ensure_one()
        returnself.line_ids.sale_line_idsandall(sale_line.is_downpaymentforsale_lineinself.line_ids.sale_line_ids)orFalse
