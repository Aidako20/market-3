#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.fieldsimportDatetime,Date
fromflectra.addons.hr_contract.tests.commonimportTestContractCommon


classTestContractCalendars(TestContractCommon):

    @classmethod
    defsetUpClass(cls):
        super(TestContractCalendars,cls).setUpClass()
        cls.calendar_richard=cls.env['resource.calendar'].create({'name':'CalendarofRichard'})
        cls.employee.resource_calendar_id=cls.calendar_richard

        cls.calendar_35h=cls.env['resource.calendar'].create({'name':'35hcalendar'})
        cls.calendar_35h._onchange_hours_per_day() #updatehours/day

        cls.contract_cdd=cls.env['hr.contract'].create({
            'date_end':Date.to_date('2015-11-15'),
            'date_start':Date.to_date('2015-01-01'),
            'name':'FirstCDDContractforRichard',
            'resource_calendar_id':cls.calendar_35h.id,
            'wage':5000.0,
            'employee_id':cls.employee.id,
            'state':'close',
        })

    deftest_contract_state_incoming_to_open(self):
        #Employee'scalendarshouldchange
        self.assertEqual(self.employee.resource_calendar_id,self.calendar_richard)
        self.contract_cdd.state='open'
        self.assertEqual(self.employee.resource_calendar_id,self.contract_cdd.resource_calendar_id,"Theemployeeshouldhavethecalendarofitscontract.")

    deftest_contract_transfer_leaves(self):

        defcreate_calendar_leave(start,end,resource=None):
            returnself.env['resource.calendar.leaves'].create({
                'name':'leavename',
                'date_from':start,
                'date_to':end,
                'resource_id':resource.idifresourceelseNone,
                'calendar_id':self.employee.resource_calendar_id.id,
                'time_type':'leave',
            })

        start=Datetime.to_datetime('2015-11-1707:00:00')
        end=Datetime.to_datetime('2015-11-2018:00:00')
        leave1=create_calendar_leave(start,end,resource=self.employee.resource_id)

        start=Datetime.to_datetime('2015-11-2507:00:00')
        end=Datetime.to_datetime('2015-11-2818:00:00')
        leave2=create_calendar_leave(start,end,resource=self.employee.resource_id)

        #globalleave
        start=Datetime.to_datetime('2015-11-2507:00:00')
        end=Datetime.to_datetime('2015-11-2818:00:00')
        leave3=create_calendar_leave(start,end)

        self.calendar_richard.transfer_leaves_to(self.calendar_35h,resources=self.employee.resource_id,from_date=Date.to_date('2015-11-21'))

        self.assertEqual(leave1.calendar_id,self.calendar_richard,"ItshouldstayinRichard'scalendar")
        self.assertEqual(leave3.calendar_id,self.calendar_richard,"Globalleaveshouldstayinoriginalcalendar")
        self.assertEqual(leave2.calendar_id,self.calendar_35h,"Itshouldbetransferedtotheothercalendar")

        #Transfergloballeaves
        self.calendar_richard.transfer_leaves_to(self.calendar_35h,resources=None,from_date=Date.to_date('2015-11-21'))

        self.assertEqual(leave3.calendar_id,self.calendar_35h,"Globalleaveshouldbetransfered")