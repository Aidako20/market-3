#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimporttests,_
fromflectra.addons.website_livechat.tests.commonimportTestLivechatCommon


@tests.tagged('post_install','-at_install')
classTestLivechatUI(tests.HttpCase,TestLivechatCommon):
    defsetUp(self):
        super(TestLivechatUI,self).setUp()
        self.visitor_tour=self.env['website.visitor'].create({
            'name':'VisitorTour',
            'website_id':self.env.ref('website.default_website').id,
        })
        self.target_visitor=self.visitor_tour

    deftest_complete_rating_flow_ui(self):
        self.start_tour("/",'website_livechat_complete_flow_tour')
        self._check_end_of_rating_tours()

    deftest_happy_rating_flow_ui(self):
        self.start_tour("/",'website_livechat_happy_rating_tour')
        self._check_end_of_rating_tours()

    deftest_ok_rating_flow_ui(self):
        self.start_tour("/",'website_livechat_ok_rating_tour')
        self._check_end_of_rating_tours()

    deftest_bad_rating_flow_ui(self):
        self.start_tour("/",'website_livechat_sad_rating_tour')
        self._check_end_of_rating_tours()

    deftest_no_rating_flow_ui(self):
        self.start_tour("/",'website_livechat_no_rating_tour')
        channel=self.env['mail.channel'].search([('livechat_visitor_id','=',self.visitor_tour.id)])
        self.assertEqual(len(channel),1,"Therecanonlybeonechannelcreatedfor'VisitorTour'.")
        self.assertEqual(channel.livechat_active,False,'Livechatmustbeinactiveafterclosingthechatwindow.')

    deftest_no_rating_no_close_flow_ui(self):
        self.start_tour("/",'website_livechat_no_rating_no_close_tour')
        channel=self.env['mail.channel'].search([('livechat_visitor_id','=',self.visitor_tour.id)])
        self.assertEqual(len(channel),1,"Therecanonlybeonechannelcreatedfor'VisitorTour'.")
        self.assertEqual(channel.livechat_active,True,'Livechatmustbeactivewhilethechatwindowisnotclosed.')

    deftest_empty_chat_request_flow_no_rating_no_close_ui(self):
        #Openanemptychatrequest
        self.visitor_tour.with_user(self.operator).action_send_chat_request()
        chat_request=self.env['mail.channel'].search([('livechat_visitor_id','=',self.visitor_tour.id),('livechat_active','=',True)])

        #Visitoraskanewlivechatsessionbeforetheoperatorstarttosendmessageinchatrequestsession
        self.start_tour("/",'website_livechat_no_rating_no_close_tour')

        #Visitor'ssessionmustbeactive(getsthepriority)
        channel=self.env['mail.channel'].search([('livechat_visitor_id','=',self.visitor_tour.id),('livechat_active','=',True)])
        self.assertEqual(len(channel),1,"Therecanonlybeonechannelcreatedfor'VisitorTour'.")
        self.assertEqual(channel.livechat_active,True,'Livechatmustbeactivewhilethechatwindowisnotclosed.')

        #Checkthatthechatrequesthasbeencanceled.
        chat_request.invalidate_cache()
        self.assertEqual(chat_request.livechat_active,False,"Thelivechatrequestmustbeinactiveasthevisitorstartedhimselfalivechatsession.")

    deftest_chat_request_flow_with_rating_ui(self):
        #Openachatrequest
        self.visitor_tour.with_user(self.operator).action_send_chat_request()
        chat_request=self.env['mail.channel'].search([('livechat_visitor_id','=',self.visitor_tour.id),('livechat_active','=',True)])

        #Operatorsendamessagetothevisitor
        self._send_message(chat_request,self.operator.email,"Hellomyfriend!",author_id=self.operator.partner_id.id)
        self.assertEqual(len(chat_request.message_ids),1,"Numberofmessagesincorrect.")

        #Visitorcomestothewebsiteandreceivesthechatrequest
        self.start_tour("/",'website_livechat_chat_request_part_1_no_close_tour')

        #Checkthatthecurrentsessionisthechatrequest
        channel=self.env['mail.channel'].search([('livechat_visitor_id','=',self.visitor_tour.id),('livechat_active','=',True)])
        self.assertEqual(len(channel),1,"Therecanonlybeonechannelcreatedfor'VisitorTour'.")
        self.assertEqual(channel,chat_request,"Theactivelivechatsessionmustbethechatrequestone.")

        #Visitorreloadthepageandcontinuesthechatwiththeoperatornormally
        self.start_tour("/",'website_livechat_chat_request_part_2_end_session_tour')
        self._check_end_of_rating_tours()

    def_check_end_of_rating_tours(self):
        channel=self.env['mail.channel'].search([('livechat_visitor_id','=', self.visitor_tour.id)])
        self.assertEqual(len(channel),1,"Therecanonlybeonechannelcreatedfor'VisitorTour'.")
        self.assertEqual(channel.livechat_active,False,'Livechatmustbeinactiveafterrating.')
