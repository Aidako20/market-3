#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models,_
fromflectra.addons.http_routing.models.ir_httpimporturl_for


classWebsite(models.Model):

    _inherit="website"

    channel_id=fields.Many2one('im_livechat.channel',string='WebsiteLiveChatChannel')

    defget_livechat_channel_info(self):
        """Getthelivechatinfodict(buttontext,channelname,...)forthelivechatchannelof
            thecurrentwebsite.
        """
        self.ensure_one()
        ifself.channel_id:
            livechat_info=self.channel_id.sudo().get_livechat_info()
            iflivechat_info['available']:
                livechat_request_session=self._get_livechat_request_session()
                iflivechat_request_session:
                    livechat_info['options']['chat_request_session']=livechat_request_session
            returnlivechat_info
        return{}

    def_get_livechat_request_session(self):
        """
        Checkifthereisanopenedchatrequestforthewebsitelivechatchannelandthecurrentvisitor(fromrequest).
        Ifso,preparethelivechatsessioninformationthatwillbestoredinvisitor'scookies
        andusedbylivechatwidgettodirectlyopenthissessioninsteadofallowingthevisitorto
        initiateanewlivechatsession.
        :param{int}channel_id:channel
        :return:{dict}livechatrequestsessioninformation
        """
        visitor=self.env['website.visitor']._get_visitor_from_request()
        ifvisitor:
            #getactivechat_requestlinkedtovisitor
            chat_request_channel=self.env['mail.channel'].sudo().search([
                ('livechat_visitor_id','=',visitor.id),
                ('livechat_channel_id','=',self.channel_id.id),
                ('livechat_active','=',True),
                ('channel_message_ids','!=',False)
            ],order='create_datedesc',limit=1)
            ifchat_request_channel:
                return{
                    "folded":False,
                    "id":chat_request_channel.id,
                    "operator_pid":[
                        chat_request_channel.livechat_operator_id.id,
                        chat_request_channel.livechat_operator_id.user_livechat_usernameorchat_request_channel.livechat_operator_id.display_name,
                        chat_request_channel.livechat_operator_id.user_livechat_username,
                    ],
                    "name":chat_request_channel.name,
                    "uuid":chat_request_channel.uuid,
                    "type":"chat_request"
                }
        return{}

    defget_suggested_controllers(self):
        suggested_controllers=super(Website,self).get_suggested_controllers()
        suggested_controllers.append((_('LiveSupport'),url_for('/livechat'),'website_livechat'))
        returnsuggested_controllers
