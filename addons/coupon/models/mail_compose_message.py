#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels


classMailComposeMessage(models.TransientModel):
    _inherit='mail.compose.message'

    defsend_mail(self,**kwargs):
        forwizardinself:
            ifself._context.get('mark_coupon_as_sent')andwizard.model=='coupon.coupon'andwizard.partner_ids:
                #Markcouponassentinsudo,ashelpdeskusersdon'thavetherighttowriteoncoupons
                self.env[wizard.model].sudo().browse(wizard.res_id).state='sent'
        returnsuper().send_mail(**kwargs)
