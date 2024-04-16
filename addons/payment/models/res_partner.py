#coding:utf-8

fromflectraimportapi,fields,models


classres_partner(models.Model):
    _name='res.partner'
    _inherit='res.partner'

    payment_token_ids=fields.One2many('payment.token','partner_id','PaymentTokens')
    payment_token_count=fields.Integer('CountPaymentToken',compute='_compute_payment_token_count')

    @api.depends('payment_token_ids')
    def_compute_payment_token_count(self):
        payment_data=self.env['payment.token'].read_group([
            ('partner_id','in',self.ids)],['partner_id'],['partner_id'])
        mapped_data=dict([(payment['partner_id'][0],payment['partner_id_count'])forpaymentinpayment_data])
        forpartnerinself:
            partner.payment_token_count=mapped_data.get(partner.id,0)
