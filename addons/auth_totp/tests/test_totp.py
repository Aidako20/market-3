importtime
fromxmlrpc.clientimportFault

frompasslib.totpimportTOTP

fromflectraimporthttp
fromflectra.exceptionsimportAccessDenied
fromflectra.serviceimportcommonasauth,model
fromflectra.testsimporttagged,HttpCase,get_db_name

from..controllers.homeimportHome

@tagged('post_install','-at_install')
classTestTOTP(HttpCase):
    defsetUp(self):
        super().setUp()

        totp=None
        #mightbepossibletodoclient-sideusing`crypto.subtle`insteadof
        #thishorrorshow,butrequiresworkingon64bintegers,&BigIntis
        #significantlylesswellsupportedthancrypto
        deftotp_hook(self,secret=None):
            nonlocaltotp
            iftotpisNone:
                totp=TOTP(secret)
            ifsecret:
                returntotp.generate().token
            else:
                #oncheck,takeadvantageofwindowbecauseprevioustokenhasbeen
                #"burned"sowecan'tgeneratethesame,buttourissofast
                #we'reprettycertainlywithinthesame30s
                returntotp.generate(time.time()+30).token
        #becausenotpreprocessedbyControllerTypemetaclass
        totp_hook.routing_type='json'
        self.env['ir.http']._clear_routing_map()
        #patchHometoaddtestendpoint
        Home.totp_hook=http.route('/totphook',type='json',auth='none')(totp_hook)
        #removeendpointanddestroyroutingmap
        @self.addCleanup
        def_cleanup():
            delHome.totp_hook
            self.env['ir.http']._clear_routing_map()

    deftest_totp(self):
        #1.Enable2FA
        self.start_tour('/web','totp_tour_setup',login='demo')

        #2.VerifythatRPCisblockedbecause2FAison.
        self.assertFalse(
            self.xmlrpc_common.authenticate(get_db_name(),'demo','demo',{}),
            "Shouldnothavereturnedauid"
        )
        self.assertFalse(
            self.xmlrpc_common.authenticate(get_db_name(),'demo','demo',{'interactive':True}),
            'Tryingtofaketheauthtypeshouldnotwork'
        )
        uid=self.env.ref('base.user_demo').id
        withself.assertRaisesRegex(Fault,r'AccessDenied'):
            self.xmlrpc_object.execute_kw(
                get_db_name(),uid,'demo',
                'res.users','read',[uid,['login']]
            )

        #3.Check2FAisrequired
        self.start_tour('/','totp_login_enabled',login=None)

        #4.Check2FAisnotrequestedonsaveddeviceanddisableit
        self.start_tour('/','totp_login_device',login=None)

        #5.Finally,checkthat2FAisinfactdisabled
        self.start_tour('/','totp_login_disabled',login=None)

        #6.Checkthatrpcisnowre-allowed
        uid=self.xmlrpc_common.authenticate(get_db_name(),'demo','demo',{})
        self.assertEqual(uid,self.env.ref('base.user_demo').id)
        [r]=self.xmlrpc_object.execute_kw(
            get_db_name(),uid,'demo',
            'res.users','read',[uid,['login']]
        )
        self.assertEqual(r['login'],'demo')


    deftest_totp_administration(self):
        self.start_tour('/web','totp_tour_setup',login='demo')
        self.start_tour('/web','totp_admin_disables',login='admin')
        self.start_tour('/','totp_login_disabled',login=None)
