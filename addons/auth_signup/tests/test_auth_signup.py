#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromunittest.mockimportpatch

importflectra
fromflectra.testsimportHttpCase
fromflectraimporthttp
fromflectra.exceptionsimportAccessError

classTestAuthSignupFlow(HttpCase):

    defsetUp(self):
        super(TestAuthSignupFlow,self).setUp()
        res_config=self.env['res.config.settings']
        self.default_values=res_config.default_get(list(res_config.fields_get()))

    def_activate_free_signup(self):
        self.default_values.update({'auth_signup_uninvited':'b2c'})

    def_get_free_signup_url(self):
        return'/web/signup'

    deftest_confirmation_mail_free_signup(self):
        """
        Checkifanewuserisinformedbyemailwhenheisregistered
        """

        #Activatefreesignup
        self._activate_free_signup()

        #Getcsrf_token
        self.authenticate(None,None)
        csrf_token=http.WebRequest.csrf_token(self)

        #Valuesfromloginform
        name='toto'
        payload={
            'login':'toto@example.com',
            'name':name,
            'password':'mypassword',
            'confirm_password':'mypassword',
            'csrf_token':csrf_token,
        }

        #Overrideunlinktonotdeletetheemailifthesendworks.
        withpatch.object(flectra.addons.mail.models.mail_mail.MailMail,'unlink',lambdaself:None):
            #Callthecontroller
            url_free_signup=self._get_free_signup_url()
            self.url_open(url_free_signup,data=payload)
            #Checkifanemailissenttothenewuser
            new_user=self.env['res.users'].search([('name','=',name)])
            self.assertTrue(new_user)
            mail=self.env['mail.message'].search([('message_type','=','email'),('model','=','res.users'),('res_id','=',new_user.id)],limit=1)
            self.assertTrue(mail,"Thenewusermustbeinformedofhisregistration")

    deftest_compute_signup_url(self):
        user=self.env.ref('base.user_demo')
        user.groups_id-=self.env.ref('base.group_partner_manager')

        partner=self.env.ref('base.partner_demo_portal')
        partner.signup_prepare()

        withself.assertRaises(AccessError):
            partner.with_user(user.id).signup_url
