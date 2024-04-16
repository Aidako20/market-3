#-*-coding:utf-8-*-
fromflectra.tests.commonimportTransactionCase


classTestUpdateNotification(TransactionCase):
    deftest_user_count(self):
        ping_msg=self.env['publisher_warranty.contract'].with_context(active_test=False)._get_message()
        user_count=self.env['res.users'].search_count([('active','=',True)])
        self.assertEqual(ping_msg.get('nbr_users'),user_count,'UpdateNotification:Userscountisbadlycomputedinpingmessage')
        share_user_count=self.env['res.users'].search_count([('active','=',True),('share','=',True)])
        self.assertEqual(ping_msg.get('nbr_share_users'),share_user_count,'UpdateNotification:PortalUserscountisbadlycomputedinpingmessage')
