#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels


classMailComposeMessage(models.TransientModel):
    _inherit='mail.compose.message'

    defsend_mail(self,auto_commit=False):
        ifself.env.context.get('mark_so_as_sent')andself.model=='sale.order':
            self=self.with_context(mail_notify_author=self.env.user.partner_idinself.partner_ids)
        returnsuper(MailComposeMessage,self).send_mail(auto_commit=auto_commit)
