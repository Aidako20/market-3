#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromdatetimeimportdatetime,timedelta,time
frompytzimporttimezone,utc

fromflectraimportfields
fromflectra.addons.mrp.tests.commonimportTestMrpCommon


classTestOee(TestMrpCommon):
    defcreate_productivity_line(self,loss_reason,date_start=False,date_end=False):
        returnself.env['mrp.workcenter.productivity'].create({
            'workcenter_id':self.workcenter_1.id,
            'date_start':date_start,
            'date_end':date_end,
            'loss_id':loss_reason.id,
            'description':loss_reason.name
        })

    deftest_wrokcenter_oee(self):
        """ Testcaseworkcenteroee."""
        day=datetime.date(datetime.today())
        #Makethetestworktheweekend.Itwillfailsduetoworkcenterworkinghours.
        ifday.weekday()in(5,6):
            day-=timedelta(days=2)

        tz=timezone(self.workcenter_1.resource_calendar_id.tz)

        deftime_to_string_utc_datetime(time):
            returnfields.Datetime.to_string(
                tz.localize(datetime.combine(day,time)).astimezone(utc)
            )

        start_time=time_to_string_utc_datetime(time(10,43,22))
        end_time=time_to_string_utc_datetime(time(10,56,22))
        #Productivetimeduration(13min)
        self.create_productivity_line(self.env.ref('mrp.block_reason7'),start_time,end_time)

        #MaterialAvailabilitytimeduration(1.52min)
        #Checkworkingstateisblockedornot.
        start_time=time_to_string_utc_datetime(time(10,47,8))
        workcenter_productivity_1=self.create_productivity_line(self.env.ref('mrp.block_reason0'),start_time)
        self.assertEqual(self.workcenter_1.working_state,'blocked',"Wrongworkingstateofworkcenter.")

        #Checkworkingstateisnormalornot.
        end_time=time_to_string_utc_datetime(time(10,48,39))
        workcenter_productivity_1.write({'date_end':end_time})
        self.assertEqual(self.workcenter_1.working_state,'normal',"Wrongworkingstateofworkcenter.")

        #ProcessDefecttimeduration(1.33min)
        start_time=time_to_string_utc_datetime(time(10,48,38))
        end_time=time_to_string_utc_datetime(time(10,49,58))
        self.create_productivity_line(self.env.ref('mrp.block_reason5'),start_time,end_time)
        #ReducedSpeedtimeduration(3.0min)
        start_time=time_to_string_utc_datetime(time(10,50,22))
        end_time=time_to_string_utc_datetime(time(10,53,22))
        self.create_productivity_line(self.env.ref('mrp.block_reason4'),start_time,end_time)

        #Blocktime:(ProcessDefact(1.33min)+ReducedSpeed(3.0min)+MaterialAvailability(1.52min))=5.85min
        blocked_time_in_hour=round(((1.33+3.0+1.52)/60.0),2)
        #Productivetime:Productivetimeduration(13min)
        productive_time_in_hour=round((13.0/60.0),2)

        #Checkblockedtimeandproductivetime
        self.assertEqual(self.workcenter_1.blocked_time,blocked_time_in_hour,"Wrongblocktimeonworkcenter.")
        self.assertEqual(self.workcenter_1.productive_time,productive_time_in_hour,"Wrongproductivetimeonworkcenter.")

        #Checkoverallequipmenteffectiveness
        computed_oee=round(((productive_time_in_hour*100.0)/(productive_time_in_hour+blocked_time_in_hour)),2)
        self.assertEqual(self.workcenter_1.oee,computed_oee,"Wrongoeeonworkcenter.")
