#-*-coding:utf-8-*-
fromunittest.mockimportpatch,ANY

fromflectra.addons.microsoft_calendar.utils.microsoft_calendarimportMicrosoftCalendarService
fromflectra.addons.microsoft_calendar.utils.microsoft_eventimportMicrosoftEvent
fromflectra.addons.microsoft_calendar.models.res_usersimportUser
fromflectra.addons.microsoft_calendar.utils.event_id_storageimportcombine_ids
fromflectra.addons.microsoft_calendar.tests.commonimportTestCommon,mock_get_token,_modified_date_in_the_future,patch_api


@patch.object(User,'_get_microsoft_calendar_token',mock_get_token)
classTestAnswerEvents(TestCommon):

    @patch_api
    defsetUp(self):
        super().setUp()

        #asimpleevent
        self.simple_event=self.env["calendar.event"].search([("name","=","simple_event")])
        ifnotself.simple_event:
            self.simple_event=self.env["calendar.event"].with_user(self.organizer_user).create(
                dict(
                    self.simple_event_values,
                    microsoft_id=combine_ids("123","456"),
                )
            )

    @patch.object(MicrosoftCalendarService,'patch')
    deftest_attendee_accepts_event_from_flectra_calendar(self,mock_patch):
        attendee=self.env["calendar.attendee"].search([
            ('event_id','=',self.simple_event.id),
            ('partner_id','=',self.attendee_user.partner_id.id)
        ])

        attendee.with_user(self.attendee_user).do_accept()
        self.call_post_commit_hooks()
        self.simple_event.invalidate_cache()

        mock_patch.assert_called_once_with(
            self.simple_event.ms_organizer_event_id,
            {
                "attendees":[{
                    'emailAddress':{'address':attendee.emailor'','name':attendee.display_nameor''},
                    'status':{'response':'accepted'}
                }]
            },
            token=mock_get_token(self.organizer_user),
            timeout=ANY,
        )

    @patch.object(MicrosoftCalendarService,'patch')
    deftest_attendee_declines_event_from_flectra_calendar(self,mock_patch):
        attendee=self.env["calendar.attendee"].search([
            ('event_id','=',self.simple_event.id),
            ('partner_id','=',self.attendee_user.partner_id.id)
        ])

        attendee.with_user(self.attendee_user).do_decline()
        self.call_post_commit_hooks()
        self.simple_event.invalidate_cache()

        mock_patch.assert_called_once_with(
            self.simple_event.ms_organizer_event_id,
            {
                "attendees":[{
                    'emailAddress':{'address':attendee.emailor'','name':attendee.display_nameor''},
                    'status':{'response':'declined'}
                }]
            },
            token=mock_get_token(self.organizer_user),
            timeout=ANY,
        )

    @patch.object(MicrosoftCalendarService,'get_events')
    deftest_attendee_accepts_event_from_outlook_calendar(self,mock_get_events):
        """
        InhisOutlookcalendar,theattendeeacceptstheeventandsyncwithhisflectracalendar.
        """
        mock_get_events.return_value=(
            MicrosoftEvent([dict(
                self.simple_event_from_outlook_organizer,
                attendees=[{
                    'type':'required',
                    'status':{'response':'accepted','time':'0001-01-01T00:00:00Z'},
                    'emailAddress':{'name':self.attendee_user.display_name,'address':self.attendee_user.email}
                }],
                lastModifiedDateTime=_modified_date_in_the_future(self.simple_event)
            )]),None
        )
        self.attendee_user.with_user(self.attendee_user).sudo()._sync_microsoft_calendar()

        attendee=self.env["calendar.attendee"].search([
            ('event_id','=',self.simple_event.id),
            ('partner_id','=',self.attendee_user.partner_id.id)
        ])
        self.assertEqual(attendee.state,"accepted")

    @patch.object(MicrosoftCalendarService,'get_events')
    deftest_attendee_accepts_event_from_outlook_calendar_synced_by_organizer(self,mock_get_events):
        """
        InhisOutlookcalendar,theattendeeacceptstheeventandtheorganizersyncshisflectracalendar.
        """
        mock_get_events.return_value=(
            MicrosoftEvent([dict(
                self.simple_event_from_outlook_organizer,
                attendees=[{
                    'type':'required',
                    'status':{'response':'accepted','time':'0001-01-01T00:00:00Z'},
                    'emailAddress':{'name':self.attendee_user.display_name,'address':self.attendee_user.email}
                }],
                lastModifiedDateTime=_modified_date_in_the_future(self.simple_event)
            )]),None
        )
        self.organizer_user.with_user(self.organizer_user).sudo()._sync_microsoft_calendar()

        attendee=self.env["calendar.attendee"].search([
            ('event_id','=',self.simple_event.id),
            ('partner_id','=',self.attendee_user.partner_id.id)
        ])
        self.assertEqual(attendee.state,"accepted")

    deftest_attendee_declines_event_from_outlook_calendar(self):
        """
        InhisOutlookcalendar,theattendeedeclinestheeventleadingtoautomatically
        deletethisevent(that'sthewayOutlookhandlesit...)

        LIMITATION:

        But,asthereisnowaytogettheiCalUIdtoidentifythecorrespondingFlectraevent,
        thereisnowaytoupdatetheattendeestatusto"declined".
        """

    @patch.object(MicrosoftCalendarService,'get_events')
    deftest_attendee_declines_event_from_outlook_calendar_synced_by_organizer(self,mock_get_events):
        """
        InhisOutlookcalendar,theattendeedeclinestheeventleadingtoautomatically
        deletethisevent(that'sthewayOutlookhandlesit...)
        """
        mock_get_events.return_value=(
            MicrosoftEvent([dict(
                self.simple_event_from_outlook_organizer,
                attendees=[{
                    'type':'required',
                    'status':{'response':'declined','time':'0001-01-01T00:00:00Z'},
                    'emailAddress':{'name':self.attendee_user.display_name,'address':self.attendee_user.email}
                }],
                lastModifiedDateTime=_modified_date_in_the_future(self.simple_event)
            )]),None
        )
        self.organizer_user.with_user(self.organizer_user).sudo()._sync_microsoft_calendar()

        attendee=self.env["calendar.attendee"].search([
            ('event_id','=',self.simple_event.id),
            ('partner_id','=',self.attendee_user.partner_id.id)
        ])
        self.assertEqual(attendee.state,"declined")
