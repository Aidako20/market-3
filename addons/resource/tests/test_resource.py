#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromdatetimeimportdate,datetime
fromfreezegunimportfreeze_time
frompytzimporttimezone,utc

fromflectraimportfields
fromflectra.exceptionsimportValidationError
fromflectra.addons.resource.models.resourceimportIntervals
fromflectra.addons.resource.tests.commonimportTestResourceCommon
fromflectra.tests.commonimportTransactionCase


defdatetime_tz(year,month,day,hour=0,minute=0,second=0,microsecond=0,tzinfo=None):
    """Returna`datetime`objectwithagiventimezone(ifgiven)."""
    dt=datetime(year,month,day,hour,minute,second,microsecond)
    returntimezone(tzinfo).localize(dt)iftzinfoelsedt


defdatetime_str(year,month,day,hour=0,minute=0,second=0,microsecond=0,tzinfo=None):
    """Returnafields.Datetimevaluewiththegiventimezone."""
    dt=datetime(year,month,day,hour,minute,second,microsecond)
    iftzinfo:
        dt=timezone(tzinfo).localize(dt).astimezone(utc)
    returnfields.Datetime.to_string(dt)


classTestIntervals(TransactionCase):

    defints(self,pairs):
        recs=self.env['base']
        return[(a,b,recs)fora,binpairs]

    deftest_union(self):
        defcheck(a,b):
            a,b=self.ints(a),self.ints(b)
            self.assertEqual(list(Intervals(a)),b)

        check([(1,2),(3,4)],[(1,2),(3,4)])
        check([(1,2),(2,4)],[(1,4)])
        check([(1,3),(2,4)],[(1,4)])
        check([(1,4),(2,3)],[(1,4)])
        check([(3,4),(1,2)],[(1,2),(3,4)])
        check([(2,4),(1,2)],[(1,4)])
        check([(2,4),(1,3)],[(1,4)])
        check([(2,3),(1,4)],[(1,4)])

    deftest_intersection(self):
        defcheck(a,b,c):
            a,b,c=self.ints(a),self.ints(b),self.ints(c)
            self.assertEqual(list(Intervals(a)&Intervals(b)),c)

        check([(10,20)],[(5,8)],[])
        check([(10,20)],[(5,10)],[])
        check([(10,20)],[(5,15)],[(10,15)])
        check([(10,20)],[(5,20)],[(10,20)])
        check([(10,20)],[(5,25)],[(10,20)])
        check([(10,20)],[(10,15)],[(10,15)])
        check([(10,20)],[(10,20)],[(10,20)])
        check([(10,20)],[(10,25)],[(10,20)])
        check([(10,20)],[(15,18)],[(15,18)])
        check([(10,20)],[(15,20)],[(15,20)])
        check([(10,20)],[(15,25)],[(15,20)])
        check([(10,20)],[(20,25)],[])
        check(
            [(0,5),(10,15),(20,25),(30,35)],
            [(6,7),(9,12),(13,17),(22,23),(24,40)],
            [(10,12),(13,15),(22,23),(24,25),(30,35)],
        )

    deftest_difference(self):
        defcheck(a,b,c):
            a,b,c=self.ints(a),self.ints(b),self.ints(c)
            self.assertEqual(list(Intervals(a)-Intervals(b)),c)

        check([(10,20)],[(5,8)],[(10,20)])
        check([(10,20)],[(5,10)],[(10,20)])
        check([(10,20)],[(5,15)],[(15,20)])
        check([(10,20)],[(5,20)],[])
        check([(10,20)],[(5,25)],[])
        check([(10,20)],[(10,15)],[(15,20)])
        check([(10,20)],[(10,20)],[])
        check([(10,20)],[(10,25)],[])
        check([(10,20)],[(15,18)],[(10,15),(18,20)])
        check([(10,20)],[(15,20)],[(10,15)])
        check([(10,20)],[(15,25)],[(10,15)])
        check([(10,20)],[(20,25)],[(10,20)])
        check(
            [(0,5),(10,15),(20,25),(30,35)],
            [(6,7),(9,12),(13,17),(22,23),(24,40)],
            [(0,5),(12,13),(20,22),(23,24)],
        )


classTestErrors(TestResourceCommon):
    defsetUp(self):
        super(TestErrors,self).setUp()

    deftest_create_negative_leave(self):
        #from>to
        withself.assertRaises(ValidationError):
            self.env['resource.calendar.leaves'].create({
                'name':'errorcannotreturninthepast',
                'resource_id':False,
                'calendar_id':self.calendar_jean.id,
                'date_from':datetime_str(2018,4,3,20,0,0,tzinfo=self.jean.tz),
                'date_to':datetime_str(2018,4,3,0,0,0,tzinfo=self.jean.tz),
            })

        withself.assertRaises(ValidationError):
            self.env['resource.calendar.leaves'].create({
                'name':'errorcausedbytimezones',
                'resource_id':False,
                'calendar_id':self.calendar_jean.id,
                'date_from':datetime_str(2018,4,3,10,0,0,tzinfo='UTC'),
                'date_to':datetime_str(2018,4,3,12,0,0,tzinfo='Etc/GMT-6')
            })


classTestCalendar(TestResourceCommon):
    defsetUp(self):
        super(TestCalendar,self).setUp()

    deftest_get_work_hours_count(self):
        self.env['resource.calendar.leaves'].create({
            'name':'GlobalLeave',
            'resource_id':False,
            'calendar_id':self.calendar_jean.id,
            'date_from':datetime_str(2018,4,3,0,0,0,tzinfo=self.jean.tz),
            'date_to':datetime_str(2018,4,3,23,59,59,tzinfo=self.jean.tz),
        })

        self.env['resource.calendar.leaves'].create({
            'name':'leaveforJean',
            'calendar_id':self.calendar_jean.id,
            'resource_id':self.jean.resource_id.id,
            'date_from':datetime_str(2018,4,5,0,0,0,tzinfo=self.jean.tz),
            'date_to':datetime_str(2018,4,5,23,59,59,tzinfo=self.jean.tz),
        })

        hours=self.calendar_jean.get_work_hours_count(
            datetime_tz(2018,4,2,0,0,0,tzinfo=self.jean.tz),
            datetime_tz(2018,4,6,23,59,59,tzinfo=self.jean.tz),
        )
        self.assertEqual(hours,32)

        hours=self.calendar_jean.get_work_hours_count(
            datetime_tz(2018,4,2,0,0,0,tzinfo=self.jean.tz),
            datetime_tz(2018,4,6,23,59,59,tzinfo=self.jean.tz),
            compute_leaves=False,
        )
        self.assertEqual(hours,40)

        #leaveofsize0
        self.env['resource.calendar.leaves'].create({
            'name':'zero_length',
            'calendar_id':self.calendar_patel.id,
            'resource_id':False,
            'date_from':datetime_str(2018,4,3,0,0,0,tzinfo=self.patel.tz),
            'date_to':datetime_str(2018,4,3,0,0,0,tzinfo=self.patel.tz),
        })

        hours=self.calendar_patel.get_work_hours_count(
            datetime_tz(2018,4,2,0,0,0,tzinfo=self.patel.tz),
            datetime_tz(2018,4,6,23,59,59,tzinfo=self.patel.tz),
        )
        self.assertEqual(hours,35)

        #leaveofmediumsize
        leave=self.env['resource.calendar.leaves'].create({
            'name':'zero_length',
            'calendar_id':self.calendar_patel.id,
            'resource_id':False,
            'date_from':datetime_str(2018,4,3,9,0,0,tzinfo=self.patel.tz),
            'date_to':datetime_str(2018,4,3,12,0,0,tzinfo=self.patel.tz),
        })

        hours=self.calendar_patel.get_work_hours_count(
            datetime_tz(2018,4,2,0,0,0,tzinfo=self.patel.tz),
            datetime_tz(2018,4,6,23,59,59,tzinfo=self.patel.tz),
        )
        self.assertEqual(hours,32)

        leave.unlink()

        #leaveofverysmallsize
        leave=self.env['resource.calendar.leaves'].create({
            'name':'zero_length',
            'calendar_id':self.calendar_patel.id,
            'resource_id':False,
            'date_from':datetime_str(2018,4,3,0,0,0,tzinfo=self.patel.tz),
            'date_to':datetime_str(2018,4,3,0,0,10,tzinfo=self.patel.tz),
        })

        hours=self.calendar_patel.get_work_hours_count(
            datetime_tz(2018,4,2,0,0,0,tzinfo=self.patel.tz),
            datetime_tz(2018,4,6,23,59,59,tzinfo=self.patel.tz),
        )
        self.assertEqual(hours,35)

        leave.unlink()

        #notimezonegivenshouldbeconvertedtoUTC
        #Shouldequaltoaleavebetween2018/04/0310:00:00and2018/04/0410:00:00
        leave=self.env['resource.calendar.leaves'].create({
            'name':'notimezone',
            'calendar_id':self.calendar_patel.id,
            'resource_id':False,
            'date_from':datetime_str(2018,4,3,4,0,0),
            'date_to':datetime_str(2018,4,4,4,0,0),
        })

        hours=self.calendar_patel.get_work_hours_count(
            datetime_tz(2018,4,2,0,0,0,tzinfo=self.patel.tz),
            datetime_tz(2018,4,6,23,59,59,tzinfo=self.patel.tz),
        )
        self.assertEqual(hours,28)

        hours=self.calendar_patel.get_work_hours_count(
            datetime_tz(2018,4,2,23,59,59,tzinfo=self.patel.tz),
            datetime_tz(2018,4,2,0,0,0,tzinfo=self.patel.tz),
        )
        self.assertEqual(hours,0)

        leave.unlink()

        #2weekscalendarweek1
        hours=self.calendar_jules.get_work_hours_count(
            datetime_tz(2018,4,2,0,0,0,tzinfo=self.jules.tz),
            datetime_tz(2018,4,6,23,59,59,tzinfo=self.jules.tz),
        )
        self.assertEqual(hours,30)

        #2weekscalendarweek1
        hours=self.calendar_jules.get_work_hours_count(
            datetime_tz(2018,4,16,0,0,0,tzinfo=self.jules.tz),
            datetime_tz(2018,4,20,23,59,59,tzinfo=self.jules.tz),
        )
        self.assertEqual(hours,30)

        #2weekscalendarweek2
        hours=self.calendar_jules.get_work_hours_count(
            datetime_tz(2018,4,9,0,0,0,tzinfo=self.jules.tz),
            datetime_tz(2018,4,13,23,59,59,tzinfo=self.jules.tz),
        )
        self.assertEqual(hours,16)

        #2weekscalendarweek2,leaveduringadaywherehedoesn'tworkthisweek
        leave=self.env['resource.calendar.leaves'].create({
            'name':'LeaveJulesweek2',
            'calendar_id':self.calendar_jules.id,
            'resource_id':False,
            'date_from':datetime_str(2018,4,11,4,0,0,tzinfo=self.jules.tz),
            'date_to':datetime_str(2018,4,13,4,0,0,tzinfo=self.jules.tz),
        })

        hours=self.calendar_jules.get_work_hours_count(
            datetime_tz(2018,4,9,0,0,0,tzinfo=self.jules.tz),
            datetime_tz(2018,4,13,23,59,59,tzinfo=self.jules.tz),
        )
        self.assertEqual(hours,16)

        leave.unlink()

        #2weekscalendarweek2,leaveduringadaywhereheworksthisweek
        leave=self.env['resource.calendar.leaves'].create({
            'name':'LeaveJulesweek2',
            'calendar_id':self.calendar_jules.id,
            'resource_id':False,
            'date_from':datetime_str(2018,4,9,0,0,0,tzinfo=self.jules.tz),
            'date_to':datetime_str(2018,4,9,23,59,0,tzinfo=self.jules.tz),
        })

        hours=self.calendar_jules.get_work_hours_count(
            datetime_tz(2018,4,9,0,0,0,tzinfo=self.jules.tz),
            datetime_tz(2018,4,13,23,59,59,tzinfo=self.jules.tz),
        )
        self.assertEqual(hours,8)

        leave.unlink()

        #2weekscalendarwithdate_fromanddate_totocheckwork_hours
        self.calendar_jules.write({
            "attendance_ids":[
                (5,0,0),
                (0,0,{
                    "name":"Monday(morning)",
                    "day_period":"morning",
                    "dayofweek":"0",
                    "week_type":"0",
                    "hour_from":8.0,
                    "hour_to":12.0,
                    "date_from":"2022-01-01",
                    "date_to":"2022-01-16"}),
                (0,0,{
                    "name":"Monday(morning)",
                    "day_period":"morning",
                    "dayofweek":"0",
                    "week_type":"0",
                    "hour_from":8.0,
                    "hour_to":12.0,
                    "date_from":"2022-01-17"}),
                (0,0,{
                    "name":"Monday(afternoon)",
                    "day_period":"afternoon",
                    "dayofweek":"0",
                    "week_type":"0",
                    "hour_from":16.0,
                    "hour_to":20.0,
                    "date_from":"2022-01-17"}),
                (0,0,{
                    "name":"Monday(morning)",
                    "day_period":"morning",
                    "dayofweek":"0",
                    "week_type":"1",
                    "hour_from":8.0,
                    "hour_to":12.0,
                    "date_from":"2022-01-01",
                    "date_to":"2022-01-16"}),
                (0,0,{
                    "name":"Monday(afternoon)",
                    "day_period":"afternoon",
                    "dayofweek":"0",
                    "week_type":"1",
                    "hour_from":16.0,
                    "hour_to":20.0,
                    "date_from":"2022-01-01",
                    "date_to":"2022-01-16"}),
                (0,0,{
                    "name":"Monday(morning)",
                    "day_period":"morning",
                    "dayofweek":"0",
                    "week_type":"1",
                    "hour_from":8.0,
                    "hour_to":12.0,
                    "date_from":"2022-01-17"}),
                (0,0,{
                    "name":"Monday(afternoon)",
                    "day_period":"afternoon",
                    "dayofweek":"0",
                    "week_type":"1",
                    "hour_from":16.0,
                    "hour_to":20.0,
                    "date_from":"2022-01-17"})]})
        hours=self.calendar_jules.get_work_hours_count(
            datetime_tz(2022,1,10,0,0,0,tzinfo=self.jules.tz),
            datetime_tz(2022,1,10,23,59,59,tzinfo=self.jules.tz),
        )
        self.assertEqual(hours,4)
        hours=self.calendar_jules.get_work_hours_count(
            datetime_tz(2022,1,17,0,0,0,tzinfo=self.jules.tz),
            datetime_tz(2022,1,17,23,59,59,tzinfo=self.jules.tz),
        )
        self.assertEqual(hours,8)

    deftest_calendar_working_hours_count(self):
        calendar=self.env.ref('resource.resource_calendar_std_35h')
        calendar.tz='UTC'
        res=calendar.get_work_hours_count(
            fields.Datetime.from_string('2017-05-0314:03:00'), #Wednesday(8:00-12:00,13:00-16:00)
            fields.Datetime.from_string('2017-05-0411:03:00'), #Thursday(8:00-12:00,13:00-16:00)
            compute_leaves=False)
        self.assertEqual(res,5.0)

    deftest_calendar_working_hours_24(self):
        self.att_4=self.env['resource.calendar.attendance'].create({
            'name':'Att4',
            'calendar_id':self.calendar_jean.id,
            'dayofweek':'2',
            'hour_from':0,
            'hour_to':24
        })
        res=self.calendar_jean.get_work_hours_count(
            datetime_tz(2018,6,19,23,0,0,tzinfo=self.jean.tz),
            datetime_tz(2018,6,21,1,0,0,tzinfo=self.jean.tz),
            compute_leaves=True)
        self.assertAlmostEqual(res,24.0)

    deftest_plan_hours(self):
        self.env['resource.calendar.leaves'].create({
            'name':'global',
            'calendar_id':self.calendar_jean.id,
            'resource_id':False,
            'date_from':datetime_str(2018,4,11,0,0,0,tzinfo=self.jean.tz),
            'date_to':datetime_str(2018,4,11,23,59,59,tzinfo=self.jean.tz),
        })

        time=self.calendar_jean.plan_hours(2,datetime_tz(2018,4,10,0,0,0,tzinfo=self.jean.tz),compute_leaves=False)
        self.assertEqual(time,datetime_tz(2018,4,10,10,0,0,tzinfo=self.jean.tz))

        time=self.calendar_jean.plan_hours(20,datetime_tz(2018,4,10,0,0,0,tzinfo=self.jean.tz),compute_leaves=False)
        self.assertEqual(time,datetime_tz(2018,4,12,12,0,0,tzinfo=self.jean.tz))

        time=self.calendar_jean.plan_hours(5,datetime_tz(2018,4,10,15,0,0,tzinfo=self.jean.tz),compute_leaves=True)
        self.assertEqual(time,datetime_tz(2018,4,12,12,0,0,tzinfo=self.jean.tz))

        #negativeplanning
        time=self.calendar_jean.plan_hours(-10,datetime_tz(2018,4,10,0,0,0,tzinfo=self.jean.tz),compute_leaves=True)
        self.assertEqual(time,datetime_tz(2018,4,6,14,0,0,tzinfo=self.jean.tz))

        #zeroplanningwithholidays
        time=self.calendar_jean.plan_hours(0,datetime_tz(2018,4,11,0,0,0,tzinfo=self.jean.tz),compute_leaves=True)
        self.assertEqual(time,datetime_tz(2018,4,12,8,0,0,tzinfo=self.jean.tz))
        time=self.calendar_jean.plan_hours(0,datetime_tz(2018,4,10,0,0,0,tzinfo=self.jean.tz),compute_leaves=False)
        self.assertEqual(time,datetime_tz(2018,4,10,8,0,0,tzinfo=self.jean.tz))

        #verysmallplanning
        time=self.calendar_jean.plan_hours(0.0002,datetime_tz(2018,4,10,0,0,0,tzinfo=self.jean.tz),compute_leaves=True)
        self.assertEqual(time,datetime_tz(2018,4,10,8,0,0,720000,tzinfo=self.jean.tz))

        #hugeplanning
        time=self.calendar_jean.plan_hours(3000,datetime_tz(2018,4,10,0,0,0,tzinfo=self.jean.tz),compute_leaves=False)
        self.assertEqual(time,datetime_tz(2019,9,16,16,0,0,tzinfo=self.jean.tz))

    deftest_plan_days(self):
        self.env['resource.calendar.leaves'].create({
            'name':'global',
            'calendar_id':self.calendar_jean.id,
            'resource_id':False,
            'date_from':datetime_str(2018,4,11,0,0,0,tzinfo=self.jean.tz),
            'date_to':datetime_str(2018,4,11,23,59,59,tzinfo=self.jean.tz),
        })

        time=self.calendar_jean.plan_days(1,datetime_tz(2018,4,10,0,0,0,tzinfo=self.jean.tz),compute_leaves=False)
        self.assertEqual(time,datetime_tz(2018,4,10,16,0,0,tzinfo=self.jean.tz))

        time=self.calendar_jean.plan_days(3,datetime_tz(2018,4,10,0,0,0,tzinfo=self.jean.tz),compute_leaves=False)
        self.assertEqual(time,datetime_tz(2018,4,12,16,0,0,tzinfo=self.jean.tz))

        time=self.calendar_jean.plan_days(4,datetime_tz(2018,4,10,16,0,0,tzinfo=self.jean.tz),compute_leaves=True)
        self.assertEqual(time,datetime_tz(2018,4,17,16,0,0,tzinfo=self.jean.tz))

        #negativeplanning
        time=self.calendar_jean.plan_days(-10,datetime_tz(2018,4,10,0,0,0,tzinfo=self.jean.tz),compute_leaves=True)
        self.assertEqual(time,datetime_tz(2018,3,27,8,0,0,tzinfo=self.jean.tz))

        #zeroplanning
        time=self.calendar_jean.plan_days(0,datetime_tz(2018,4,10,0,0,0,tzinfo=self.jean.tz),compute_leaves=True)
        self.assertEqual(time,datetime_tz(2018,4,10,0,0,0,tzinfo=self.jean.tz))

        #verysmallplanningreturnsFalseinthiscase
        #TODO:decideifthisbehaviourisalright
        time=self.calendar_jean.plan_days(0.0002,datetime_tz(2018,4,10,0,0,0,tzinfo=self.jean.tz),compute_leaves=True)
        self.assertEqual(time,False)

        #hugeplanning
        #TODO:Sameasabove
        #NOTE:Maybeallowtosetamaxlimittothemethod
        time=self.calendar_jean.plan_days(3000,datetime_tz(2018,4,10,0,0,0,tzinfo=self.jean.tz),compute_leaves=False)
        self.assertEqual(time,False)

    deftest_closest_time(self):
        #Calendar:
        #Tuesdays8-16
        #Fridays8-13and16-23
        dt=datetime_tz(2020,4,2,7,0,0,tzinfo=self.john.tz)
        calendar_dt=self.calendar_john._get_closest_work_time(dt)
        self.assertFalse(calendar_dt,"Itshouldnotreturnanyvalueforunattendeddays")

        dt=datetime_tz(2020,4,3,7,0,0,tzinfo=self.john.tz)
        range_start=datetime_tz(2020,4,3,8,0,0,tzinfo=self.john.tz)
        range_end=datetime_tz(2020,4,3,19,0,0,tzinfo=self.john.tz)
        calendar_dt=self.calendar_john._get_closest_work_time(dt,search_range=(range_start,range_end))
        self.assertFalse(calendar_dt,"Itshouldnotreturnanyvalueifdtoutsideofrange")

        dt=datetime_tz(2020,4,3,7,0,0,tzinfo=self.john.tz) #before
        start=datetime_tz(2020,4,3,8,0,0,tzinfo=self.john.tz)
        calendar_dt=self.calendar_john._get_closest_work_time(dt)
        self.assertEqual(calendar_dt,start,"Itshouldreturnthestartoftheday")

        dt=datetime_tz(2020,4,3,10,0,0,tzinfo=self.john.tz) #after
        start=datetime_tz(2020,4,3,8,0,0,tzinfo=self.john.tz)
        calendar_dt=self.calendar_john._get_closest_work_time(dt)
        self.assertEqual(calendar_dt,start,"Itshouldreturnthestartoftheclosestattendance")

        dt=datetime_tz(2020,4,3,7,0,0,tzinfo=self.john.tz) #before
        end=datetime_tz(2020,4,3,13,0,0,tzinfo=self.john.tz)
        calendar_dt=self.calendar_john._get_closest_work_time(dt,match_end=True)
        self.assertEqual(calendar_dt,end,"Itshouldreturntheendoftheclosestattendance")

        dt=datetime_tz(2020,4,3,14,0,0,tzinfo=self.john.tz) #after
        end=datetime_tz(2020,4,3,13,0,0,tzinfo=self.john.tz)
        calendar_dt=self.calendar_john._get_closest_work_time(dt,match_end=True)
        self.assertEqual(calendar_dt,end,"Itshouldreturntheendoftheclosestattendance")

        dt=datetime_tz(2020,4,3,0,0,0,tzinfo=self.john.tz)
        start=datetime_tz(2020,4,3,8,0,0,tzinfo=self.john.tz)
        calendar_dt=self.calendar_john._get_closest_work_time(dt)
        self.assertEqual(calendar_dt,start,"Itshouldreturnthestartoftheclosestattendance")

        dt=datetime_tz(2020,4,3,23,59,59,tzinfo=self.john.tz)
        end=datetime_tz(2020,4,3,23,0,0,tzinfo=self.john.tz)
        calendar_dt=self.calendar_john._get_closest_work_time(dt,match_end=True)
        self.assertEqual(calendar_dt,end,"Itshouldreturntheendoftheclosestattendance")

        #witharesourcespecificattendance
        self.env['resource.calendar.attendance'].create({
            'name':'Att4',
            'calendar_id':self.calendar_john.id,
            'dayofweek':'4',
            'hour_from':5,
            'hour_to':6,
            'resource_id':self.john.resource_id.id,
        })
        dt=datetime_tz(2020,4,3,5,0,0,tzinfo=self.john.tz)
        start=datetime_tz(2020,4,3,8,0,0,tzinfo=self.john.tz)
        calendar_dt=self.calendar_john._get_closest_work_time(dt)
        self.assertEqual(calendar_dt,start,"Itshouldnottakeintoaccountresoucespecificattendances")

        dt=datetime_tz(2020,4,3,5,0,0,tzinfo=self.john.tz)
        start=datetime_tz(2020,4,3,5,0,0,tzinfo=self.john.tz)
        calendar_dt=self.calendar_john._get_closest_work_time(dt,resource=self.john.resource_id)
        self.assertEqual(calendar_dt,start,"Itshouldhavetakenjohn'sspecificattendances")

        dt=datetime_tz(2020,4,4,1,0,0,tzinfo='UTC') #ThenextdayinUTC,butstillthe3rdinjohn'stimezone(America/Los_Angeles)
        start=datetime_tz(2020,4,3,16,0,0,tzinfo=self.john.tz)
        calendar_dt=self.calendar_john._get_closest_work_time(dt,resource=self.john.resource_id)
        self.assertEqual(calendar_dt,start,"Itshouldhavefoundtheattendanceonthe3rdApril")

classTestResMixin(TestResourceCommon):

    deftest_adjust_calendar(self):
        #Calendar:
        #Tuesdays8-16
        #Fridays8-13and16-23
        result=self.john._adjust_to_calendar(
            datetime_tz(2020,4,3,9,0,0,tzinfo=self.john.tz),
            datetime_tz(2020,4,3,14,0,0,tzinfo=self.john.tz),
        )
        self.assertEqual(result[self.john],(
            datetime_tz(2020,4,3,8,0,0,tzinfo=self.john.tz),
            datetime_tz(2020,4,3,13,0,0,tzinfo=self.john.tz),
        ))

        result=self.john._adjust_to_calendar(
            datetime_tz(2020,4,3,13,1,0,tzinfo=self.john.tz),
            datetime_tz(2020,4,3,14,0,0,tzinfo=self.john.tz),
        )
        self.assertEqual(result[self.john],(
            datetime_tz(2020,4,3,16,0,0,tzinfo=self.john.tz),
            datetime_tz(2020,4,3,23,0,0,tzinfo=self.john.tz),
        ))

        result=self.john._adjust_to_calendar(
            datetime_tz(2020,4,4,9,0,0,tzinfo=self.john.tz), #bothadaywithoutattendance
            datetime_tz(2020,4,4,14,0,0,tzinfo=self.john.tz),
        )
        self.assertEqual(result[self.john],(None,None))

        result=self.john._adjust_to_calendar(
            datetime_tz(2020,4,3,8,0,0,tzinfo=self.john.tz),
            datetime_tz(2020,4,4,14,0,0,tzinfo=self.john.tz), #daywithoutattendance
        )
        self.assertEqual(result[self.john],(
            datetime_tz(2020,4,3,8,0,0,tzinfo=self.john.tz),
            None,
        ))

        result=self.john._adjust_to_calendar(
            datetime_tz(2020,4,2,8,0,0,tzinfo=self.john.tz), #daywithoutattendance
            datetime_tz(2020,4,3,14,0,0,tzinfo=self.john.tz),
        )
        self.assertEqual(result[self.john],(
            None,
            datetime_tz(2020,4,3,13,0,0,tzinfo=self.john.tz),
        ))

        #Itshouldfindthestartandendwithinthesearchrange
        result=self.paul._adjust_to_calendar(
            datetime_tz(2020,4,2,2,0,0,tzinfo='UTC'),
            datetime_tz(2020,4,3,1,59,59,tzinfo='UTC'),
        )

        self.assertEqual(result[self.paul],(
            datetime_tz(2020,4,2,4,0,tzinfo='UTC'),
            datetime_tz(2020,4,2,18,0,tzinfo='UTC')
        ),"ItshouldhavefoundthestartandendoftheshiftonthesamedayonApril2nd,2020")

    deftest_adjust_calendar_timezone_before(self):
        #Calendar:
        #Everyday8-16
        self.jean.tz='Japan'
        self.calendar_jean.tz='Europe/Brussels'

        result=self.jean._adjust_to_calendar(
            datetime_tz(2020,4,1,0,0,0,tzinfo='Japan'),
            datetime_tz(2020,4,1,23,59,59,tzinfo='Japan'),
        )
        self.assertEqual(result[self.jean],(
            datetime_tz(2020,4,1,8,0,0,tzinfo='Japan'),
            datetime_tz(2020,4,1,16,0,0,tzinfo='Japan'),
        ),"Itshouldhavefoundastartingtimethe1st")

    deftest_adjust_calendar_timezone_after(self):
        #Calendar:
        #Tuesdays8-16
        #Fridays8-13and16-23
        tz='Europe/Brussels'
        self.john.tz=tz
        result=self.john._adjust_to_calendar(
            datetime(2020,4,2,23,0,0), #ThepreviousdayinUTC,butthe3rdinEurope/Brussels
            datetime(2020,4,3,20,0,0),
        )
        self.assertEqual(result[self.john],(
            datetime(2020,4,3,6,0,0),
            datetime(2020,4,3,21,0,0),
        ),"Itshouldhavefoundastartingtimethe3rd")

    deftest_work_days_data(self):
        #LookingatJean'scalendar

        #ViewingitasJean
        data=self.jean._get_work_days_data_batch(
            datetime_tz(2018,4,2,0,0,0,tzinfo=self.jean.tz),
            datetime_tz(2018,4,6,16,0,0,tzinfo=self.jean.tz),
        )[self.jean.id]
        self.assertEqual(data,{'days':5,'hours':40})

        #ViewingitasPatel
        #Viewsfrom2018/04/0120:00:00to2018/04/0612:00:00
        data=self.jean._get_work_days_data_batch(
            datetime_tz(2018,4,2,0,0,0,tzinfo=self.patel.tz),
            datetime_tz(2018,4,6,16,0,0,tzinfo=self.patel.tz),
        )[self.jean.id]
        self.assertEqual(data,{'days':4.5,'hours':36}) #Weseeonly36hours

        #ViewingitasJohn
        #Viewsfrom2018/04/0209:00:00to2018/04/0702:00:00
        data=self.jean._get_work_days_data_batch(
            datetime_tz(2018,4,2,0,0,0,tzinfo=self.john.tz),
            datetime_tz(2018,4,6,16,0,0,tzinfo=self.john.tz),
        )[self.jean.id]
        #stillshowingas5daysbecauseofrounding,butweseeonly39hours
        self.assertEqual(data,{'days':4.875,'hours':39})

        #LookingatJohn'scalendar

        #ViewingitasJean
        #Viewsfrom2018/04/0115:00:00to2018/04/0614:00:00
        data=self.john._get_work_days_data_batch(
            datetime_tz(2018,4,2,0,0,0,tzinfo=self.jean.tz),
            datetime_tz(2018,4,6,23,0,0,tzinfo=self.jean.tz),
        )[self.john.id]
        self.assertEqual(data,{'days':1.4375,'hours':13})

        #ViewingitasPatel
        #Viewsfrom2018/04/0111:00:00to2018/04/0610:00:00
        data=self.john._get_work_days_data_batch(
            datetime_tz(2018,4,2,0,0,0,tzinfo=self.patel.tz),
            datetime_tz(2018,4,6,23,0,0,tzinfo=self.patel.tz),
        )[self.john.id]
        self.assertEqual(data,{'days':1.1875,'hours':10})

        #ViewingitasJohn
        data=self.john._get_work_days_data_batch(
            datetime_tz(2018,4,2,0,0,0,tzinfo=self.john.tz),
            datetime_tz(2018,4,6,23,0,0,tzinfo=self.john.tz),
        )[self.john.id]
        self.assertEqual(data,{'days':2,'hours':20})

        #usingJeanasatimezonereference
        data=self.john._get_work_days_data_batch(
            datetime_tz(2018,4,2,0,0,0,tzinfo=self.john.tz),
            datetime_tz(2018,4,6,23,0,0,tzinfo=self.john.tz),
            calendar=self.calendar_jean,
        )[self.john.id]
        self.assertEqual(data,{'days':5,'hours':40})

        #halfdays
        leave=self.env['resource.calendar.leaves'].create({
            'name':'half',
            'calendar_id':self.calendar_jean.id,
            'resource_id':self.jean.resource_id.id,
            'date_from':datetime_str(2018,4,2,10,0,0,tzinfo=self.jean.tz),
            'date_to':datetime_str(2018,4,2,14,0,0,tzinfo=self.jean.tz),
        })

        data=self.jean._get_work_days_data_batch(
            datetime_tz(2018,4,2,0,0,0,tzinfo=self.jean.tz),
            datetime_tz(2018,4,6,23,0,0,tzinfo=self.jean.tz),
        )[self.jean.id]
        self.assertEqual(data,{'days':4.5,'hours':36})

        #usingJohnasatimezonereference,leavesareoutsideattendances
        data=self.john._get_work_days_data_batch(
            datetime_tz(2018,4,2,0,0,0,tzinfo=self.john.tz),
            datetime_tz(2018,4,6,23,0,0,tzinfo=self.john.tz),
            calendar=self.calendar_jean,
        )[self.john.id]
        self.assertEqual(data,{'days':5,'hours':40})

        leave.unlink()

        #leavesize0
        leave=self.env['resource.calendar.leaves'].create({
            'name':'zero',
            'calendar_id':self.calendar_jean.id,
            'resource_id':False,
            'date_from':datetime_str(2018,4,2,10,0,0,tzinfo=self.jean.tz),
            'date_to':datetime_str(2018,4,2,10,0,0,tzinfo=self.jean.tz),
        })

        data=self.jean._get_work_days_data_batch(
            datetime_tz(2018,4,2,0,0,0,tzinfo=self.jean.tz),
            datetime_tz(2018,4,6,23,0,0,tzinfo=self.jean.tz),
        )[self.jean.id]
        self.assertEqual(data,{'days':5,'hours':40})

        leave.unlink()

        #leaveverysmallsize
        leave=self.env['resource.calendar.leaves'].create({
            'name':'small',
            'calendar_id':self.calendar_jean.id,
            'resource_id':False,
            'date_from':datetime_str(2018,4,2,10,0,0,tzinfo=self.jean.tz),
            'date_to':datetime_str(2018,4,2,10,0,1,tzinfo=self.jean.tz),
        })

        data=self.jean._get_work_days_data_batch(
            datetime_tz(2018,4,2,0,0,0,tzinfo=self.jean.tz),
            datetime_tz(2018,4,6,23,0,0,tzinfo=self.jean.tz),
        )[self.jean.id]
        self.assertEqual(data['days'],5)
        self.assertAlmostEqual(data['hours'],40,2)

    deftest_leaves_days_data(self):
        #Jeantakesaleave
        self.env['resource.calendar.leaves'].create({
            'name':'JeanisvisitingIndia',
            'calendar_id':self.jean.resource_calendar_id.id,
            'resource_id':self.jean.resource_id.id,
            'date_from':datetime_str(2018,4,10,8,0,0,tzinfo=self.jean.tz),
            'date_to':datetime_str(2018,4,10,16,0,0,tzinfo=self.jean.tz),
        })

        #JohntakesaleaveforJean
        self.env['resource.calendar.leaves'].create({
            'name':'JeaniscomminginUSA',
            'calendar_id':self.jean.resource_calendar_id.id,
            'resource_id':self.jean.resource_id.id,
            'date_from':datetime_str(2018,4,12,8,0,0,tzinfo=self.john.tz),
            'date_to':datetime_str(2018,4,12,16,0,0,tzinfo=self.john.tz),
        })

        #Jeanaskstoseehowmuchleavehehastaken
        data=self.jean._get_leave_days_data_batch(
            datetime_tz(2018,4,9,0,0,0,tzinfo=self.jean.tz),
            datetime_tz(2018,4,13,23,59,59,tzinfo=self.jean.tz),
        )[self.jean.id]
        #Seesonly1dayand8hoursbecause,asjohnisinUTC-7thesecondleaveisnotin
        #theattendancesofJean
        self.assertEqual(data,{'days':1,'hours':8})

        #PatelAskstoseewhenJeanhastakensomeleaves
        #Patelshouldseethesame
        data=self.jean._get_leave_days_data_batch(
            datetime_tz(2018,4,9,0,0,0,tzinfo=self.patel.tz),
            datetime_tz(2018,4,13,23,59,59,tzinfo=self.patel.tz),
        )[self.jean.id]
        self.assertEqual(data,{'days':1,'hours':8})

        #usePatelasaresource,jean'sleavesarenotvisible
        datas=self.patel._get_leave_days_data_batch(
            datetime_tz(2018,4,9,0,0,0,tzinfo=self.patel.tz),
            datetime_tz(2018,4,13,23,59,59,tzinfo=self.patel.tz),
            calendar=self.calendar_jean,
        )[self.patel.id]
        self.assertEqual(datas['days'],0)
        self.assertEqual(datas['hours'],0)

        #JeantakesaleaveforJohn
        #Gives3hours(3/8ofaday)
        self.env['resource.calendar.leaves'].create({
            'name':'Johnissick',
            'calendar_id':self.john.resource_calendar_id.id,
            'resource_id':self.john.resource_id.id,
            'date_from':datetime_str(2018,4,10,0,0,0,tzinfo=self.jean.tz),
            'date_to':datetime_str(2018,4,10,20,0,0,tzinfo=self.jean.tz),
        })

        #Johntakesaleave
        #Givesallday(12hours)
        self.env['resource.calendar.leaves'].create({
            'name':'Johngoestoholywood',
            'calendar_id':self.john.resource_calendar_id.id,
            'resource_id':self.john.resource_id.id,
            'date_from':datetime_str(2018,4,13,7,0,0,tzinfo=self.john.tz),
            'date_to':datetime_str(2018,4,13,18,0,0,tzinfo=self.john.tz),
        })

        #Johnaskshowmuchleaveshehas
        #Heseesthathehasonly15hoursofleaveinhisattendances
        data=self.john._get_leave_days_data_batch(
            datetime_tz(2018,4,9,0,0,0,tzinfo=self.john.tz),
            datetime_tz(2018,4,13,23,59,59,tzinfo=self.john.tz),
        )[self.john.id]
        self.assertEqual(data,{'days':0.9375,'hours':10})

        #halfdays
        leave=self.env['resource.calendar.leaves'].create({
            'name':'half',
            'calendar_id':self.calendar_jean.id,
            'resource_id':self.jean.resource_id.id,
            'date_from':datetime_str(2018,4,2,10,0,0,tzinfo=self.jean.tz),
            'date_to':datetime_str(2018,4,2,14,0,0,tzinfo=self.jean.tz),
        })

        data=self.jean._get_leave_days_data_batch(
            datetime_tz(2018,4,2,0,0,0,tzinfo=self.jean.tz),
            datetime_tz(2018,4,6,23,0,0,tzinfo=self.jean.tz),
        )[self.jean.id]
        self.assertEqual(data,{'days':0.5,'hours':4})

        leave.unlink()

        #leavesize0
        leave=self.env['resource.calendar.leaves'].create({
            'name':'zero',
            'calendar_id':self.calendar_jean.id,
            'resource_id':False,
            'date_from':datetime_str(2018,4,2,10,0,0,tzinfo=self.jean.tz),
            'date_to':datetime_str(2018,4,2,10,0,0,tzinfo=self.jean.tz),
        })

        data=self.jean._get_leave_days_data_batch(
            datetime_tz(2018,4,2,0,0,0,tzinfo=self.jean.tz),
            datetime_tz(2018,4,6,23,0,0,tzinfo=self.jean.tz),
        )[self.jean.id]
        self.assertEqual(data,{'days':0,'hours':0})

        leave.unlink()

        #leaveverysmallsize
        leave=self.env['resource.calendar.leaves'].create({
            'name':'small',
            'calendar_id':self.calendar_jean.id,
            'resource_id':False,
            'date_from':datetime_str(2018,4,2,10,0,0,tzinfo=self.jean.tz),
            'date_to':datetime_str(2018,4,2,10,0,1,tzinfo=self.jean.tz),
        })

        data=self.jean._get_leave_days_data_batch(
            datetime_tz(2018,4,2,0,0,0,tzinfo=self.jean.tz),
            datetime_tz(2018,4,6,23,0,0,tzinfo=self.jean.tz),
        )[self.jean.id]
        self.assertEqual(data['days'],0)
        self.assertAlmostEqual(data['hours'],0,2)

        leave.unlink()

    deftest_list_leaves(self):
        jean_leave=self.env['resource.calendar.leaves'].create({
            'name':"Jean'ssonissick",
            'calendar_id':self.jean.resource_calendar_id.id,
            'resource_id':False,
            'date_from':datetime_str(2018,4,10,0,0,0,tzinfo=self.jean.tz),
            'date_to':datetime_str(2018,4,10,23,59,59,tzinfo=self.jean.tz),
        })

        leaves=self.jean.list_leaves(
            datetime_tz(2018,4,9,0,0,0,tzinfo=self.jean.tz),
            datetime_tz(2018,4,13,23,59,59,tzinfo=self.jean.tz),
        )
        self.assertEqual(leaves,[(date(2018,4,10),8,jean_leave)])

        #halfdays
        leave=self.env['resource.calendar.leaves'].create({
            'name':'half',
            'calendar_id':self.jean.resource_calendar_id.id,
            'resource_id':self.jean.resource_id.id,
            'date_from':datetime_str(2018,4,2,10,0,0,tzinfo=self.jean.tz),
            'date_to':datetime_str(2018,4,2,14,0,0,tzinfo=self.jean.tz),
        })

        leaves=self.jean.list_leaves(
            datetime_tz(2018,4,2,0,0,0,tzinfo=self.jean.tz),
            datetime_tz(2018,4,6,23,0,0,tzinfo=self.jean.tz),
        )
        self.assertEqual(leaves,[(date(2018,4,2),4,leave)])

        leave.unlink()

        #verysmallsize
        leave=self.env['resource.calendar.leaves'].create({
            'name':'small',
            'calendar_id':self.jean.resource_calendar_id.id,
            'resource_id':self.jean.resource_id.id,
            'date_from':datetime_str(2018,4,2,10,0,0,tzinfo=self.jean.tz),
            'date_to':datetime_str(2018,4,2,10,0,1,tzinfo=self.jean.tz),
        })

        leaves=self.jean.list_leaves(
            datetime_tz(2018,4,2,0,0,0,tzinfo=self.jean.tz),
            datetime_tz(2018,4,6,23,0,0,tzinfo=self.jean.tz),
        )
        self.assertEqual(len(leaves),1)
        self.assertEqual(leaves[0][0],date(2018,4,2))
        self.assertAlmostEqual(leaves[0][1],0,2)
        self.assertEqual(leaves[0][2].id,leave.id)

        leave.unlink()

        #size0
        leave=self.env['resource.calendar.leaves'].create({
            'name':'zero',
            'calendar_id':self.jean.resource_calendar_id.id,
            'resource_id':self.jean.resource_id.id,
            'date_from':datetime_str(2018,4,2,10,0,0,tzinfo=self.jean.tz),
            'date_to':datetime_str(2018,4,2,10,0,0,tzinfo=self.jean.tz),
        })

        leaves=self.jean.list_leaves(
            datetime_tz(2018,4,2,0,0,0,tzinfo=self.jean.tz),
            datetime_tz(2018,4,6,23,0,0,tzinfo=self.jean.tz),
        )
        self.assertEqual(leaves,[])

        leave.unlink()

    deftest_list_work_time_per_day(self):
        working_time=self.john.list_work_time_per_day(
            datetime_tz(2018,4,9,0,0,0,tzinfo=self.john.tz),
            datetime_tz(2018,4,13,23,59,59,tzinfo=self.john.tz),
        )
        self.assertEqual(working_time,[
            (date(2018,4,10),8),
            (date(2018,4,13),12),
        ])

        #changejohn'sresource'stimezone
        self.john.resource_id.tz='Europe/Brussels'
        self.assertEqual(self.john.tz,'Europe/Brussels')
        self.assertEqual(self.calendar_john.tz,'America/Los_Angeles')
        working_time=self.john.list_work_time_per_day(
            datetime_tz(2018,4,9,0,0,0,tzinfo=self.john.tz),
            datetime_tz(2018,4,13,23,59,59,tzinfo=self.john.tz),
        )
        self.assertEqual(working_time,[
            (date(2018,4,10),8),
            (date(2018,4,13),12),
        ])

        #halfdays
        leave=self.env['resource.calendar.leaves'].create({
            'name':'small',
            'calendar_id':self.jean.resource_calendar_id.id,
            'resource_id':self.jean.resource_id.id,
            'date_from':datetime_str(2018,4,2,10,0,0,tzinfo=self.jean.tz),
            'date_to':datetime_str(2018,4,2,14,0,0,tzinfo=self.jean.tz),
        })

        working_time=self.jean.list_work_time_per_day(
            datetime_tz(2018,4,2,0,0,0,tzinfo=self.jean.tz),
            datetime_tz(2018,4,6,23,0,0,tzinfo=self.jean.tz),
        )
        self.assertEqual(working_time,[
            (date(2018,4,2),4),
            (date(2018,4,3),8),
            (date(2018,4,4),8),
            (date(2018,4,5),8),
            (date(2018,4,6),8),
        ])

        leave.unlink()

        #verysmallsize
        leave=self.env['resource.calendar.leaves'].create({
            'name':'small',
            'calendar_id':self.jean.resource_calendar_id.id,
            'resource_id':self.jean.resource_id.id,
            'date_from':datetime_str(2018,4,2,10,0,0,tzinfo=self.jean.tz),
            'date_to':datetime_str(2018,4,2,10,0,1,tzinfo=self.jean.tz),
        })

        working_time=self.jean.list_work_time_per_day(
            datetime_tz(2018,4,2,0,0,0,tzinfo=self.jean.tz),
            datetime_tz(2018,4,6,23,0,0,tzinfo=self.jean.tz),
        )
        self.assertEqual(len(working_time),5)
        self.assertEqual(working_time[0][0],date(2018,4,2))
        self.assertAlmostEqual(working_time[0][1],8,2)

        leave.unlink()

        #size0
        leave=self.env['resource.calendar.leaves'].create({
            'name':'zero',
            'calendar_id':self.jean.resource_calendar_id.id,
            'resource_id':self.jean.resource_id.id,
            'date_from':datetime_str(2018,4,2,10,0,0,tzinfo=self.jean.tz),
            'date_to':datetime_str(2018,4,2,10,0,0,tzinfo=self.jean.tz),
        })

        working_time=self.jean.list_work_time_per_day(
            datetime_tz(2018,4,2,0,0,0,tzinfo=self.jean.tz),
            datetime_tz(2018,4,6,23,0,0,tzinfo=self.jean.tz),
        )
        self.assertEqual(working_time,[
            (date(2018,4,2),8),
            (date(2018,4,3),8),
            (date(2018,4,4),8),
            (date(2018,4,5),8),
            (date(2018,4,6),8),
        ])

        leave.unlink()


classTestTimezones(TestResourceCommon):
    defsetUp(self):
        super(TestTimezones,self).setUp()

        self.tz1='Etc/GMT+6'
        self.tz2='Europe/Brussels'
        self.tz3='Etc/GMT-10'
        self.tz4='Etc/GMT+10'

    deftest_work_hours_count(self):
        #Whennotimezone=>UTC
        count=self.calendar_jean.get_work_hours_count(
            datetime_tz(2018,4,10,8,0,0),
            datetime_tz(2018,4,10,12,0,0),
        )
        self.assertEqual(count,4)

        #Thistimezoneisnotthesameasthecalendar'sone
        count=self.calendar_jean.get_work_hours_count(
            datetime_tz(2018,4,10,8,0,0,tzinfo=self.tz1),
            datetime_tz(2018,4,10,12,0,0,tzinfo=self.tz1),
        )
        self.assertEqual(count,0)

        #Usingtwodifferenttimezones
        #10-04-201806:00:00-10-04-201802:00:00
        count=self.calendar_jean.get_work_hours_count(
            datetime_tz(2018,4,10,8,0,0,tzinfo=self.tz2),
            datetime_tz(2018,4,10,12,0,0,tzinfo=self.tz3),
        )
        self.assertEqual(count,0)

        #Usingtwodifferenttimezones
        #2018-4-1006:00:00-2018-4-1022:00:00
        count=self.calendar_jean.get_work_hours_count(
            datetime_tz(2018,4,10,8,0,0,tzinfo=self.tz2),
            datetime_tz(2018,4,10,12,0,0,tzinfo=self.tz4),
        )
        self.assertEqual(count,8)

    deftest_plan_hours(self):
        dt=self.calendar_jean.plan_hours(10,datetime_tz(2018,4,10,8,0,0))
        self.assertEqual(dt,datetime_tz(2018,4,11,10,0,0))

        dt=self.calendar_jean.plan_hours(10,datetime_tz(2018,4,10,8,0,0,tzinfo=self.tz4))
        self.assertEqual(dt,datetime_tz(2018,4,11,22,0,0,tzinfo=self.tz4))

    deftest_plan_days(self):
        dt=self.calendar_jean.plan_days(2,datetime_tz(2018,4,10,8,0,0))
        self.assertEqual(dt,datetime_tz(2018,4,11,14,0,0))

        #Weloseonedaybecauseoftimezone
        dt=self.calendar_jean.plan_days(2,datetime_tz(2018,4,10,8,0,0,tzinfo=self.tz4))
        self.assertEqual(dt,datetime_tz(2018,4,12,4,0,0,tzinfo=self.tz4))

    deftest_work_data(self):
        #09-04-201810:00:00-13-04-201818:00:00
        data=self.jean._get_work_days_data_batch(
            datetime_tz(2018,4,9,8,0,0),
            datetime_tz(2018,4,13,16,0,0),
        )[self.jean.id]
        self.assertEqual(data,{'days':4.75,'hours':38})

        #09-04-201800:00:00-13-04-201808:00:00
        data=self.jean._get_work_days_data_batch(
            datetime_tz(2018,4,9,8,0,0,tzinfo=self.tz3),
            datetime_tz(2018,4,13,16,0,0,tzinfo=self.tz3),
        )[self.jean.id]
        self.assertEqual(data,{'days':4,'hours':32})

        #09-04-201808:00:00-14-04-201812:00:00
        data=self.jean._get_work_days_data_batch(
            datetime_tz(2018,4,9,8,0,0,tzinfo=self.tz2),
            datetime_tz(2018,4,13,16,0,0,tzinfo=self.tz4),
        )[self.jean.id]
        self.assertEqual(data,{'days':5,'hours':40})

        #Juleswith2weekscalendar
        #02-04-201800:00:00-6-04-201823:59:59
        data=self.jules._get_work_days_data_batch(
            datetime_tz(2018,4,2,0,0,0,tzinfo=self.jules.tz),
            datetime_tz(2018,4,6,23,59,59,tzinfo=self.jules.tz),
        )[self.jules.id]
        self.assertEqual(data,{'days':4,'hours':30})

        #Juleswith2weekscalendar
        #02-04-201800:00:00-14-04-201823:59:59
        data=self.jules._get_work_days_data_batch(
            datetime_tz(2018,4,2,0,0,0,tzinfo=self.jules.tz),
            datetime_tz(2018,4,14,23,59,59,tzinfo=self.jules.tz),
        )[self.jules.id]
        self.assertEqual(data,{'days':6,'hours':46})

        #Juleswith2weekscalendar
        #12-29-201400:00:00-27-12-201923:59:59=>261weeks
        #130weekstype1:131*4=524daysand131*30=3930hours
        #131weekstype2:130*2=260daysand130*16=2080hours
        data=self.jules._get_work_days_data_batch(
            datetime_tz(2014,12,29,0,0,0,tzinfo=self.jules.tz),
            datetime_tz(2019,12,27,23,59,59,tzinfo=self.jules.tz),
        )[self.jules.id]
        self.assertEqual(data,{'days':784,'hours':6010})

    deftest_leave_data(self):
        self.env['resource.calendar.leaves'].create({
            'name':'',
            'calendar_id':self.jean.resource_calendar_id.id,
            'resource_id':self.jean.resource_id.id,
            'date_from':datetime_str(2018,4,9,8,0,0,tzinfo=self.tz2),
            'date_to':datetime_str(2018,4,9,14,0,0,tzinfo=self.tz2),
        })

        #09-04-201810:00:00-13-04-201818:00:00
        data=self.jean._get_leave_days_data_batch(
            datetime_tz(2018,4,9,8,0,0),
            datetime_tz(2018,4,13,16,0,0),
        )[self.jean.id]
        self.assertEqual(data,{'days':0.5,'hours':4})

        #09-04-201800:00:00-13-04-201808:00:00
        data=self.jean._get_leave_days_data_batch(
            datetime_tz(2018,4,9,8,0,0,tzinfo=self.tz3),
            datetime_tz(2018,4,13,16,0,0,tzinfo=self.tz3),
        )[self.jean.id]
        self.assertEqual(data,{'days':0.75,'hours':6})

        #09-04-201808:00:00-14-04-201812:00:00
        data=self.jean._get_leave_days_data_batch(
            datetime_tz(2018,4,9,8,0,0,tzinfo=self.tz2),
            datetime_tz(2018,4,13,16,0,0,tzinfo=self.tz4),
        )[self.jean.id]
        self.assertEqual(data,{'days':0.75,'hours':6})

    deftest_leaves(self):
        leave=self.env['resource.calendar.leaves'].create({
            'name':'',
            'calendar_id':self.jean.resource_calendar_id.id,
            'resource_id':self.jean.resource_id.id,
            'date_from':datetime_str(2018,4,9,8,0,0,tzinfo=self.tz2),
            'date_to':datetime_str(2018,4,9,14,0,0,tzinfo=self.tz2),
        })

        #09-04-201810:00:00-13-04-201818:00:00
        leaves=self.jean.list_leaves(
            datetime_tz(2018,4,9,8,0,0),
            datetime_tz(2018,4,13,16,0,0),
        )
        self.assertEqual(leaves,[(date(2018,4,9),4,leave)])

        #09-04-201800:00:00-13-04-201808:00:00
        leaves=self.jean.list_leaves(
            datetime_tz(2018,4,9,8,0,0,tzinfo=self.tz3),
            datetime_tz(2018,4,13,16,0,0,tzinfo=self.tz3),
        )
        self.assertEqual(leaves,[(date(2018,4,9),6,leave)])

        #09-04-201808:00:00-14-04-201812:00:00
        leaves=self.jean.list_leaves(
            datetime_tz(2018,4,9,8,0,0,tzinfo=self.tz2),
            datetime_tz(2018,4,13,16,0,0,tzinfo=self.tz4),
        )
        self.assertEqual(leaves,[(date(2018,4,9),6,leave)])

    deftest_works(self):
        work=self.jean.list_work_time_per_day(
            datetime_tz(2018,4,9,8,0,0),
            datetime_tz(2018,4,13,16,0,0),
        )
        self.assertEqual(work,[
            (date(2018,4,9),6),
            (date(2018,4,10),8),
            (date(2018,4,11),8),
            (date(2018,4,12),8),
            (date(2018,4,13),8),
        ])

        work=self.jean.list_work_time_per_day(
            datetime_tz(2018,4,9,8,0,0,tzinfo=self.tz3),
            datetime_tz(2018,4,13,16,0,0,tzinfo=self.tz3),
        )
        self.assertEqual(len(work),4)
        self.assertEqual(work,[
            (date(2018,4,9),8),
            (date(2018,4,10),8),
            (date(2018,4,11),8),
            (date(2018,4,12),8),
        ])

        work=self.jean.list_work_time_per_day(
            datetime_tz(2018,4,9,8,0,0,tzinfo=self.tz2),
            datetime_tz(2018,4,13,16,0,0,tzinfo=self.tz4),
        )
        self.assertEqual(work,[
            (date(2018,4,9),8),
            (date(2018,4,10),8),
            (date(2018,4,11),8),
            (date(2018,4,12),8),
            (date(2018,4,13),8),
        ])

    @freeze_time("2022-09-2115:30:00",tz_offset=-10)
    deftest_unavailable_intervals(self):
        resource=self.env['resource.resource'].create({
            'name':'resource',
            'tz':self.tz3,
        })
        intervals=resource._get_unavailable_intervals(datetime(2022,9,21),datetime(2022,9,22))
        self.assertEqual(list(intervals.values())[0],[
            (datetime(2022,9,21,0,0,tzinfo=utc),datetime(2022,9,21,6,0,tzinfo=utc)),
            (datetime(2022,9,21,10,0,tzinfo=utc),datetime(2022,9,21,11,0,tzinfo=utc)),
            (datetime(2022,9,21,15,0,tzinfo=utc),datetime(2022,9,22,0,0,tzinfo=utc)),
        ])
