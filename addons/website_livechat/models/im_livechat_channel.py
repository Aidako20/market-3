#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels,_


classImLivechatChannel(models.Model):
    _inherit='im_livechat.channel'

    def_get_livechat_mail_channel_vals(self,anonymous_name,operator,user_id=None,country_id=None):
        mail_channel_vals=super(ImLivechatChannel,self)._get_livechat_mail_channel_vals(anonymous_name,operator,user_id=user_id,country_id=country_id)
        visitor_sudo=self.env['website.visitor']._get_visitor_from_request()
        ifvisitor_sudo:
            mail_channel_vals['livechat_visitor_id']=visitor_sudo.id
            ifnotuser_id:
                mail_channel_vals['anonymous_name']=visitor_sudo.display_name+('(%s)'%visitor_sudo.country_id.nameifvisitor_sudo.country_idelse'')
            #Aschatrequestedbythevisitor,deletethechatrequestedbyanoperatorifanytoavoidconflictsbetweentwoflows
            #TODODBE:Movethisintothepropermethod(openorinitmailchannel)
            chat_request_channel=self.env['mail.channel'].sudo().search([('livechat_visitor_id','=',visitor_sudo.id),('livechat_active','=',True)])
            formail_channelinchat_request_channel:
                mail_channel._close_livechat_session(cancel=True,operator=operator.name)

        returnmail_channel_vals
