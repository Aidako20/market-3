#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimporttests
fromflectra.addons.website_livechat.tests.commonimportTestLivechatCommon


@tests.tagged('post_install','-at_install')
classTestLivechatRequestHttpCase(tests.HttpCase,TestLivechatCommon):
    deftest_livechat_request_complete_flow(self):
        self._clean_livechat_sessions()

        #Sendfirstchatrequest-Openchatfromoperatorside
        channel_1=self._common_chat_request_flow()
        #VisitorRatestheconversation(Good)
        self._send_rating(channel_1,self.visitor,5)

        #OperatorRe-Sendachatrequest
        channel_2=self._common_chat_request_flow()
        #VisitorRatestheconversation(Bad)
        self._send_rating(channel_2,self.visitor,1,"Stopbotheringme!Ihateyou</3!")

    deftest_cancel_chat_request_on_visitor_demand(self):
        self._clean_livechat_sessions()

        self.operator_b=self.env['res.users'].create({
            'name':'OperatorMarc',
            'login':'operator_b',
            'email':'operatormarc@example.com',
            'password':"operatormarc",
            'livechat_username':"Marco'rEl",
        })

        #OpenChatRequest
        self.visitor.with_user(self.operator_b).action_send_chat_request()
        chat_request=self.env['mail.channel'].search([('livechat_visitor_id','=',self.visitor.id),('livechat_active','=',True)])
        self.assertEqual(chat_request.livechat_operator_id,self.operator_b.partner_id,"OperatorforactivelivechatsessionmustbeOperatorMarc")

        #Clickonlivechatbuttonatclientside
        res=self.opener.post(url=self.open_chat_url,json=self.open_chat_params)
        self.assertEqual(res.status_code,200)
        channel=self.env['mail.channel'].search([('livechat_visitor_id','=',self.visitor.id),
                                                   ('livechat_active','=',True)])

        #Checkthatthechatrequesthasbeencanceled.
        chat_request.invalidate_cache()
        self.assertEqual(chat_request.livechat_active,False,"Thelivechatrequestmustbeinactiveasthevisitorstartedhimselfalivechatsession.")
        self.assertEqual(len(channel),1)
        self.assertEqual(channel.livechat_operator_id,self.operator.partner_id,"OperatorforactivelivechatsessionmustbeMichelOperator")

    def_common_chat_request_flow(self):
        self.visitor.with_user(self.operator).action_send_chat_request()
        channel=self.env['mail.channel'].search([('livechat_visitor_id','=',self.visitor.id),('livechat_active','=',True)])
        self.assertEqual(len(channel),1)
        self.assertEqual(channel.livechat_operator_id,self.operator.partner_id,"MichelOperatorshouldbetheoperatorofthischannel.")
        self.assertEqual(len(channel.message_ids),0)

        #OperatorSendsmessage
        self._send_message(channel,self.operator.email,"HelloAgain!",author_id=self.operator.partner_id.id)
        self.assertEqual(len(channel.message_ids),1)

        #VisitorAnswers
        self._send_message(channel,self.visitor.display_name,"AnswerfromVisitor")
        self.assertEqual(len(channel.message_ids),2)

        #VisitorLeavetheconversation
        channel._close_livechat_session()
        self.assertEqual(len(channel.message_ids),3)
        self.assertEqual(channel.message_ids[0].author_id,self.env.ref('base.partner_root'),"Flectrabotmustbethesenderofthe'haslefttheconversation'message.")
        self.assertEqual(channel.message_ids[0].body,"<p>%shaslefttheconversation.</p>"%self.visitor.display_name)
        self.assertEqual(channel.livechat_active,False,"Thelivechatsessionmustbeinactiveasthevisitorsenthisfeedback.")

        returnchannel

    def_clean_livechat_sessions(self):
        #cleaneverypossiblemailchannellinkedtothevisitor
        active_channels=self.env['mail.channel'].search([('livechat_visitor_id','=',self.visitor.id),('livechat_active','=',True)])
        foractive_channelinactive_channels:
            active_channel._close_livechat_session()
