#-*-coding:utf-8-*-
#purchesPartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels


classMailComposeMessage(models.TransientModel):
    _inherit='mail.compose.message'

    defsend_mail(self,auto_commit=False):
        ifself.env.context.get('mark_rfq_as_sent')andself.model=='purchase.order':
            self=self.with_context(mail_notify_author=self.env.user.partner_idinself.partner_ids)
        returnsuper(MailComposeMessage,self).send_mail(auto_commit=auto_commit)
