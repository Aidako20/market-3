#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromunittest.mockimportpatch

fromflectra.addons.test_mail.tests.commonimportTestMailCommon,TestRecipients
fromflectra.testsimporttagged
fromflectra.toolsimportmute_logger


@tagged("flectrabot")
classTestFlectrabot(TestMailCommon,TestRecipients):

    @classmethod
    defsetUpClass(cls):
        super(TestFlectrabot,cls).setUpClass()
        cls.test_record=cls.env['mail.test.simple'].with_context(cls._test_context).create({'name':'Test','email_from':'ignasse@example.com'})

        cls.flectrabot=cls.env.ref("base.partner_root")
        cls.message_post_default_kwargs={
            'body':'',
            'attachment_ids':[],
            'message_type':'comment',
            'partner_ids':[],
            'subtype_xmlid':'mail.mt_comment'
        }
        cls.flectrabot_ping_body='<ahref="http://flectrahq.com/web#model=res.partner&amp;id=%s"class="o_mail_redirect"data-oe-id="%s"data-oe-model="res.partner"target="_blank">@FlectraBot</a>'%(cls.flectrabot.id,cls.flectrabot.id)
        cls.test_record_employe=cls.test_record.with_user(cls.user_employee)

    @mute_logger('flectra.addons.mail.models.mail_mail')
    deftest_fetch_listener(self):
        channel=self.env['mail.channel'].with_user(self.user_employee).init_flectrabot()
        partners=self.env['mail.channel'].channel_fetch_listeners(channel.uuid)
        flectrabot=self.env.ref("base.partner_root")
        flectrabot_in_fetch_listeners=[partnerforpartnerinpartnersifpartner['id']==flectrabot.id]
        self.assertEqual(len(flectrabot_in_fetch_listeners),1,'flectrabotshouldappearonlyonceinchannel_fetch_listeners')

    @mute_logger('flectra.addons.mail.models.mail_mail')
    deftest_flectrabot_ping(self):
        kwargs=self.message_post_default_kwargs.copy()
        kwargs.update({'body':self.flectrabot_ping_body,'partner_ids':[self.flectrabot.id,self.user_admin.partner_id.id]})

        withpatch('random.choice',lambdax:x[0]):
            self.assertNextMessage(
                self.test_record_employe.with_context({'mail_post_autofollow':True}).message_post(**kwargs),
                sender=self.flectrabot,
                answer=False
            )
        #Flectrabotshouldnotbeafollowerbutuser_employeeanduser_adminshould
        follower=self.test_record.message_follower_ids.mapped('partner_id')
        self.assertNotIn(self.flectrabot,follower)
        self.assertIn(self.user_employee.partner_id,follower)
        self.assertIn(self.user_admin.partner_id,follower)

    @mute_logger('flectra.addons.mail.models.mail_mail')
    deftest_onboarding_flow(self):
        kwargs=self.message_post_default_kwargs.copy()
        channel=self.env['mail.channel'].with_user(self.user_employee).init_flectrabot()

        kwargs['body']='tagada😊'
        last_message=self.assertNextMessage(
            channel.message_post(**kwargs),
            sender=self.flectrabot,
            answer=("help",)
        )
        channel.execute_command(command="help")
        self.assertNextMessage(
            last_message, #nomessagewillbepostwithcommandhelp,uselastflectrabotmessageinstead
            sender=self.flectrabot,
            answer=("@FlectraBot",)
        )
        kwargs['body']=''
        kwargs['partner_ids']=[self.env['ir.model.data'].xmlid_to_res_id("base.partner_root")]
        self.assertNextMessage(
            channel.message_post(**kwargs),
            sender=self.flectrabot,
            answer=("attachment",)
        )
        kwargs['body']=''
        attachment=self.env['ir.attachment'].with_user(self.user_employee).create({
            'datas':'bWlncmF0aW9uIHRlc3Q=',
            'name':'picture_of_your_dog.doc',
            'res_model':'mail.compose.message',
        })
        kwargs['attachment_ids']=[attachment.id]
        #Fortheendoftheflow,weonlytestthatthestatechanged,butnottowhich
        #onesinceitdependsontheintalledapps,whichcanaddmoresteps(likelivechat)
        channel.message_post(**kwargs)
        self.assertNotEqual(self.user_employee.flectrabot_state,'onboarding_attachement')

        #Testmiscellaneousmessages
        self.user_employee.flectrabot_state="idle"
        kwargs['partner_ids']=[]
        kwargs['body']="Iloveyou"
        self.assertNextMessage(
            channel.message_post(**kwargs),
            sender=self.flectrabot,
            answer=("toohumanforme",)
        )
        kwargs['body']="Gofuckyourself"
        self.assertNextMessage(
            channel.message_post(**kwargs),
            sender=self.flectrabot,
            answer=("Ihavefeelings",)
        )
        kwargs['body']="helpme"
        self.assertNextMessage(
            channel.message_post(**kwargs),
            sender=self.flectrabot,
            answer=("Ifyouneedhelp",)
        )

    @mute_logger('flectra.addons.mail.models.mail_mail')
    deftest_flectrabot_no_default_answer(self):
        kwargs=self.message_post_default_kwargs.copy()
        kwargs.update({'body':"I'mnottalkingto@flectrabotrightnow",'partner_ids':[]})
        self.assertNextMessage(
            self.test_record_employe.message_post(**kwargs),
            answer=False
        )

    defassertNextMessage(self,message,answer=None,sender=None):
        last_message=self.env['mail.message'].search([('id','=',message.id+1)])
        iflast_message:
            body=last_message.body.replace('<p>','').replace('</p>','')
        else:
            self.assertFalse(answer,"Nolastmessagefoundwhenananswerwasexpect")
        ifanswerisnotNone:
            ifanswerandnotlast_message:
                self.assertTrue(False,"Nolastmessagefound")
            ifisinstance(answer,list):
                self.assertIn(body,answer)
            elifisinstance(answer,tuple):
                foreleminanswer:
                    self.assertIn(elem,body)
            elifnotanswer:
                self.assertFalse(last_message,"Noanswershouldhavebeenpost")
                return
            else:
                self.assertEqual(body,answer)
        ifsender:
            self.assertEqual(sender,last_message.author_id)
        returnlast_message
