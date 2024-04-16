#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,models


classMailThread(models.AbstractModel):
    _inherit='mail.thread'

    @api.returns('mail.message',lambdavalue:value.id)
    defmessage_post(self,**kwargs):
        rating_value=kwargs.pop('rating_value',False)
        rating_feedback=kwargs.pop('rating_feedback',False)
        message=super(MailThread,self).message_post(**kwargs)

        #createrating.ratingrecordlinkedtogivenrating_value.Usingsudoasportalusersmayhave
        #rightstocreatemessagesandthereforeratings(securityshouldbecheckedbeforehand)
        ifrating_value:
            ir_model=self.env['ir.model'].sudo().search([('model','=',self._name)])
            self.env['rating.rating'].sudo().create({
                'rating':float(rating_value)ifrating_valueisnotNoneelseFalse,
                'feedback':rating_feedback,
                'res_model_id':ir_model.id,
                'res_id':self.id,
                'message_id':message.id,
                'consumed':True,
                'partner_id':self.env.user.partner_id.id,
            })
        returnmessage
