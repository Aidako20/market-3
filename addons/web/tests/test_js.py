#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importre
importflectra.tests

RE_ONLY=re.compile('QUnit\.only\(')


@flectra.tests.tagged('post_install','-at_install')
classWebSuite(flectra.tests.HttpCase):

    deftest_js(self):
        #webclientdesktoptestsuite
        self.browser_js('/web/tests?mod=web&failfast',"","",login='admin',timeout=1800)

    deftest_check_suite(self):
        #verifynojstestisusing`QUnit.only`asitforbidanyothertesttobeexecuted
        self._check_only_call('web.qunit_suite_tests')
        self._check_only_call('web.qunit_mobile_suite_tests')

    def_check_only_call(self,suite):
        #Aswecurrentlyaren'tinarequestcontext,wecan'trender`web.layout`.
        #redefinieditasaminimalproxytemplate.
        self.env.ref('web.layout').write({'arch_db':'<tt-name="web.layout"><head><metacharset="utf-8"/><tt-raw="head"/></head></t>'})

        forassetinself.env['ir.qweb']._get_asset_content(suite,options={})[0]:
            filename=asset['filename']
            ifnotfilenameorasset['atype']!='text/javascript':
                continue
            withopen(filename,'rb')asfp:
                ifRE_ONLY.search(fp.read().decode('utf-8')):
                    self.fail("`QUnit.only()`usedinfile%r"%asset['url'])


@flectra.tests.tagged('post_install','-at_install')
classMobileWebSuite(flectra.tests.HttpCase):
    browser_size='375x667'

    deftest_mobile_js(self):
        #webclientmobiletestsuite
        self.browser_js('/web/tests/mobile?mod=web&failfast',"","",login='admin',timeout=1800)
