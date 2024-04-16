#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importflectra.tests


@flectra.tests.tagged('post_install','-at_install')
classTestRoutes(flectra.tests.HttpCase):

    deftest_01_web_session_destroy(self):
        base_url=self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        self.authenticate('demo','demo')
        res=self.opener.post(url=base_url+'/web/session/destroy',json={})
        self.assertEqual(res.status_code,200)
