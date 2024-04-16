#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,models


classMailComposeMessage(models.TransientModel):
    _inherit='mail.compose.message'

    defsend_mail(self,auto_commit=False):
        context=self._context
        #TODOTDE:cleanthatbroleoneday
        ifcontext.get('website_sale_send_recovery_email')andself.model=='sale.order'andcontext.get('active_ids'):
            self.env['sale.order'].search([
                ('id','in',context.get('active_ids')),
                ('cart_recovery_email_sent','=',False),
                ('is_abandoned_cart','=',True)
            ]).write({'cart_recovery_email_sent':True})
            self=self.with_context(mail_post_autofollow=True)
        returnsuper(MailComposeMessage,self).send_mail(auto_commit=auto_commit)
