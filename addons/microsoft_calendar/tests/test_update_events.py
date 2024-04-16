#-*-coding:utf-8-*-
fromdatetimeimportdatetime,timedelta
fromdateutil.parserimportparse
importlogging
importpytz
fromunittest.mockimportpatch,ANY

fromflectra.addons.microsoft_calendar.utils.microsoft_calendarimportMicrosoftCalendarService
fromflectra.addons.microsoft_calendar.utils.microsoft_eventimportMicrosoftEvent
fromflectra.addons.microsoft_calendar.models.res_usersimportUser
fromflectra.addons.microsoft_calendar.utils.event_id_storageimportcombine_ids
fromflectra.addons.microsoft_calendar.tests.commonimportTestCommon,mock_get_token,_modified_date_in_the_future,patch_api
fromflectra.exceptionsimportUserError

_logger=logging.getLogger(__name__)

@patch.object(User,'_get_microsoft_calendar_token',mock_get_token)
classTestUpdateEvents(TestCommon):

    @patch_api
    defsetUp(self):
        super(TestUpdateEvents,self).setUp()
        self.create_events_for_tests()

    #-------------------------------------------------------------------------------
    #UpdatefromFlectratoOutlook
    #-------------------------------------------------------------------------------

    #------Simpleevent------

    @patch.object(MicrosoftCalendarService,'patch')
    deftest_update_simple_event_from_flectra(self,mock_patch):
        """
        UpdateanFlectraeventwithOutlooksyncenabled
        """

        #arrange
        mock_patch.return_value=True

        #act
        res=self.simple_event.with_user(self.organizer_user).write({"name":"mynewsimpleevent"})
        self.call_post_commit_hooks()
        self.simple_event.invalidate_cache()

        #assert
        self.assertTrue(res)
        mock_patch.assert_called_once_with(
            self.simple_event.ms_organizer_event_id,
            {"subject":"mynewsimpleevent"},
            token=mock_get_token(self.organizer_user),
            timeout=ANY,
        )
        self.assertEqual(self.simple_event.name,"mynewsimpleevent")

    @patch.object(MicrosoftCalendarService,'patch')
    deftest_update_simple_event_from_flectra_attendee_calendar(self,mock_patch):
        """
        UpdateanFlectraeventfromtheattendeecalendar.
        """

        #arrange
        mock_patch.return_value=True

        #act
        res=self.simple_event.with_user(self.attendee_user).write({"name":"mynewsimpleevent"})
        self.call_post_commit_hooks()
        self.simple_event.invalidate_cache()

        #assert
        self.assertTrue(res)
        mock_patch.assert_called_once_with(
            self.simple_event.ms_organizer_event_id,
            {"subject":"mynewsimpleevent"},
            token=mock_get_token(self.organizer_user),
            timeout=ANY,
        )
        self.assertEqual(self.simple_event.name,"mynewsimpleevent")

    #------Oneeventinarecurrence------

    @patch.object(MicrosoftCalendarService,'patch')
    deftest_update_name_of_one_event_of_recurrence_from_flectra(self,mock_patch):
        """
        UpdateoneFlectraeventnamefromarecurrencefromtheorganizercalendar.
        """

        #arrange
        new_name="myspecificeventinrecurrence"
        modified_event_id=4

        #act
        res=self.recurrent_events[modified_event_id].with_user(self.organizer_user).write({
            "recurrence_update":"self_only",
            "name":new_name,
        })
        self.call_post_commit_hooks()
        self.recurrent_events[modified_event_id].invalidate_cache()

        #assert
        self.assertTrue(res)
        mock_patch.assert_called_once_with(
            self.recurrent_events[modified_event_id].ms_organizer_event_id,
            {'seriesMasterId':'REC123','type':'exception',"subject":new_name},
            token=mock_get_token(self.organizer_user),
            timeout=ANY,
        )
        self.assertEqual(self.recurrent_events[modified_event_id].name,new_name)
        self.assertEqual(self.recurrent_events[modified_event_id].follow_recurrence,True)

        foriinrange(self.recurrent_events_count):
            ifi!=modified_event_id:
                self.assertNotEqual(self.recurrent_events[i].name,new_name)

    @patch.object(MicrosoftCalendarService,'patch')
    deftest_update_start_of_one_event_of_recurrence_from_flectra(self,mock_patch):
        """
        UpdateoneFlectraeventstartdatefromarecurrencefromtheorganizercalendar.
        """

        #arrange
        new_date=datetime(2021,9,29,10,0,0)
        modified_event_id=4

        #act
        res=self.recurrent_events[modified_event_id].with_user(self.organizer_user).write({
            "recurrence_update":"self_only",
            "start":new_date.strftime("%Y-%m-%d%H:%M:%S"),
        })
        self.call_post_commit_hooks()
        self.recurrent_events[modified_event_id].invalidate_cache()

        #assert
        self.assertTrue(res)
        mock_patch.assert_called_once_with(
            self.recurrent_events[modified_event_id].ms_organizer_event_id,
            {
                'seriesMasterId':'REC123',
                'type':'exception',
                'start':{
                    'dateTime':pytz.utc.localize(new_date).isoformat(),
                    'timeZone':'Europe/London'
                },
                'end':{
                    'dateTime':pytz.utc.localize(new_date+timedelta(hours=1)).isoformat(),
                    'timeZone':'Europe/London'
                },
                'isAllDay':False
            },
            token=mock_get_token(self.organizer_user),
            timeout=ANY,
        )
        self.assertEqual(self.recurrent_events[modified_event_id].start,new_date)
        self.assertEqual(self.recurrent_events[modified_event_id].follow_recurrence,False)

        foriinrange(self.recurrent_events_count):
            ifi!=modified_event_id:
                self.assertNotEqual(self.recurrent_events[i].start,new_date)
                self.assertEqual(self.recurrent_events[i].follow_recurrence,True)

    @patch.object(MicrosoftCalendarService,'patch')
    deftest_update_start_of_one_event_of_recurrence_from_flectra_with_overlap(self,mock_patch):
        """
        UpdateoneFlectraeventstartdatefromarecurrencefromtheorganizercalendar,inorderto
        overlapanotherexistingevent.
        """
        #arrange
        new_date=datetime(2021,9,27,10,0,0)
        modified_event_id=4

        #act
        withself.assertRaises(UserError):
            self.recurrent_events[modified_event_id].with_user(self.organizer_user).write({
                "recurrence_update":"self_only",
                "start":new_date.strftime("%Y-%m-%d%H:%M:%S"),
            })
            self.call_post_commit_hooks()
            self.recurrent_events.invalidate_cache()

        #assert
        mock_patch.assert_not_called()

    @patch.object(MicrosoftCalendarService,'patch')
    deftest_update_name_of_one_event_of_recurrence_from_flectra_attendee_calendar(self,mock_patch):
        """
        UpdateoneFlectraeventnamefromarecurrencefromtheatendeecalendar.
        """

        #arrange
        new_name="myspecificeventinrecurrence"
        modified_event_id=4

        #act
        res=self.recurrent_events[modified_event_id].with_user(self.attendee_user).write({
            "recurrence_update":"self_only",
            "name":new_name
        })
        self.call_post_commit_hooks()
        self.recurrent_events[modified_event_id].invalidate_cache()

        #assert
        self.assertTrue(res)
        mock_patch.assert_called_once_with(
            self.recurrent_events[modified_event_id].ms_organizer_event_id,
            {'seriesMasterId':'REC123','type':'exception',"subject":new_name},
            token=mock_get_token(self.organizer_user),
            timeout=ANY,
        )
        self.assertEqual(self.recurrent_events[modified_event_id].name,new_name)
        self.assertEqual(self.recurrent_events[modified_event_id].follow_recurrence,True)

    #------Oneandfutureeventsinarecurrence------

    @patch.object(MicrosoftCalendarService,'delete')
    @patch.object(MicrosoftCalendarService,'insert')
    @patch.object(MicrosoftCalendarService,'patch')
    deftest_update_name_of_one_and_future_events_of_recurrence_from_flectra(
        self,mock_patch,mock_insert,mock_delete
    ):
        """
        UpdateaFlectraeventnameandfutureeventsfromarecurrencefromtheorganizercalendar.
        """

        #arrange
        new_name="myspecificeventinrecurrence"
        modified_event_id=4

        #act
        res=self.recurrent_events[modified_event_id].with_user(self.organizer_user).write({
            "recurrence_update":"future_events",
            "name":new_name,
        })
        self.call_post_commit_hooks()
        self.recurrent_events.invalidate_cache()

        #assert
        self.assertTrue(res)
        self.assertEqual(mock_patch.call_count,self.recurrent_events_count-modified_event_id)
        foriinrange(modified_event_id,self.recurrent_events_count):
            mock_patch.assert_any_call(
                self.recurrent_events[i].ms_organizer_event_id,
                {'seriesMasterId':'REC123','type':'exception',"subject":new_name},
                token=mock_get_token(self.organizer_user),
                timeout=ANY,
            )
        foriinrange(modified_event_id,self.recurrent_events_count):
            self.assertEqual(self.recurrent_events[i].name,new_name)
            self.assertEqual(self.recurrent_events[i].follow_recurrence,True)

        foriinrange(modified_event_id):
            self.assertNotEqual(self.recurrent_events[i].name,new_name)

    @patch.object(MicrosoftCalendarService,'delete')
    @patch.object(MicrosoftCalendarService,'insert')
    @patch.object(MicrosoftCalendarService,'patch')
    deftest_update_start_of_one_and_future_events_of_recurrence_from_flectra(
        self,mock_patch,mock_insert,mock_delete
    ):
        """
        UpdateaFlectraeventstartdateandfutureeventsfromarecurrencefromtheorganizercalendar.
        """

        #Whenatime-relatedfieldischanged,theeventdoesnotfollowtherecurrenceschemeanymore.
        #WithOutlook,anotherconstraintisthatthenewstartoftheeventcannotoverlap/crossthestart
        #dateofanothereventoftherecurrence(seemicrosoft_calendar/models/calendar.py
        #_check_recurrence_overlapping()formoreexplanation)
        #
        #Inthiscase,aswealsoupdatefutureevents,therecurrenceshouldbesplittedinto2parts:
        # -theoriginalrecurrenceshouldendjustbeforethefirstupdatedevent
        # -asecondrecurrenceshouldstartatthefirstupdatedevent

        #arrange
        new_date=datetime(2021,9,29,10,0,0)
        modified_event_id=4
        existing_recurrences=self.env["calendar.recurrence"].search([])

        expected_deleted_event_ids=[
            r.ms_organizer_event_id
            fori,rinenumerate(self.recurrent_events)
            ifiinrange(modified_event_id+1,self.recurrent_events_count)
        ]

        #act
        res=self.recurrent_events[modified_event_id].with_user(self.organizer_user).write({
            "recurrence_update":"future_events",
            "start":new_date.strftime("%Y-%m-%d%H:%M:%S"),
        })
        self.call_post_commit_hooks()
        self.recurrent_events.invalidate_cache()

        #assert
        new_recurrences=self.env["calendar.recurrence"].search([])-existing_recurrences

        self.assertTrue(res)

        #anewrecurrenceshouldbecreatedfromthemodifiedeventtotheend
        self.assertEqual(len(new_recurrences),1)
        self.assertEqual(new_recurrences.base_event_id.start,new_date)
        self.assertEqual(len(new_recurrences.calendar_event_ids),self.recurrent_events_count-modified_event_id)

        #futureeventsoftheoldrecurrenceshouldhavebeenremoved
        fore_idinexpected_deleted_event_ids:
            mock_delete.assert_any_call(
                e_id,
                token=mock_get_token(self.organizer_user),
                timeout=ANY,
            )

        #thebaseeventshouldhavebeenmodified
        mock_patch.assert_called_once_with(
            self.recurrent_events[modified_event_id].ms_organizer_event_id,
            {
                'seriesMasterId':'REC123',
                'type':'exception',
                'start':{
                    'dateTime':pytz.utc.localize(new_date).isoformat(),
                    'timeZone':'Europe/London'
                },
                'end':{
                    'dateTime':pytz.utc.localize(new_date+timedelta(hours=1)).isoformat(),
                    'timeZone':'Europe/London'
                },
                'isAllDay':False
            },
            token=mock_get_token(self.organizer_user),
            timeout=ANY,
        )

    @patch.object(MicrosoftCalendarService,'delete')
    @patch.object(MicrosoftCalendarService,'insert')
    @patch.object(MicrosoftCalendarService,'patch')
    deftest_update_start_of_one_and_future_events_of_recurrence_from_flectra_with_overlap(
        self,mock_patch,mock_insert,mock_delete
    ):
        """
        UpdateaFlectraeventstartdateandfutureeventsfromarecurrencefromtheorganizercalendar,
        overlappinganexistingevent.
        """

        #arrange
        new_date=datetime(2021,9,27,10,0,0)
        modified_event_id=4
        existing_recurrences=self.env["calendar.recurrence"].search([])

        expected_deleted_event_ids=[
            r.ms_organizer_event_id
            fori,rinenumerate(self.recurrent_events)
            ifiinrange(modified_event_id+1,self.recurrent_events_count)
        ]

        #asthetestoverlapthepreviouseventoftheupdatedevent,thispreviousevent
        #shouldberemovedtoo
        expected_deleted_event_ids+=[self.recurrent_events[modified_event_id-1].ms_organizer_event_id]

        #act
        res=self.recurrent_events[modified_event_id].with_user(self.organizer_user).write({
            "recurrence_update":"future_events",
            "start":new_date.strftime("%Y-%m-%d%H:%M:%S"),
        })
        self.call_post_commit_hooks()
        self.recurrent_events.invalidate_cache()

        #assert
        new_recurrences=self.env["calendar.recurrence"].search([])-existing_recurrences

        self.assertTrue(res)

        #anewrecurrenceshouldbecreatedfromthemodifiedeventtotheend
        self.assertEqual(len(new_recurrences),1)
        self.assertEqual(new_recurrences.base_event_id.start,new_date)
        self.assertEqual(len(new_recurrences.calendar_event_ids),self.recurrent_events_count-modified_event_id+1)

        #futureeventsoftheoldrecurrenceshouldhavebeenremoved+theoverlappedevent
        fore_idinexpected_deleted_event_ids:
            mock_delete.assert_any_call(
                e_id,
                token=mock_get_token(self.organizer_user),
                timeout=ANY,
            )

        #thebaseeventshouldhavebeenmodified
        mock_patch.assert_called_once_with(
            self.recurrent_events[modified_event_id].ms_organizer_event_id,
            {
                'seriesMasterId':'REC123',
                'type':'exception',
                'start':{
                    'dateTime':pytz.utc.localize(new_date).isoformat(),
                    'timeZone':'Europe/London'
                },
                'end':{
                    'dateTime':pytz.utc.localize(new_date+timedelta(hours=1)).isoformat(),
                    'timeZone':'Europe/London'
                },
                'isAllDay':False
            },
            token=mock_get_token(self.organizer_user),
            timeout=ANY,
        )

    @patch.object(MicrosoftCalendarService,'delete')
    @patch.object(MicrosoftCalendarService,'insert')
    @patch.object(MicrosoftCalendarService,'patch')
    deftest_update_one_and_future_events_of_recurrence_from_flectra_attendee_calendar(
        self,mock_patch,mock_insert,mock_delete
    ):
        """
        UpdateaFlectraeventnameandfutureeventsfromarecurrencefromtheattendeecalendar.
        """

        #arrange
        new_date=datetime(2021,9,29,10,0,0)
        modified_event_id=4
        existing_recurrences=self.env["calendar.recurrence"].search([])

        expected_deleted_event_ids=[
            r.ms_organizer_event_id
            fori,rinenumerate(self.recurrent_events)
            ifiinrange(modified_event_id+1,self.recurrent_events_count)
        ]

        #act
        res=self.recurrent_events[modified_event_id].with_user(self.attendee_user).write({
            "recurrence_update":"future_events",
            "start":new_date.strftime("%Y-%m-%d%H:%M:%S"),
        })
        self.call_post_commit_hooks()
        self.recurrent_events.invalidate_cache()

        #assert
        new_recurrences=self.env["calendar.recurrence"].search([])-existing_recurrences

        self.assertTrue(res)

        #anewrecurrenceshouldbecreatedfromthemodifiedeventtotheend
        self.assertEqual(len(new_recurrences),1)
        self.assertEqual(new_recurrences.base_event_id.start,new_date)
        self.assertEqual(len(new_recurrences.calendar_event_ids),self.recurrent_events_count-modified_event_id)

        #futureeventsoftheoldrecurrenceshouldhavebeenremoved
        fore_idinexpected_deleted_event_ids:
            mock_delete.assert_any_call(
                e_id,
                token=mock_get_token(self.organizer_user),
                timeout=ANY,
            )

        #thebaseeventshouldhavebeenmodified
        mock_patch.assert_called_once_with(
            self.recurrent_events[modified_event_id].ms_organizer_event_id,
            {
                'seriesMasterId':'REC123',
                'type':'exception',
                'start':{
                    'dateTime':pytz.utc.localize(new_date).isoformat(),
                    'timeZone':'Europe/London'
                },
                'end':{
                    'dateTime':pytz.utc.localize(new_date+timedelta(hours=1)).isoformat(),
                    'timeZone':'Europe/London'
                },
                'isAllDay':False
            },
            token=mock_get_token(self.organizer_user),
            timeout=ANY,
        )

    #------Alleventsinarecurrence------

    @patch.object(MicrosoftCalendarService,'delete')
    @patch.object(MicrosoftCalendarService,'insert')
    @patch.object(MicrosoftCalendarService,'patch')
    deftest_update_name_of_all_events_of_recurrence_from_flectra(
        self,mock_patch,mock_insert,mock_delete
    ):
        """
        Updatealleventsnamefromarecurrencefromtheorganizercalendar.
        """

        #arrange
        new_name="myspecificeventinrecurrence"

        #act
        res=self.recurrent_events[0].with_user(self.organizer_user).write({
            "recurrence_update":"all_events",
            "name":new_name,
        })
        self.call_post_commit_hooks()
        self.recurrent_events.invalidate_cache()

        #assert
        self.assertTrue(res)
        self.assertEqual(mock_patch.call_count,self.recurrent_events_count)
        foriinrange(self.recurrent_events_count):
            mock_patch.assert_any_call(
                self.recurrent_events[i].ms_organizer_event_id,
                {'seriesMasterId':'REC123','type':'exception',"subject":new_name},
                token=mock_get_token(self.organizer_user),
                timeout=ANY,
            )
            self.assertEqual(self.recurrent_events[i].name,new_name)
            self.assertEqual(self.recurrent_events[i].follow_recurrence,True)

    @patch.object(MicrosoftCalendarService,'delete')
    @patch.object(MicrosoftCalendarService,'insert')
    @patch.object(MicrosoftCalendarService,'patch')
    deftest_update_start_of_all_events_of_recurrence_from_flectra(
        self,mock_patch,mock_insert,mock_delete
    ):
        """
        Updatealleventsstartdatefromarecurrencefromtheorganizercalendar.
        """

        #arrange
        new_date=datetime(2021,9,25,10,0,0)

        #act
        withself.assertRaises(UserError):
            self.recurrent_events[0].with_user(self.organizer_user).write({
                "recurrence_update":"all_events",
                "start":new_date.strftime("%Y-%m-%d%H:%M:%S"),
            })
            self.call_post_commit_hooks()
            self.recurrent_events.invalidate_cache()

    @patch.object(MicrosoftCalendarService,'delete')
    @patch.object(MicrosoftCalendarService,'insert')
    @patch.object(MicrosoftCalendarService,'patch')
    deftest_update_all_events_of_recurrence_from_flectra_attendee_calendar(
        self,mock_patch,mock_insert,mock_delete
    ):
        """
        Updatealleventsstartdatefromarecurrencefromtheattendeecalendarshouldraiseanerror.
        """

        #arrange
        new_date=datetime(2021,9,25,10,0,0)

        #act
        withself.assertRaises(UserError):
            self.recurrent_events[0].with_user(self.attendee_user).write({
                "recurrence_update":"all_events",
                "start":new_date.strftime("%Y-%m-%d%H:%M:%S"),
            })
            self.call_post_commit_hooks()
            self.recurrent_events.invalidate_cache()

    #-------------------------------------------------------------------------------
    #UpdatefromOutlooktoFlectra
    #-------------------------------------------------------------------------------

    @patch.object(MicrosoftCalendarService,'get_events')
    deftest_update_simple_event_from_outlook_organizer_calendar(self,mock_get_events):
        """
        UpdateasimpleeventfromOutlookorganizercalendar.
        """

        #arrange
        new_name="updatesimpleevent"
        mock_get_events.return_value=(
            MicrosoftEvent([dict(
                self.simple_event_from_outlook_organizer,
                subject=new_name,
                type="exception",
                lastModifiedDateTime=_modified_date_in_the_future(self.simple_event)
            )]),None
        )

        #act
        self.organizer_user.with_user(self.organizer_user).sudo()._sync_microsoft_calendar()

        #assert
        self.assertEqual(self.simple_event.name,new_name)
        self.assertEqual(self.simple_event.follow_recurrence,False)

    @patch.object(MicrosoftCalendarService,'get_events')
    deftest_update_simple_event_from_outlook_attendee_calendar(self,mock_get_events):
        """
        UpdateasimpleeventfromOutlookattendeecalendar.
        """

        #arrange
        new_name="updatesimpleevent"
        mock_get_events.return_value=(
            MicrosoftEvent([dict(
                dict(self.simple_event_from_outlook_organizer,id=789), #sameiCalUIdbutdifferentid
                subject=new_name,
                type="exception",
                lastModifiedDateTime=_modified_date_in_the_future(self.simple_event)
            )]),None
        )

        #act
        self.attendee_user.with_user(self.attendee_user).sudo()._sync_microsoft_calendar()

        #assert
        self.assertEqual(self.simple_event.name,new_name)
        self.assertEqual(self.simple_event.follow_recurrence,False)

    @patch.object(MicrosoftCalendarService,'get_events')
    deftest_update_name_of_one_event_of_recurrence_from_outlook_organizer_calendar(self,mock_get_events):
        """
        UpdateoneeventnamefromarecurrencefromOutlookorganizercalendar.
        """

        #arrange
        new_name="anothereventname"
        from_event_index=2
        events=self.recurrent_event_from_outlook_organizer
        events[from_event_index]=dict(
            events[from_event_index],
            subject=new_name,
            type="exception",
            lastModifiedDateTime=_modified_date_in_the_future(self.simple_event)
        )
        ms_event_id=events[from_event_index]['id']
        mock_get_events.return_value=(MicrosoftEvent(events),None)

        #act
        self.organizer_user.with_user(self.organizer_user).sudo()._sync_microsoft_calendar()

        #assert
        updated_event=self.env["calendar.event"].search([('ms_organizer_event_id','=',ms_event_id)])
        self.assertEqual(updated_event.name,new_name)
        self.assertEqual(updated_event.follow_recurrence,False)

    @patch.object(MicrosoftCalendarService,'get_events')
    deftest_update_start_of_one_event_of_recurrence_from_outlook_organizer_calendar(self,mock_get_events):
        """
        UpdateoneeventstartdatefromarecurrencefromOutlookorganizercalendar.
        """

        #arrange
        new_date=datetime(2021,9,25,10,0,0)
        from_event_index=3
        events=self.recurrent_event_from_outlook_organizer
        events[from_event_index]=dict(
            events[from_event_index],
            start={'dateTime':new_date.strftime("%Y-%m-%dT%H:%M:%S.0000000"),'timeZone':'UTC'},
            type="exception",
            lastModifiedDateTime=_modified_date_in_the_future(self.recurrent_base_event)
        )
        ms_event_id=events[from_event_index]['id']
        mock_get_events.return_value=(MicrosoftEvent(events),None)

        #act
        self.organizer_user.with_user(self.organizer_user).sudo()._sync_microsoft_calendar()

        #assert
        updated_event=self.env["calendar.event"].search([('ms_organizer_event_id','=',ms_event_id)])
        self.assertEqual(updated_event.start,new_date)
        self.assertEqual(updated_event.follow_recurrence,False)

    @patch.object(MicrosoftCalendarService,'get_events')
    deftest_update_start_of_one_event_of_recurrence_from_outlook_organizer_calendar_with_overlap(
        self,mock_get_events
    ):
        """
        UpdateoneeventstartdatefromarecurrencefromOutlookorganizercalendar,witheventoverlap.
        """

        #arrange
        new_date=datetime(2021,9,23,10,0,0)
        from_event_index=3
        events=self.recurrent_event_from_outlook_organizer
        events[from_event_index]=dict(
            events[from_event_index],
            start={'dateTime':new_date.strftime("%Y-%m-%dT%H:%M:%S.0000000"),'timeZone':'UTC'},
            type="exception",
            lastModifiedDateTime=_modified_date_in_the_future(self.recurrent_base_event)
        )
        ms_event_id=events[from_event_index]['id']
        mock_get_events.return_value=(MicrosoftEvent(events),None)

        #act
        self.organizer_user.with_user(self.organizer_user).sudo()._sync_microsoft_calendar()

        #assert
        updated_event=self.env["calendar.event"].search([('ms_organizer_event_id','=',ms_event_id)])
        self.assertEqual(updated_event.start,new_date)
        self.assertEqual(updated_event.follow_recurrence,False)

    @patch.object(MicrosoftCalendarService,'get_events')
    deftest_update_name_of_one_event_and_future_of_recurrence_from_outlook_organizer_calendar(self,mock_get_events):
        """
        UpdateoneeventnameandfutureeventsfromarecurrencefromOutlookorganizercalendar.
        """

        #arrange
        new_name="anothereventname"
        from_event_index=3
        events=self.recurrent_event_from_outlook_organizer
        foriinrange(from_event_index,len(events)):
            events[i]=dict(
                events[i],
                subject=f"{new_name}_{i}",
                type="exception",
                lastModifiedDateTime=_modified_date_in_the_future(self.recurrent_base_event)
            )
        ms_event_ids={
            events[i]['id']:events[i]['subject']foriinrange(from_event_index,len(events))
        }
        mock_get_events.return_value=(MicrosoftEvent(events),None)

        #act
        self.organizer_user.with_user(self.organizer_user).sudo()._sync_microsoft_calendar()

        #assert
        updated_events=self.env["calendar.event"].search([
            ('ms_organizer_event_id','in',tuple(ms_event_ids.keys()))
        ])
        foreinupdated_events:
            self.assertEqual(e.name,ms_event_ids[e.ms_organizer_event_id])

    @patch.object(MicrosoftCalendarService,'get_events')
    deftest_update_start_of_one_event_and_future_of_recurrence_from_outlook_organizer_calendar(self,mock_get_events):
        """
        UpdateoneeventstartdateandfutureeventsfromarecurrencefromOutlookorganizercalendar.

        Whenatimefieldismodifiedonaneventandthefutureeventsoftherecurrence,therecurrenceissplitted:
        -thefirstoneisstillthesamethantheexistingone,butstopsatthefirstmodifiedevent,
        -thesecondonecontainingnewlycreatedeventsbutbasedontheoldeventswhichhavebeendeleted.
        """

        #-----------ARRANGE--------------

        existing_events=self.env["calendar.event"].search([])
        existing_recurrences=self.env["calendar.recurrence"].search([])

        #eventindexfromwherethecurrentrecurrencewillbesplitted/modified
        from_event_index=3

        #numberofeventsinbothrecurrences
        old_recurrence_event_count=from_event_index-1
        new_recurrence_event_count=len(self.recurrent_event_from_outlook_organizer)-from_event_index

        #datesforthenewrecurrences(shifteventdatesof1dayinthepast)
        new_rec_first_event_start_date=self.start_date+timedelta(
            days=self.recurrent_event_interval*old_recurrence_event_count-1
        )
        new_rec_first_event_end_date=new_rec_first_event_start_date+timedelta(hours=1)
        new_rec_end_date=new_rec_first_event_end_date+timedelta(
            days=self.recurrent_event_interval*new_recurrence_event_count-1
        )

        #preparefirstrecurrencedatainreceivedOutlookevents
        events=self.recurrent_event_from_outlook_organizer[0:from_event_index]
        events[0]['lastModifiedDateTime']=_modified_date_in_the_future(self.recurrent_base_event)
        events[0]['recurrence']['range']['endDate']=(
            self.recurrence_end_date-timedelta(days=self.recurrent_event_interval*new_recurrence_event_count)
        ).strftime("%Y-%m-%d")

        #preparesecondrecurrencedatainreceivedOutlookevents
        events+=[
            dict(
                self.recurrent_event_from_outlook_organizer[0],
                start={
                    'dateTime':new_rec_first_event_start_date.strftime("%Y-%m-%dT%H:%M:%S.0000000"),
                    'timeZone':'UTC'
                },
                end={
                    'dateTime':new_rec_first_event_end_date.strftime("%Y-%m-%dT%H:%M:%S.0000000"),
                    'timeZone':'UTC'
                },
                id='REC123_new',
                iCalUId='REC456_new',
                recurrence=dict(
                    self.recurrent_event_from_outlook_organizer[0]['recurrence'],
                    range={
                        'startDate':new_rec_first_event_start_date.strftime("%Y-%m-%d"),
                        'endDate':new_rec_end_date.strftime("%Y-%m-%d"),
                        'numberOfOccurrences':0,
                        'recurrenceTimeZone':'RomanceStandardTime',
                        'type':'endDate'
                    }
                )
            )
        ]
        #...andtherecurrentevents
        events+=[
            dict(
                self.recurrent_event_from_outlook_organizer[1],
                start={
                    'dateTime':(
                        new_rec_first_event_start_date+timedelta(days=i*self.recurrent_event_interval)
                    ).strftime("%Y-%m-%dT%H:%M:%S.0000000"),
                    'timeZone':'UTC'
                },
                end={
                    'dateTime':(
                        new_rec_first_event_end_date+timedelta(days=i*self.recurrent_event_interval)
                    ).strftime("%Y-%m-%dT%H:%M:%S.0000000"),
                    'timeZone':'UTC'
                },
                id=f'REC123_new_{i+1}',
                iCalUId=f'REC456_new_{i+1}',
                seriesMasterId='REC123_new',
            )
            foriinrange(0,new_recurrence_event_count)
        ]
        mock_get_events.return_value=(MicrosoftEvent(events),None)

        #-----------ACT--------------

        self.organizer_user.with_user(self.organizer_user).sudo()._sync_microsoft_calendar()

        #-----------ASSERT--------------

        new_events=self.env["calendar.event"].search([])-existing_events
        new_recurrences=self.env["calendar.recurrence"].search([])-existing_recurrences

        #oldrecurrence
        self.assertEqual(len(self.recurrence.calendar_event_ids),2)
        self.assertEqual(
            self.recurrence.until,
            self.recurrence_end_date.date()-timedelta(days=self.recurrent_event_interval*new_recurrence_event_count)
        )

        #newrecurrence
        self.assertEqual(len(new_recurrences),1)
        self.assertEqual(len(new_events),new_recurrence_event_count)
        self.assertEqual(new_recurrences.ms_organizer_event_id,"REC123_new")
        self.assertEqual(new_recurrences.ms_universal_event_id,"REC456_new")

        fori,einenumerate(sorted(new_events,key=lambdae:e.id)):
            self.assert_flectra_event(e,{
                "start":new_rec_first_event_start_date+timedelta(days=i*self.recurrent_event_interval),
                "stop":new_rec_first_event_end_date+timedelta(days=i*self.recurrent_event_interval),
                "microsoft_id":combine_ids(f'REC123_new_{i+1}',f'REC456_new_{i+1}'),
                "recurrence_id":new_recurrences,
                "follow_recurrence":True,
            })

    @patch.object(MicrosoftCalendarService,'get_events')
    deftest_update_start_of_one_event_and_future_of_recurrence_from_outlook_organizer_calendar_with_overlap(
        self,mock_get_events
    ):
        """
        UpdateoneeventstartdateandfutureeventsfromarecurrencefromOutlookorganizercalendar,
        overlappinganexistingevent.
        """

        #-----------ARRANGE--------------

        existing_events=self.env["calendar.event"].search([])
        existing_recurrences=self.env["calendar.recurrence"].search([])

        #eventindexfromwherethecurrentrecurrencewillbesplitted/modified
        from_event_index=3

        #numberofeventsinbothrecurrences
        old_recurrence_event_count=from_event_index-1
        new_recurrence_event_count=len(self.recurrent_event_from_outlook_organizer)-from_event_index

        #datesforthenewrecurrences(shifteventdatesof(recurrent_event_interval+1)daysinthepast
        #tooverlapanevent.
        new_rec_first_event_start_date=self.start_date+timedelta(
            days=self.recurrent_event_interval*(old_recurrence_event_count-1)-1
        )
        new_rec_first_event_end_date=new_rec_first_event_start_date+timedelta(hours=1)
        new_rec_end_date=new_rec_first_event_end_date+timedelta(
            days=self.recurrent_event_interval*(new_recurrence_event_count-1)-1
        )

        #preparefirstrecurrencedatainreceivedOutlookevents
        events=self.recurrent_event_from_outlook_organizer[0:from_event_index]
        events[0]['lastModifiedDateTime']=_modified_date_in_the_future(self.recurrent_base_event)
        events[0]['recurrence']['range']['endDate']=(
            self.recurrence_end_date-timedelta(days=self.recurrent_event_interval*new_recurrence_event_count)
        ).strftime("%Y-%m-%d")

        #preparesecondrecurrencedatainreceivedOutlookevents
        events+=[
            dict(
                self.recurrent_event_from_outlook_organizer[0],
                start={
                    'dateTime':new_rec_first_event_start_date.strftime("%Y-%m-%dT%H:%M:%S.0000000"),
                    'timeZone':'UTC'
                },
                end={
                    'dateTime':new_rec_first_event_end_date.strftime("%Y-%m-%dT%H:%M:%S.0000000"),
                    'timeZone':'UTC'
                },
                id='REC123_new',
                iCalUId='REC456_new',
                recurrence=dict(
                    self.recurrent_event_from_outlook_organizer[0]['recurrence'],
                    range={
                        'startDate':new_rec_first_event_start_date.strftime("%Y-%m-%d"),
                        'endDate':new_rec_end_date.strftime("%Y-%m-%d"),
                        'numberOfOccurrences':0,
                        'recurrenceTimeZone':'RomanceStandardTime',
                        'type':'endDate'
                    }
                )
            )
        ]
        #...andtherecurrentevents
        events+=[
            dict(
                self.recurrent_event_from_outlook_organizer[1],
                start={
                    'dateTime':(
                        new_rec_first_event_start_date+timedelta(days=i*self.recurrent_event_interval)
                    ).strftime("%Y-%m-%dT%H:%M:%S.0000000"),
                    'timeZone':'UTC'
                },
                end={
                    'dateTime':(
                        new_rec_first_event_end_date+timedelta(days=i*self.recurrent_event_interval)
                    ).strftime("%Y-%m-%dT%H:%M:%S.0000000"),
                    'timeZone':'UTC'
                },
                id=f'REC123_new_{i+1}',
                iCalUId=f'REC456_new_{i+1}',
                seriesMasterId='REC123_new',
            )
            foriinrange(0,new_recurrence_event_count)
        ]
        mock_get_events.return_value=(MicrosoftEvent(events),None)

        #-----------ACT--------------

        self.organizer_user.with_user(self.organizer_user).sudo()._sync_microsoft_calendar()

        #-----------ASSERT--------------

        new_events=self.env["calendar.event"].search([])-existing_events
        new_recurrences=self.env["calendar.recurrence"].search([])-existing_recurrences

        #oldrecurrence
        self.assertEqual(len(self.recurrence.calendar_event_ids),2)
        self.assertEqual(
            self.recurrence.until,
            self.recurrence_end_date.date()-timedelta(days=self.recurrent_event_interval*new_recurrence_event_count)
        )

        #newrecurrence
        self.assertEqual(len(new_recurrences),1)
        self.assertEqual(len(new_events),new_recurrence_event_count)
        self.assertEqual(new_recurrences.ms_organizer_event_id,"REC123_new")
        self.assertEqual(new_recurrences.ms_universal_event_id,"REC456_new")

        fori,einenumerate(sorted(new_events,key=lambdae:e.id)):
            self.assert_flectra_event(e,{
                "start":new_rec_first_event_start_date+timedelta(days=i*self.recurrent_event_interval),
                "stop":new_rec_first_event_end_date+timedelta(days=i*self.recurrent_event_interval),
                "microsoft_id":combine_ids(f'REC123_new_{i+1}',f'REC456_new_{i+1}'),
                "recurrence_id":new_recurrences,
                "follow_recurrence":True,
            })

    @patch.object(MicrosoftCalendarService,'get_events')
    deftest_update_name_of_all_events_of_recurrence_from_outlook_organizer_calendar(self,mock_get_events):
        """
        UpdatealleventnamesofarecurrencefromOutlookorganizercalendar.
        """

        #arrange
        new_name="anothereventname"
        events=self.recurrent_event_from_outlook_organizer
        fori,einenumerate(events):
            events[i]=dict(
                e,
                subject=f"{new_name}_{i}",
                lastModifiedDateTime=_modified_date_in_the_future(self.recurrent_base_event)
            )
        ms_events_to_update={
            events[i]['id']:events[i]['subject']foriinrange(1,len(events))
        }
        mock_get_events.return_value=(MicrosoftEvent(events),None)

        #act
        self.organizer_user.with_user(self.organizer_user).sudo()._sync_microsoft_calendar()

        #assert
        updated_events=self.env["calendar.event"].search([
            ('ms_organizer_event_id','in',tuple(ms_events_to_update.keys()))
        ])
        foreinupdated_events:
            self.assertEqual(e.name,ms_events_to_update[e.ms_organizer_event_id])
            self.assertEqual(e.follow_recurrence,True)

    def_prepare_outlook_events_for_all_events_start_date_update(self,nb_of_events):
        """
        Utilitymethodtoavoidrepeatingdatapreparationforalltests
        aboutupdatingthestartdateofalleventsofarecurrence
        """
        new_start_date=datetime(2021,9,21,10,0,0)
        new_end_date=new_start_date+timedelta(hours=1)

        #preparerecurrencebasedonself.recurrent_event_from_outlook_organizer[0]whichistheOutlookrecurrence
        events=[dict(
            self.recurrent_event_from_outlook_organizer[0],
            start={
                'dateTime':new_start_date.strftime("%Y-%m-%dT%H:%M:%S.0000000"),
                'timeZone':'UTC'
            },
            end={
                'dateTime':new_end_date.strftime("%Y-%m-%dT%H:%M:%S.0000000"),
                'timeZone':'UTC',
            },
            recurrence=dict(
                self.recurrent_event_from_outlook_organizer[0]['recurrence'],
                range={
                    'startDate':new_start_date.strftime("%Y-%m-%d"),
                    'endDate':(
                        new_end_date+timedelta(days=self.recurrent_event_interval*nb_of_events)
                    ).strftime("%Y-%m-%d"),
                    'numberOfOccurrences':0,
                    'recurrenceTimeZone':'RomanceStandardTime',
                    'type':'endDate'
                }
            ),
            lastModifiedDateTime=_modified_date_in_the_future(self.recurrent_base_event)
        )]

        #preparealleventsbasedonself.recurrent_event_from_outlook_organizer[1]whichisthefirstOutlookevent
        events+=nb_of_events*[self.recurrent_event_from_outlook_organizer[1]]
        foriinrange(1,nb_of_events+1):
            events[i]=dict(
                events[i],
                id=f'REC123_EVENT_{i}',
                iCalUId=f'REC456_EVENT_{i}',
                start={
                    'dateTime':(
                        new_start_date+timedelta(days=(i-1)*self.recurrent_event_interval)
                    ).strftime("%Y-%m-%dT%H:%M:%S.0000000"),
                    'timeZone':'UTC',
                },
                end={
                    'dateTime':(
                        new_end_date+timedelta(days=(i-1)*self.recurrent_event_interval)
                    ).strftime("%Y-%m-%dT%H:%M:%S.0000000"),
                    'timeZone':'UTC',
                },
                lastModifiedDateTime=_modified_date_in_the_future(self.recurrent_base_event)
            )

        returnevents

    @patch.object(MicrosoftCalendarService,'get_events')
    deftest_update_start_of_all_events_of_recurrence_from_outlook_organizer_calendar(self,mock_get_events):
        """
        UpdatealleventstartdateofarecurrencefromOutlookorganizercalendar.
        """

        #-----------ARRANGE-----------
        events=self._prepare_outlook_events_for_all_events_start_date_update(self.recurrent_events_count)
        ms_events_to_update={
            events[i]['id']:events[i]['start']foriinrange(1,self.recurrent_events_count+1)
        }
        mock_get_events.return_value=(MicrosoftEvent(events),None)

        #-----------ACT-----------

        self.organizer_user.with_user(self.organizer_user).sudo()._sync_microsoft_calendar()

        #-----------ASSERT-----------

        updated_events=self.env["calendar.event"].search([
            ('ms_organizer_event_id','in',tuple(ms_events_to_update.keys()))
        ])
        foreinupdated_events:
            self.assertEqual(
                e.start.strftime("%Y-%m-%dT%H:%M:%S.0000000"),
                ms_events_to_update[e.ms_organizer_event_id]["dateTime"]
            )

    @patch.object(MicrosoftCalendarService,'get_events')
    deftest_update_start_of_all_events_of_recurrence_with_more_events(self,mock_get_events):
        """
        UpdatealleventstartdateofarecurrencefromOutlookorganizercalendar,where
        moreeventshavebeenadded(theenddateislaterintheyear)
        """
        #-----------ARRANGE-----------

        nb_of_events=self.recurrent_events_count+2
        events=self._prepare_outlook_events_for_all_events_start_date_update(nb_of_events)
        ms_events_to_update={
            events[i]['id']:events[i]['start']foriinrange(1,nb_of_events+1)
        }
        mock_get_events.return_value=(MicrosoftEvent(events),None)

        #-----------ACT-----------

        self.organizer_user.with_user(self.organizer_user).sudo()._sync_microsoft_calendar()

        #-----------ASSERT-----------

        updated_events=self.env["calendar.event"].search([
            ('ms_organizer_event_id','in',tuple(ms_events_to_update.keys()))
        ])
        foreinupdated_events:
            self.assertEqual(
                e.start.strftime("%Y-%m-%dT%H:%M:%S.0000000"),
                ms_events_to_update[e.ms_organizer_event_id]["dateTime"]
            )

    @patch.object(MicrosoftCalendarService,'get_events')
    deftest_update_start_of_all_events_of_recurrence_with_less_events(self,mock_get_events):
        """
        UpdatealleventstartdateofarecurrencefromOutlookorganizercalendar,where
        someeventshavebeenremoved(theenddateisearlierintheyear)
        """
        #-----------ARRANGE-----------

        nb_of_events=self.recurrent_events_count-2
        events=self._prepare_outlook_events_for_all_events_start_date_update(nb_of_events)
        ms_events_to_update={
            events[i]['id']:events[i]['start']foriinrange(1,nb_of_events+1)
        }
        mock_get_events.return_value=(MicrosoftEvent(events),None)

        #-----------ACT-----------

        self.organizer_user.with_user(self.organizer_user).sudo()._sync_microsoft_calendar()

        #-----------ASSERT-----------

        updated_events=self.env["calendar.event"].search([
            ('ms_organizer_event_id','in',tuple(ms_events_to_update.keys()))
        ])
        foreinupdated_events:
            self.assertEqual(
                e.start.strftime("%Y-%m-%dT%H:%M:%S.0000000"),
                ms_events_to_update[e.ms_organizer_event_id]["dateTime"]
            )

    @patch.object(MicrosoftCalendarService,'get_events')
    deftest_update_start_of_all_events_of_recurrence_with_exceptions(self,mock_get_events):
        """
        UpdatealleventstartdateofarecurrencefromOutlookorganizercalendar,where
        aneventdoesnotfollowtherecurrenceanymore(itbecameanexception)
        """
        #-----------ARRANGE-----------

        nb_of_events=self.recurrent_events_count-2
        events=self._prepare_outlook_events_for_all_events_start_date_update(nb_of_events)

        new_start_date=parse(events[2]['start']['dateTime'])+timedelta(days=1)
        new_end_date=parse(events[2]['end']['dateTime'])+timedelta(days=1)
        events[2]=dict(
            events[2],
            start={
                'dateTime':new_start_date.strftime("%Y-%m-%dT%H:%M:%S.0000000"),
                'timeZone':'UTC',
            },
            end={
                'dateTime':new_end_date.strftime("%Y-%m-%dT%H:%M:%S.0000000"),
                'timeZone':'UTC',
            },
            type="exception",
        )
        ms_events_to_update={
            events[i]['id']:events[i]['start']foriinrange(1,nb_of_events+1)
        }
        mock_get_events.return_value=(MicrosoftEvent(events),None)

        #-----------ACT-----------

        self.organizer_user.with_user(self.organizer_user).sudo()._sync_microsoft_calendar()

        #-----------ASSERT-----------

        updated_events=self.env["calendar.event"].search([
            ('ms_organizer_event_id','in',tuple(ms_events_to_update.keys()))
        ])
        foreinupdated_events:
            self.assertEqual(
                e.start.strftime("%Y-%m-%dT%H:%M:%S.0000000"),
                ms_events_to_update[e.ms_organizer_event_id]["dateTime"]
            )
