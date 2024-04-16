#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromdatetimeimportdatetime,date
fromflectra.exceptionsimportValidationError
fromflectra.addons.hr_contract.tests.commonimportTestContractCommon


classTestHrContracts(TestContractCommon):

    @classmethod
    defsetUpClass(cls):
        super(TestHrContracts,cls).setUpClass()
        cls.contracts=cls.env['hr.contract'].with_context(tracking_disable=True)

    defcreate_contract(self,state,kanban_state,start,end=None):
        returnself.env['hr.contract'].create({
            'name':'Contract',
            'employee_id':self.employee.id,
            'state':state,
            'kanban_state':kanban_state,
            'wage':1,
            'date_start':start,
            'date_end':end,
        })

    deftest_incoming_overlapping_contract(self):
        start=datetime.strptime('2015-11-01','%Y-%m-%d').date()
        end=datetime.strptime('2015-11-30','%Y-%m-%d').date()
        self.create_contract('open','normal',start,end)

        #Incomingcontract
        withself.assertRaises(ValidationError,msg="Itshouldnotcreatetwocontractinstateopenorincoming"):
            start=datetime.strptime('2015-11-15','%Y-%m-%d').date()
            end=datetime.strptime('2015-12-30','%Y-%m-%d').date()
            self.create_contract('draft','done',start,end)

    deftest_pending_overlapping_contract(self):
        start=datetime.strptime('2015-11-01','%Y-%m-%d').date()
        end=datetime.strptime('2015-11-30','%Y-%m-%d').date()
        self.create_contract('open','normal',start,end)

        #Pendingcontract
        withself.assertRaises(ValidationError,msg="Itshouldnotcreatetwocontractinstateopenorpending"):
            start=datetime.strptime('2015-11-15','%Y-%m-%d').date()
            end=datetime.strptime('2015-12-30','%Y-%m-%d').date()
            self.create_contract('open','blocked',start,end)

        #Draftcontract->shouldnotraise
        start=datetime.strptime('2015-11-15','%Y-%m-%d').date()
        end=datetime.strptime('2015-12-30','%Y-%m-%d').date()
        self.create_contract('draft','normal',start,end)

    deftest_draft_overlapping_contract(self):
        start=datetime.strptime('2015-11-01','%Y-%m-%d').date()
        end=datetime.strptime('2015-11-30','%Y-%m-%d').date()
        self.create_contract('open','normal',start,end)

        #Draftcontract->shouldnotraiseevenifoverlapping
        start=datetime.strptime('2015-11-15','%Y-%m-%d').date()
        end=datetime.strptime('2015-12-30','%Y-%m-%d').date()
        self.create_contract('draft','normal',start,end)

    deftest_overlapping_contract_no_end(self):

        #Noenddate
        self.create_contract('open','normal',datetime.strptime('2015-11-01','%Y-%m-%d').date())

        withself.assertRaises(ValidationError):
            start=datetime.strptime('2015-11-15','%Y-%m-%d').date()
            end=datetime.strptime('2015-12-30','%Y-%m-%d').date()
            self.create_contract('draft','done',start,end)

    deftest_overlapping_contract_no_end2(self):

        start=datetime.strptime('2015-11-01','%Y-%m-%d').date()
        end=datetime.strptime('2015-12-30','%Y-%m-%d').date()
        self.create_contract('open','normal',start,end)

        withself.assertRaises(ValidationError):
            #Noend
            self.create_contract('draft','done',datetime.strptime('2015-01-01','%Y-%m-%d').date())

    deftest_set_employee_contract_create(self):
        contract=self.create_contract('open','normal',date(2018,1,1),date(2018,1,2))
        self.assertEqual(self.employee.contract_id,contract)

    deftest_set_employee_contract_write(self):
        contract=self.create_contract('draft','normal',date(2018,1,1),date(2018,1,2))
        contract.state='open'
        self.assertEqual(self.employee.contract_id,contract)
