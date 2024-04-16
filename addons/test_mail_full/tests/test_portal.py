#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromwerkzeug.urlsimporturl_parse,url_decode

importjson

fromflectraimporthttp
fromflectra.addons.mail.tests.commonimportmail_new_test_user
fromflectra.testsimporttagged,users
fromflectra.tests.commonimportHttpCase


@tagged('portal')
classTestPortal(HttpCase):

    defsetUp(self):
        super(TestPortal,self).setUp()

        self.user_admin=self.env.ref('base.user_admin')
        self.user_employee=mail_new_test_user(
            self.env,
            groups='base.group_user',
            login='employee',
            name='ErnestEmployee',
            signature='--\nErnest',
        )
        self.partner_1,self.partner_2=self.env['res.partner'].create([
            {'name':'ValidLelitre',
             'email':'valid.lelitre@agrolait.com',
             'country_id':self.env.ref('base.be').id,
             'mobile':'0456001122'},
            {'name':'ValidPoilvache',
             'email':'valid.other@gmail.com',
             'country_id':self.env.ref('base.be').id,
             'mobile':'+32456221100'}
        ])

        self.record_portal=self.env['mail.test.portal'].create({
            'partner_id':self.partner_1.id,
            'name':'TestPortalRecord',
        })

        self.record_portal._portal_ensure_token()


@tagged('-at_install','post_install','portal')
classTestPortalControllers(TestPortal):

    deftest_redirect_to_records(self):
        """Testredirectionofportal-enabledrecords"""
        #TestCase0:asanonymous,cannotaccess,redirecttoweb/login
        response=self.url_open('/mail/view?model=%s&res_id=%s'%(
            self.record_portal._name,
            self.record_portal.id),timeout=15)

        path=url_parse(response.url).path
        self.assertEqual(path,'/web/login')

        #TestCase1:asadmin,canaccessrecord
        self.authenticate(self.user_admin.login,self.user_admin.login)
        response=self.url_open('/mail/view?model=%s&res_id=%s'%(
            self.record_portal._name,
            self.record_portal.id),timeout=15)

        self.assertEqual(response.status_code,200)

        fragment=url_parse(response.url).fragment
        params=url_decode(fragment)
        self.assertEqual(params['cids'],'%s'%self.user_admin.company_id.id)
        self.assertEqual(params['id'],'%s'%self.record_portal.id)
        self.assertEqual(params['model'],self.record_portal._name)

    deftest_redirect_to_records_norecord(self):
        """Checkspecificusecaseofmissingmodel,shoulddirectlyredirect
        tologinpage."""
        formodel,res_idin[
                (False,self.record_portal.id),
                ('',self.record_portal.id),
                (self.record_portal._name,False),
                (self.record_portal._name,''),
                (False,False),
                ('wrong.model',self.record_portal.id),
                (self.record_portal._name,-4),
            ]:
            response=self.url_open(
                '/mail/view?model=%s&res_id=%s'%(model,res_id),
                timeout=15
            )
            path=url_parse(response.url).path
            self.assertEqual(
                path,'/web/login',
                'Failedwith%s-%s'%(model,res_id)
            )

    deftest_portal_message_fetch(self):
        """Testretrievingchattermessagesthroughtheportalcontroller"""
        self.authenticate(None,None)
        message_fetch_url='/mail/chatter_fetch'
        payload=json.dumps({
            'jsonrpc':'2.0',
            'method':'call',
            'id':0,
            'params':{
                'res_model':'mail.test.portal',
                'res_id':self.record_portal.id,
                'token':self.record_portal.access_token,
            },
        })

        defget_chatter_message_count():
            res=self.url_open(
                url=message_fetch_url,
                data=payload,
                headers={'Content-Type':'application/json'}
            )
            returnres.json().get('result',{}).get('message_count',0)

        self.assertEqual(get_chatter_message_count(),0)

        for_inrange(8):
            self.record_portal.message_post(
                body='Test',
                author_id=self.partner_1.id,
                message_type='comment',
                subtype_id=self.env.ref('mail.mt_comment').id,
            )

        self.assertEqual(get_chatter_message_count(),8)

        #Emptythebodyofafewmessages
        foriin(2,5,6):
            self.record_portal.message_ids[i].body=""

        #Emptymessagesshouldbeignored
        self.assertEqual(get_chatter_message_count(),5)

    deftest_portal_share_comment(self):
        """Testpostingthroughportalcontrollerallowingtouseahashto
        postwihtoutaccessrights."""
        self.authenticate(None,None)
        post_url="/mail/chatter_post"
        post_data={
            'csrf_token':http.WebRequest.csrf_token(self),
            'hash':self.record_portal._sign_token(self.partner_2.id),
            'message':'Test',
            'pid':self.partner_2.id,
            'redirect':'/',
            'res_model':self.record_portal._name,
            'res_id':self.record_portal.id,
            'token':self.record_portal.access_token,
        }

        #testasnotlogged
        self.url_open(url=post_url,data=post_data)
        message=self.record_portal.message_ids[0]

        self.assertIn('Test',message.body)
        self.assertEqual(message.author_id,self.partner_2)


@tagged('portal')
classTestPortalMixin(TestPortal):

    @users('employee')
    deftest_portal_mixin(self):
        """Testinternalsofportalmixin"""
        customer=self.partner_1.with_env(self.env)
        record_portal=self.env['mail.test.portal'].create({
            'partner_id':customer.id,
            'name':'TestPortalRecord',
        })

        self.assertFalse(record_portal.access_token)
        self.assertEqual(record_portal.access_url,'/my/test_portal/%s'%record_portal.id)

        record_portal._portal_ensure_token()
        self.assertTrue(record_portal.access_token)
