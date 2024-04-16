#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importdatetime

fromflectraimporttests,_
fromflectra.addons.website_livechat.tests.commonimportTestLivechatCommon


@tests.tagged('post_install','-at_install')
classTestLivechatBasicFlowHttpCase(tests.HttpCase,TestLivechatCommon):
    deftest_visitor_banner_history(self):
        #createvisitorhistory
        self.env['website.track'].create([{
            'page_id':self.env.ref('website.homepage_page').id,
            'visitor_id':self.visitor.id,
            'visit_datetime':self.base_datetime,
        },{
            'page_id':self.env.ref('website.contactus_page').id,
            'visitor_id':self.visitor.id,
            'visit_datetime':self.base_datetime-datetime.timedelta(minutes=10),
        },{
            'page_id':self.env.ref('website.homepage_page').id,
            'visitor_id':self.visitor.id,
            'visit_datetime':self.base_datetime-datetime.timedelta(minutes=20),
        }])

        handmade_history="%s(21:10)→%s(21:20)→%s(21:30)"%(
            self.env.ref('website.homepage_page').name,
            self.env.ref('website.contactus_page').name,
            self.env.ref('website.homepage_page').name,
        )
        history=self.env['mail.channel']._get_visitor_history(self.visitor)

        self.assertEqual(history,handmade_history)

    deftest_livechat_username(self):
        #Openanewlivechat
        res=self.opener.post(url=self.open_chat_url,json=self.open_chat_params)
        self.assertEqual(res.status_code,200)
        channel_1=self.env['mail.channel'].search([('livechat_visitor_id','=',self.visitor.id),('livechat_active','=',True)],limit=1)

        #CheckChannelnaming
        self.assertEqual(channel_1.name,"%s%s"%(self.visitor.display_name,self.operator.livechat_username))
        channel_1.unlink()

        #Removelivechat_username
        self.operator.livechat_username=False

        #Openanewlivechat
        res=self.opener.post(url=self.open_chat_url,json=self.open_chat_params)
        self.assertEqual(res.status_code,200)
        channel_2=self.env['mail.channel'].search([('livechat_visitor_id','=',self.visitor.id),('livechat_active','=',True)],limit=1)

        #CheckChannelnaming
        self.assertEqual(channel_2.name,"%s%s"%(self.visitor.display_name,self.operator.name))

    deftest_basic_flow_with_rating(self):
        channel=self._common_basic_flow()

        self._send_rating(channel,self.visitor,5,"Thisdeboulonnagewasfinebutnottopitop.")

        channel._close_livechat_session()

        self.assertEqual(len(channel.message_ids),4)
        self.assertEqual(channel.message_ids[0].author_id,self.env.ref('base.partner_root'),"Flectrabotmustbethesenderofthe'haslefttheconversation'message.")
        self.assertEqual(channel.message_ids[0].body,"<p>%shaslefttheconversation.</p>"%self.visitor.display_name)
        self.assertEqual(channel.livechat_active,False,"Thelivechatsessionmustbeinactiveasthevisitorsenthisfeedback.")

    deftest_basic_flow_without_rating(self):
        channel=self._common_basic_flow()

        #haslefttheconversation
        channel._close_livechat_session()
        self.assertEqual(len(channel.message_ids),3)
        self.assertEqual(channel.message_ids[0].author_id,self.env.ref('base.partner_root'),"Flectrabotmustbetheauthorthemessage.")
        self.assertEqual(channel.message_ids[0].body,"<p>%shaslefttheconversation.</p>"%self.visitor.display_name)
        self.assertEqual(channel.livechat_active,False,"Thelivechatsessionmustbeinactivesincevisitorhaslefttheconversation.")

    deftest_visitor_info_access_rights(self):
        channel=self._common_basic_flow()
        self.authenticate(self.operator.login,'ideboulonate')

        #Retrievechannelsinformation,visitorinfoshouldbethere
        res=self.opener.get(self.message_info_url,json={})
        self.assertEqual(res.status_code,200)
        messages_info=res.json().get('result',{})
        livechat_info=messages_info['channel_slots']['channel_livechat']
        self.assertIn('visitor',livechat_info[0])

        #Removeaccesstovisitorsandtryagain,visitorsinfoshouldn'tbeincluded
        self.operator.groups_id-=self.group_livechat_user
        res=self.opener.get(self.message_info_url,json={})
        self.assertEqual(res.status_code,200)
        messages_info=res.json().get('result',{})
        livechat_info=messages_info['channel_slots']['channel_livechat']
        self.assertNotIn('visitor',livechat_info[0])

    def_common_basic_flow(self):
        #Openanewlivechat
        res=self.opener.post(url=self.open_chat_url,json=self.open_chat_params)
        self.assertEqual(res.status_code,200)

        channel=self.env['mail.channel'].search([('livechat_visitor_id','=',self.visitor.id),('livechat_active','=',True)],limit=1)

        #CheckChannelandVisitornaming
        self.assertEqual(self.visitor.display_name,"%s#%s"%(_("WebsiteVisitor"),self.visitor.id))
        self.assertEqual(channel.name,"%s%s"%(self.visitor.display_name,self.operator.livechat_username))

        #PostMessagefromvisitor
        self._send_message(channel,self.visitor.display_name,"MessagefromVisitor")

        self.assertEqual(len(channel.message_ids),1)
        self.assertEqual(channel.message_ids[0].author_id.id,False,"Theauthorofthemessageisnotapartner.")
        self.assertEqual(channel.message_ids[0].email_from,self.visitor.display_name,"Thesender'semailshouldbethevisitor'semail.")
        self.assertEqual(channel.message_ids[0].body,"<p>MessagefromVisitor</p>")
        self.assertEqual(channel.livechat_active,True,"Thelivechatsessionmustbeactiveasthevisitordidnotlefttheconversationyet.")

        #Postmessagefromoperator
        self._send_message(channel,self.operator.email,"MessagefromOperator",author_id=self.operator.partner_id.id)

        self.assertEqual(len(channel.message_ids),2)
        self.assertEqual(channel.message_ids[0].author_id,self.operator.partner_id,"Theauthorofthemessageshouldbetheoperator.")
        self.assertEqual(channel.message_ids[0].email_from,self.operator.email,"Thesender'semailshouldbetheoperator'semail.")
        self.assertEqual(channel.message_ids[0].body,"<p>MessagefromOperator</p>")
        self.assertEqual(channel.livechat_active,True,"Thelivechatsessionmustbeactiveasthevisitordidnotlefttheconversationyet.")

        returnchannel
