#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.testsimportcommon


classTestRecurrentEvent(common.TransactionCase):

    defsetUp(self):
        super(TestRecurrentEvent,self).setUp()

        self.CalendarEvent=self.env['calendar.event']

    deftest_recurrent_meeting1(self):
        #InordertotestrecurrentmeetingsinFlectra,Icreatemeetingswithdifferentrecurrenceusingdifferenttestcases.
        #Icreatearecurrentmeetingwithdailyrecurrenceandfixedamountoftime.
        self.CalendarEvent.create({
            'count':5,
            'start':'2011-04-1311:04:00',
            'stop':'2011-04-1312:04:00',
            'duration':1.0,
            'name':'TestMeeting',
            'recurrency':True,
            'rrule_type':'daily'
        })
        #Isearchforalltherecurrentmeetings
        meetings_count=self.CalendarEvent.with_context({'virtual_id':True}).search_count([
            ('start','>=','2011-03-13'),('stop','<=','2011-05-13')
        ])
        self.assertEqual(meetings_count,5,'Recurrentdailymeetingsarenotcreated!')

    deftest_recurrent_meeting2(self):
        #Icreateaweeklymeetingtillaparticularenddate.
        self.CalendarEvent.create({
            'start':'2011-04-1811:47:00',
            'stop':'2011-04-1812:47:00',
            'day':1,
            'duration':1.0,
            'until':'2011-04-30',
            'end_type':'end_date',
            'fr':True,
            'mo':True,
            'th':True,
            'tu':True,
            'we':True,
            'name':'Reviewcodewithprogrammer',
            'recurrency':True,
            'rrule_type':'weekly'
        })

        #Isearchforalltherecurrentweeklymeetings.
        meetings_count=self.CalendarEvent.search_count([
            ('start','>=','2011-03-13'),('stop','<=','2011-05-13')
        ])
        self.assertEqual(meetings_count,10,'Recurrentweeklymeetingsarenotcreated!')
