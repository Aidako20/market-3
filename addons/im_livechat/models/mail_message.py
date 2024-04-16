#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels


classMailMessage(models.Model):
    _inherit='mail.message'

    def_message_format(self,fnames):
        """Overridetoremoveemail_fromandtoreturnthelivechatusernameifapplicable.
        Athirdparamisaddedtotheauthor_idtupleinthiscasetobeabletodifferentiateit
        fromthenormalnameinclientcode."""
        vals_list=super()._message_format(fnames=fnames)
        forvalsinvals_list:
            message_sudo=self.browse(vals['id']).sudo().with_prefetch(self.ids)
            ifmessage_sudo.model=='mail.channel'andself.env['mail.channel'].browse(message_sudo.res_id).channel_type=='livechat':
                vals.pop('email_from')
                ifmessage_sudo.author_id.user_livechat_username:
                    vals['author_id']=(message_sudo.author_id.id,message_sudo.author_id.user_livechat_username,message_sudo.author_id.user_livechat_username)
        returnvals_list
