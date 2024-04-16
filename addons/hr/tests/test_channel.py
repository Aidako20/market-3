#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.addons.hr.tests.commonimportTestHrCommon


classTestChannel(TestHrCommon):

    defsetUp(self):
        super(TestChannel,self).setUp()

        self.channel=self.env['mail.channel'].create({'name':'Test'})

        emp0=self.env['hr.employee'].create({
            'user_id':self.res_users_hr_officer.id,
        })
        self.department=self.env['hr.department'].create({
            'name':'TestDepartment',
            'member_ids':[(4,emp0.id)],
        })

    deftest_auto_subscribe_department(self):
        self.assertEqual(self.channel.channel_partner_ids,self.env['res.partner'])

        self.channel.write({
            'subscription_department_ids':[(4,self.department.id)]
        })

        self.assertEqual(self.channel.channel_partner_ids,self.department.mapped('member_ids.user_id.partner_id'))
