#-*-coding:utf-8-*-

fromflectra.testsimportcommon,tagged
fromflectra.tools.miscimportmute_logger,ustr


@tagged('-at_install','post_install')
classTestConfirmUnsubscribe(common.HttpCase):
    defsetUp(self):
        super(TestConfirmUnsubscribe,self).setUp()
        self.partner=self.env['res.partner'].create({
            'name':'Bob',
            'email':'bob@bob.bob'
        })
        self.mailing_list=self.env['mail.channel'].create({
            'name':'TestMailingList',
            'public':'public',
        })
        self.token=self.mailing_list._generate_action_token(self.partner.id,action='unsubscribe')

    deftest_not_subscribed(self):
        """Testwarningworks"""
        self._unsubscribe_check("Theaddress%sisalreadyunsubscribed"%self.partner.email)

    @mute_logger('flectra.addons.website.models.ir_ui_view')
    deftest_not_subscribed_no_template(self):
        """Testwarningworksondbwithouttemplate(codeupdatew/omoduleupdate)"""
        self.env.ref('website_mail_channel.not_subscribed').unlink()
        self.assertEqual(
            self.env['ir.model.data'].search_count([
            ('module','=','website_mail_channel'),
            ('name','=','not_subscribed'),
        ]),0,'XIDfortemplateshouldhavebeendeleted')

        self._unsubscribe_check("Theaddress%sisalreadyunsubscribedorwasneversubscribedtoanymailinglist"%self.partner.email)

    deftest_wrong_token(self):
        self.mailing_list.sudo().write({
            'channel_partner_ids':[(4,self.partner.id,False)]
        })
        self.token='XXX'

        self._unsubscribe_check("Invalidorexpiredconfirmationlink.")

    deftest_successful_unsubscribe(self):
        self.mailing_list.sudo().write({
            'channel_partner_ids':[(4,self.partner.id,False)]
        })

        self._unsubscribe_check("Youhavebeencorrectlyunsubscribed")

    def_unsubscribe_check(self,text):
        url="/groups/unsubscribe/{}/{}/{}".format(
            self.mailing_list.id,self.partner.id,
            self.token
        )
        r=self.url_open(url)
        body=ustr(r.content)
        #normalizespacetomakematchingsimpler
        self.assertIn(text,u''.join(body.split()))
