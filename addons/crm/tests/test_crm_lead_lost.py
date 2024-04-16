#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.addons.crm.testsimportcommonascrm_common
fromflectra.exceptionsimportAccessError
fromflectra.tests.commonimporttagged,users


@tagged('lead_manage')
classTestLeadConvert(crm_common.TestCrmCommon):

    @classmethod
    defsetUpClass(cls):
        super(TestLeadConvert,cls).setUpClass()
        cls.lost_reason=cls.env['crm.lost.reason'].create({
            'name':'TestReason'
        })

    @users('user_sales_salesman')
    deftest_lead_lost(self):
        self.lead_1.with_user(self.user_sales_manager).write({
            'user_id':self.user_sales_salesman.id,
            'probability':32,
        })

        lead=self.lead_1.with_user(self.env.user)
        self.assertEqual(lead.probability,32)

        lost_wizard=self.env['crm.lead.lost'].with_context({
            'active_ids':lead.ids,
        }).create({
            'lost_reason_id':self.lost_reason.id
        })

        lost_wizard.action_lost_reason_apply()

        self.assertEqual(lead.probability,0)
        self.assertEqual(lead.automated_probability,0)
        self.assertFalse(lead.active)
        self.assertEqual(lead.lost_reason,self.lost_reason) #TDEFIXME:shouldbecalledlost_reason_idnondidjou

    @users('user_sales_salesman')
    deftest_lead_lost_crm_rights(self):
        lead=self.lead_1.with_user(self.env.user)

        #nicetrylittlesalesmanbutonlymanagerscancreatelostreasontoavoidbloatingtheDB
        withself.assertRaises(AccessError):
            lost_reason=self.env['crm.lost.reason'].create({
                'name':'TestReason'
            })

        withself.with_user('user_sales_manager'):
            lost_reason=self.env['crm.lost.reason'].create({
                'name':'TestReason'
            })

        lost_wizard=self.env['crm.lead.lost'].with_context({
            'active_ids':lead.ids
        }).create({
            'lost_reason_id':lost_reason.id
        })

        #nicetrylittlesalesman,youcannotinvokeawizardtoupdateotherpeopleleads
        withself.assertRaises(AccessError):
            lost_wizard.action_lost_reason_apply()
