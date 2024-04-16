#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels


classMailThread(models.AbstractModel):
    _inherit='mail.thread'

    def_message_post_after_hook(self,message,msg_vals):
        self.env['mail.bot']._apply_logic(self,msg_vals)
        returnsuper(MailThread,self)._message_post_after_hook(message,msg_vals)
