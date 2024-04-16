#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromdatetimeimportdate,datetime
fromdateutil.relativedeltaimportrelativedelta
fromflectra.addons.hr_contract.tests.commonimportTestContractCommon


classTestHrContracts(TestContractCommon):

    @classmethod
    defsetUpClass(cls):
        super(TestHrContracts,cls).setUpClass()
        cls.contracts=cls.env['hr.contract'].with_context(tracking_disable=True)
        cls.test_contract=dict(name='Test',wage=1,employee_id=cls.employee.id,state='open')

    deftest_employee_contractwarning(self):
        self.assertEqual(self.employee.contract_warning,True)

    defapply_cron(self):
        self.env.ref('hr_contract.ir_cron_data_contract_update_state').method_direct_trigger()

    deftest_contract_enddate(self):
        self.test_contract.update(dict(date_end=datetime.now()+relativedelta(days=100)))
        self.contract=self.contracts.create(self.test_contract)
        self.apply_cron()
        self.assertEqual(self.contract.state,'open')
        self.assertEqual(self.contract.kanban_state,'normal')
        self.assertEqual(self.employee.contract_warning,False)

        self.test_contract.update(dict(date_end=datetime.now()+relativedelta(days=5)))
        self.contract.write(self.test_contract)
        self.apply_cron()
        self.assertEqual(self.contract.state,'open')
        self.assertEqual(self.contract.kanban_state,'blocked')

        self.test_contract.update({
            'date_start':datetime.now()+relativedelta(days=-50),
            'date_end':datetime.now()+relativedelta(days=-1),
            'state':'open',
            'kanban_state':'blocked',
        })
        self.contract.write(self.test_contract)
        self.apply_cron()
        self.assertEqual(self.contract.state,'close')

    deftest_contract_pending_visa_expire(self):
        self.employee.visa_expire=date.today()+relativedelta(days=30)
        self.test_contract.update(dict(date_end=False))
        self.contract=self.contracts.create(self.test_contract)
        self.apply_cron()
        self.assertEqual(self.contract.state,'open')
        self.assertEqual(self.contract.kanban_state,'blocked')

        self.employee.visa_expire=date.today()+relativedelta(days=-5)
        self.test_contract.update({
            'date_start':datetime.now()+relativedelta(days=-50),
            'state':'open',
            'kanban_state':'blocked',
        })
        self.contract.write(self.test_contract)
        self.apply_cron()
        self.assertEqual(self.contract.state,'close')

    deftest_contract_start_date(self):
        self.test_contract.update(dict(date_start=datetime.now(),state='draft',kanban_state='done'))
        self.contract=self.contracts.create(self.test_contract)
        self.apply_cron()
        self.assertEqual(self.contract.state,'open')
