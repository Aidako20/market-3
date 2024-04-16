#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classMailMessage(models.Model):
    _inherit='mail.message'

    rating_ids=fields.One2many('rating.rating','message_id',groups='base.group_user',string='Relatedratings')
    rating_value=fields.Float(
        'RatingValue',compute='_compute_rating_value',compute_sudo=True,
        store=False,search='_search_rating_value')

    @api.depends('rating_ids','rating_ids.rating')
    def_compute_rating_value(self):
        ratings=self.env['rating.rating'].search([('message_id','in',self.ids),('consumed','=',True)],order='create_dateDESC')
        mapping=dict((r.message_id.id,r.rating)forrinratings)
        formessageinself:
            message.rating_value=mapping.get(message.id,0.0)

    def_search_rating_value(self,operator,operand):
        ratings=self.env['rating.rating'].sudo().search([
            ('rating',operator,operand),
            ('message_id','!=',False)
        ])
        return[('id','in',ratings.mapped('message_id').ids)]
