importtime

frompasslib.totpimportTOTP

fromflectraimporthttp
fromflectra.testsimporttagged,HttpCase
fromflectra.addons.auth_totp.controllers.homeimportHome


@tagged('post_install','-at_install')
classTestTOTPortal(HttpCase):
    """
    LargelyreplicatesTestTOTP
    """
    deftest_totp(self):
        totp=None
        #testendpointasdoingtotpontheclientsideisnotreallyanoption
        #(needssha1andhmac+BEpackingof64bintegers)
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
        #patchHometoaddtestendpoint
        Home.totp_hook=http.route('/totphook',type='json',auth='none')(totp_hook)
        self.env['ir.http']._clear_routing_map()
        #removeendpointanddestroyroutingmap
        @self.addCleanup
        def_cleanup():
            delHome.totp_hook
            self.env['ir.http']._clear_routing_map()

        self.start_tour('/my/security','totportal_tour_setup',login='portal')
        #alsodisablestotpotherwisewecan'tre-login
        self.start_tour('/','totportal_login_enabled',login=None)
        self.start_tour('/','totportal_login_disabled',login=None)
