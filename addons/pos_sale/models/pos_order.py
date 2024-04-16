#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classPosOrder(models.Model):
    _inherit='pos.order'

    currency_rate=fields.Float(compute='_compute_currency_rate',store=True,digits=0,readonly=True)
    crm_team_id=fields.Many2one('crm.team',string="SalesTeam")

    @api.model
    def_complete_values_from_session(self,session,values):
        values=super(PosOrder,self)._complete_values_from_session(session,values)
        values.setdefault('crm_team_id',session.config_id.crm_team_id.id)
        returnvalues

    @api.depends('pricelist_id.currency_id','date_order','company_id')
    def_compute_currency_rate(self):
        fororderinself:
            date_order=order.date_orderorfields.Datetime.now()
            order.currency_rate=self.env['res.currency']._get_conversion_rate(order.company_id.currency_id,order.pricelist_id.currency_id,order.company_id,date_order)

    def_prepare_invoice_vals(self):
        invoice_vals=super(PosOrder,self)._prepare_invoice_vals()
        invoice_vals['team_id']=self.crm_team_id
        addr=self.partner_id.address_get(['delivery'])
        invoice_vals['partner_shipping_id']=addr['delivery']
        returninvoice_vals
