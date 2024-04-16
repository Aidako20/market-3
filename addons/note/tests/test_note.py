#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.addons.base.tests.commonimportTransactionCaseWithUserDemo


classTestNote(TransactionCaseWithUserDemo):

    deftest_bug_lp_1156215(self):
        """ensureanyuserscancreatenewusers"""
        demo_user=self.user_demo
        group_erp=self.env.ref('base.group_erp_manager')

        demo_user.write({
            'groups_id':[(4,group_erp.id)],
        })

        #mustnotfail
        demo_user.create({
            'name':'testbuglp:1156215',
            'login':'lp_1156215',
        })
