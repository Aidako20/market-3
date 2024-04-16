#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.tests.commonimportTransactionCase


classTestGetMailChannel(TransactionCase):
    defsetUp(self):
        super(TestGetMailChannel,self).setUp()
        self.operators=self.env['res.users'].create([{
            'name':'Michel',
            'login':'michel',
            'livechat_username':"MichelOperator",
        },{
            'name':'Paul',
            'login':'paul'
        },{
            'name':'Pierre',
            'login':'pierre'
        },{
            'name':'Jean',
            'login':'jean'
        },{
            'name':'Georges',
            'login':'georges'
        }])

        self.visitor_user=self.env['res.users'].create({
            'name':'Rajesh',
            'login':'rajesh',
            'country_id':self.ref('base.in'),
        })

        self.livechat_channel=self.env['im_livechat.channel'].create({
            'name':'Thechannel',
            'user_ids':[(6,0,self.operators.ids)]
        })

        operators=self.operators
        defget_available_users(self):
            returnoperators

        self.patch(type(self.env['im_livechat.channel']),'_get_available_users',get_available_users)

    deftest_get_mail_channel(self):
        """Foralivechatwith5availableoperators,weopen5channels5times(25channelstotal).
        Forevery5channelsopening,wecheckthatalloperatorswereassigned.
        """

        foriinrange(5):
            mail_channels=self._open_livechat_mail_channel()
            channel_operators=[channel_info['operator_pid']forchannel_infoinmail_channels]
            channel_operator_ids=[channel_operator[0]forchannel_operatorinchannel_operators]
            self.assertTrue(all(partner_idinchannel_operator_idsforpartner_idinself.operators.mapped('partner_id').ids))

    deftest_channel_get_livechat_visitor_info(self):
        belgium=self.env.ref('base.be')
        public_user=self.env.ref('base.public_user')
        test_user=self.env['res.users'].create({'name':'Roger','login':'roger','country_id':belgium.id})

        #ensurevisitorinfoarecorrectwithanonymous
        operator=self.operators[0]
        channel_info=self.livechat_channel.with_user(public_user)._open_livechat_mail_channel(anonymous_name='Visitor22',previous_operator_id=operator.partner_id.id,country_id=belgium.id)
        visitor_info=channel_info['livechat_visitor']
        self.assertFalse(visitor_info['id'])
        self.assertEqual(visitor_info['name'],"Visitor22")
        self.assertEqual(visitor_info['country'],(20,"Belgium"))

        #ensurememberinfoarehidden(inparticularemailandrealnamewhenlivechatusernameispresent)
        self.assertEqual(sorted(channel_info['members'],key=lambdam:m['id']),sorted([{
            'email':False,
            'id':operator.partner_id.id,
            'im_status':False,
            'livechat_username':'MichelOperator',
            'name':'MichelOperator',
        },{
            'email':False,
            'id':public_user.partner_id.id,
            'im_status':False,
            'livechat_username':False,
            'name':'Publicuser',
        }],key=lambdam:m['id']))

        #ensurevisitorinfoarecorrectwithrealuser
        channel_info=self.livechat_channel.with_user(test_user)._open_livechat_mail_channel(anonymous_name='whatever',user_id=test_user.id)
        visitor_info=channel_info['livechat_visitor']
        self.assertEqual(visitor_info['id'],test_user.partner_id.id)
        self.assertEqual(visitor_info['name'],"Roger")
        self.assertEqual(visitor_info['country'],(20,"Belgium"))

        #ensurevisitorinfoarecorrectwhenoperatoristestinghimself
        operator=self.operators[0]
        channel_info=self.livechat_channel.with_user(operator)._open_livechat_mail_channel(anonymous_name='whatever',previous_operator_id=operator.partner_id.id,user_id=operator.id)
        self.assertEqual(channel_info['operator_pid'],(operator.partner_id.id,"MichelOperator"))
        visitor_info=channel_info['livechat_visitor']
        self.assertEqual(visitor_info['id'],operator.partner_id.id)
        self.assertEqual(visitor_info['name'],"Michel")
        self.assertFalse(visitor_info['country'])

    def_open_livechat_mail_channel(self):
        mail_channels=[]

        foriinrange(5):
            mail_channel=self.livechat_channel._open_livechat_mail_channel('Anonymous')
            mail_channels.append(mail_channel)
            #sendamessagetomarkthischannelas'active'
            self.env['mail.channel'].browse(mail_channel['id']).write({
                'channel_message_ids':[(0,0,{'body':'cc'})]
            })

        returnmail_channels

    deftest_operator_livechat_username(self):
        """Ensurestheoperatorlivechat_usernameisreturnedby`channel_fetch_message`,whichis
        themethodcalledbythepublicroutedisplayingchathistory."""
        public_user=self.env.ref('base.public_user')
        operator=self.operators[0]
        operator.write({
            'email':'michel@example.com',
            'livechat_username':'Michelatyourservice',
        })
        channel_info=self.livechat_channel.with_user(public_user)._open_livechat_mail_channel(anonymous_name='whatever')
        channel=self.env['mail.channel'].browse(channel_info['id'])
        channel.with_user(operator).message_post(body='Hello',message_type='comment',subtype_xmlid='mail.mt_comment')
        message_formats=channel.with_user(public_user).channel_fetch_message()
        self.assertEqual(len(message_formats),1)
        self.assertEqual(message_formats[0]['author_id'][0],operator.partner_id.id)
        self.assertEqual(message_formats[0]['author_id'][1],operator.livechat_username)
        self.assertEqual(message_formats[0]['author_id'][2],operator.livechat_username)
        self.assertFalse(message_formats[0].get('email_from'),"shouldnotsendemail_fromtolivechatuser")
