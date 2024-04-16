#-*-coding:utf-8-*-
fromunittest.mockimportpatch,ANY,call

fromflectra.addons.microsoft_calendar.utils.microsoft_calendarimportMicrosoftCalendarService
fromflectra.addons.microsoft_calendar.utils.microsoft_eventimportMicrosoftEvent
fromflectra.addons.microsoft_calendar.models.res_usersimportUser
fromflectra.addons.microsoft_calendar.tests.commonimport(
    TestCommon,
    mock_get_token,
    _modified_date_in_the_future,
    patch_api
)

@patch.object(User,'_get_microsoft_calendar_token',mock_get_token)
classTestDeleteEvents(TestCommon):

    @patch_api
    defsetUp(self):
        super(TestDeleteEvents,self).setUp()
        self.create_events_for_tests()

    @patch.object(MicrosoftCalendarService,'delete')
    deftest_delete_simple_event_from_flectra_organizer_calendar(self,mock_delete):
        event_id=self.simple_event.ms_organizer_event_id

        self.simple_event.with_user(self.organizer_user).unlink()
        self.call_post_commit_hooks()
        self.simple_event.invalidate_cache()

        self.assertFalse(self.simple_event.exists())
        mock_delete.assert_called_once_with(
            event_id,
            token=mock_get_token(self.organizer_user),
            timeout=ANY
        )

    @patch.object(MicrosoftCalendarService,'delete')
    deftest_delete_simple_event_from_flectra_attendee_calendar(self,mock_delete):
        event_id=self.simple_event.ms_organizer_event_id

        self.simple_event.with_user(self.attendee_user).unlink()
        self.call_post_commit_hooks()
        self.simple_event.invalidate_cache()

        self.assertFalse(self.simple_event.exists())
        mock_delete.assert_called_once_with(
            event_id,
            token=mock_get_token(self.organizer_user),
            timeout=ANY
        )

    @patch.object(MicrosoftCalendarService,'delete')
    deftest_archive_simple_event_from_flectra_organizer_calendar(self,mock_delete):
        event_id=self.simple_event.ms_organizer_event_id

        self.simple_event.with_user(self.organizer_user).write({'active':False})
        self.call_post_commit_hooks()
        self.simple_event.invalidate_cache()

        self.assertTrue(self.simple_event.exists())
        self.assertFalse(self.simple_event.active)
        mock_delete.assert_called_once_with(
            event_id,
            token=mock_get_token(self.organizer_user),
            timeout=ANY
        )

    @patch.object(MicrosoftCalendarService,'delete')
    deftest_archive_simple_event_from_flectra_attendee_calendar(self,mock_delete):
        event_id=self.simple_event.ms_organizer_event_id

        self.simple_event.with_user(self.attendee_user).write({'active':False})
        self.call_post_commit_hooks()
        self.simple_event.invalidate_cache()

        self.assertTrue(self.simple_event.exists())
        self.assertFalse(self.simple_event.active)
        mock_delete.assert_called_once_with(
            event_id,
            token=mock_get_token(self.organizer_user),
            timeout=ANY
        )

    @patch.object(MicrosoftCalendarService,'delete')
    deftest_archive_several_events_at_once(self,mock_delete):
        """
        Archiveseveraleventsatonceshouldnotproduceanyexception.
        """
        #act
        self.several_events.action_archive()
        self.call_post_commit_hooks()
        self.several_events.invalidate_cache()

        #assert
        self.assertFalse(all(e.activeforeinself.several_events))

        mock_delete.assert_has_calls([
            call(e.ms_organizer_event_id,token=ANY,timeout=ANY)
            foreinself.several_events
        ])

    @patch.object(MicrosoftCalendarService,'get_events')
    deftest_cancel_simple_event_from_outlook_organizer_calendar(self,mock_get_events):
        """
        InhisOutlookcalendar,theorganizercannotdeletetheevent,hecanonlycancelit.
        """
        event_id=self.simple_event.ms_organizer_event_id
        mock_get_events.return_value=(
            MicrosoftEvent([{
                "id":event_id,
                "@removed":{"reason":"deleted"}
            }]),
            None
        )
        self.organizer_user.with_user(self.organizer_user).sudo()._sync_microsoft_calendar()
        self.assertFalse(self.simple_event.exists())

    deftest_delete_simple_event_from_outlook_attendee_calendar(self):
        """
        IfanattendeedeletesaneventfromitsOutlookcalendar,duringthesync,Flectrawillbenotifiedthat
        thiseventhasbeendeletedBUTonlywiththeattendees'scalendareventidandnotwiththeglobalone
        (callediCalUId).Thatmeans,it'snotpossibletomatchthisdeletedeventwithanFlectraevent.

        LIMITATION:

        Unfortunately,thereisnomagicsolution:
            1)keepthelistofcalendareventsidslinkedtoauniqueiCalUIdbutallFlectrausersmaynothavesynced
            theirFlectracalendar,leadingtomissingidsinthelist=>badsolution.
            2)callthemicrosoftAPItogettheiCalUIdmatchingthereceivedeventid=>astheeventhasalready
            beendeleted,thiscallmayreturnanerror.
        """

    @patch.object(MicrosoftCalendarService,'delete')
    deftest_delete_one_event_from_recurrence_from_flectra_calendar(self,mock_delete):

        #arrange
        idx=2
        event_id=self.recurrent_events[idx].ms_organizer_event_id

        #act
        self.recurrent_events[idx].with_user(self.organizer_user).unlink()
        self.call_post_commit_hooks()

        #assert
        self.assertFalse(self.recurrent_events[idx].exists())
        self.assertEqual(len(self.recurrence.calendar_event_ids),self.recurrent_events_count-1)
        mock_delete.assert_called_once_with(
            event_id,
            token=mock_get_token(self.organizer_user),
            timeout=ANY
        )

    @patch.object(MicrosoftCalendarService,'delete')
    deftest_delete_first_event_from_recurrence_from_flectra_calendar(self,mock_delete):

        #arrange
        idx=0
        event_id=self.recurrent_events[idx].ms_organizer_event_id

        #act
        self.recurrent_events[idx].with_user(self.organizer_user).unlink()
        self.call_post_commit_hooks()

        #assert
        self.assertFalse(self.recurrent_events[idx].exists())
        self.assertEqual(len(self.recurrence.calendar_event_ids),self.recurrent_events_count-1)
        self.assertEqual(self.recurrence.base_event_id,self.recurrent_events[1])
        mock_delete.assert_called_once_with(
            event_id,
            token=mock_get_token(self.organizer_user),
            timeout=ANY
        )

    @patch.object(MicrosoftCalendarService,'get_events')
    deftest_delete_one_event_from_recurrence_from_outlook_calendar(self,mock_get_events):
        """
        Whenasingleeventisremovedfromarecurrence,Outlookreturnstherecurrenceand
        eventswhichstillexist.
        """
        #arrange
        idx=3
        rec_values=[
            dict(
                event,
                lastModifiedDateTime=_modified_date_in_the_future(self.recurrence)
            )
            fori,eventinenumerate(self.recurrent_event_from_outlook_organizer)
            ifi!=(idx+1) #+1becauserecurrent_event_from_outlook_organizercontainstherecurrenceitselfasfirstitem
        ]
        event_to_remove=self.recurrent_events[idx]
        mock_get_events.return_value=(MicrosoftEvent(rec_values),None)

        #act
        self.organizer_user.with_user(self.organizer_user).sudo()._sync_microsoft_calendar()

        #assert
        self.assertFalse(event_to_remove.exists())
        self.assertEqual(len(self.recurrence.calendar_event_ids),self.recurrent_events_count-1)

    @patch.object(MicrosoftCalendarService,'get_events')
    deftest_delete_first_event_from_recurrence_from_outlook_calendar(self,mock_get_events):

        #arrange
        rec_values=[
            dict(
                event,
                lastModifiedDateTime=_modified_date_in_the_future(self.recurrence)
            )
            fori,eventinenumerate(self.recurrent_event_from_outlook_organizer)
            ifi!=1
        ]
        event_to_remove=self.recurrent_events[0]
        next_base_event=self.recurrent_events[1]
        mock_get_events.return_value=(MicrosoftEvent(rec_values),None)

        #act
        self.organizer_user.with_user(self.organizer_user).sudo()._sync_microsoft_calendar()

        #assert
        self.assertFalse(event_to_remove.exists())
        self.assertEqual(len(self.recurrence.calendar_event_ids),self.recurrent_events_count-1)
        self.assertEqual(self.recurrence.base_event_id,next_base_event)

    @patch.object(MicrosoftCalendarService,'get_events')
    deftest_delete_one_event_and_future_from_recurrence_from_outlook_calendar(self,mock_get_events):
        #arrange
        idx=range(4,self.recurrent_events_count)
        rec_values=[
            dict(
                event,
                lastModifiedDateTime=_modified_date_in_the_future(self.recurrence)
            )
            fori,eventinenumerate(self.recurrent_event_from_outlook_organizer)
            ifinotin[x+1forxinidx]
        ]
        event_to_remove=[efori,einenumerate(self.recurrent_events)ifiinidx]
        mock_get_events.return_value=(MicrosoftEvent(rec_values),None)

        #act
        self.organizer_user.with_user(self.organizer_user).sudo()._sync_microsoft_calendar()

        #assert
        foreinevent_to_remove:
            self.assertFalse(e.exists())
        self.assertEqual(len(self.recurrence.calendar_event_ids),self.recurrent_events_count-len(idx))

    @patch.object(MicrosoftCalendarService,'get_events')
    deftest_delete_first_event_and_future_from_recurrence_from_outlook_calendar(self,mock_get_events):
        """
        InOutlook,deletingthefirsteventandfutureonesisthesamethanremovingalltherecurrence.
        """
        #arrange
        mock_get_events.return_value=(
            MicrosoftEvent([{
                "id":self.recurrence.ms_organizer_event_id,
                "@removed":{"reason":"deleted"}
            }]),
            None
        )

        #act
        self.organizer_user.with_user(self.organizer_user).sudo()._sync_microsoft_calendar()

        #assert
        self.assertFalse(self.recurrence.exists())
        self.assertFalse(self.recurrence.calendar_event_ids.exists())

    @patch.object(MicrosoftCalendarService,'get_events')
    deftest_delete_all_events_from_recurrence_from_outlook_calendar(self,mock_get_events):
        """
        Samethantest_delete_first_event_and_future_from_recurrence_from_outlook_calendar.
        """
