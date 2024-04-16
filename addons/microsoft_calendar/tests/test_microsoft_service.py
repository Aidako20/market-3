importjson
importrequests
fromunittest.mockimportpatch,call,MagicMock

fromflectraimportfields
fromflectra.addons.microsoft_calendar.utils.microsoft_calendarimportMicrosoftCalendarService
fromflectra.addons.microsoft_calendar.utils.microsoft_eventimportMicrosoftEvent
fromflectra.addons.microsoft_account.models.microsoft_serviceimportMicrosoftService
fromflectra.testsimportTransactionCase


DEFAULT_TIMEOUT=20


classTestMicrosoftService(TransactionCase):

    def_do_request_result(self,data):
        """_do_requestreturnsatuple(status,data,time)butonlythedatapartisused"""
        return(None,data,None)

    defsetUp(self):
        super(TestMicrosoftService,self).setUp()

        self.service=MicrosoftCalendarService(self.env["microsoft.service"])
        self.fake_token="MY_TOKEN"
        self.fake_sync_token="MY_SYNC_TOKEN"
        self.fake_next_sync_token="MY_NEXT_SYNC_TOKEN"
        self.fake_next_sync_token_url=f"https://graph.microsoft.com/v1.0/me/calendarView/delta?$deltatoken={self.fake_next_sync_token}"

        self.header_prefer='outlook.body-content-type="text",odata.maxpagesize=50'
        self.header={'Content-type':'application/json','Authorization':'Bearer%s'%self.fake_token}
        self.call_with_sync_token=call(
            "/v1.0/me/calendarView/delta",
            {"$deltatoken":self.fake_sync_token},
            {**self.header,'Prefer':self.header_prefer},
            method="GET",timeout=DEFAULT_TIMEOUT,
        )
        self.call_without_sync_token=call(
            "/v1.0/me/calendarView/delta",
            {
                'startDateTime':fields.Datetime.subtract(fields.Datetime.now(),years=2).strftime("%Y-%m-%dT00:00:00Z"),
                'endDateTime':fields.Datetime.add(fields.Datetime.now(),years=2).strftime("%Y-%m-%dT00:00:00Z"),
            },
            {**self.header,'Prefer':self.header_prefer},
            method="GET",timeout=DEFAULT_TIMEOUT,
        )

    deftest_get_events_delta_without_token(self):
        """
        ifnotokenisprovided,anexceptionisraised
        """
        withself.assertRaises(AttributeError):
            self.service._get_events_delta()

    @patch.object(MicrosoftService,"_do_request")
    deftest_get_events_unexpected_exception(self,mock_do_request):
        """
        Whenanunexpectedexceptionisraised,justpropagateit.
        """
        mock_do_request.side_effect=Exception()

        withself.assertRaises(Exception):
            self.service._get_events_delta(token=self.fake_token,timeout=DEFAULT_TIMEOUT)

    @patch.object(MicrosoftService,"_do_request")
    deftest_get_events_delta_token_error(self,mock_do_request):
        """
        Whentheprovidedsynctokenisinvalid,anexceptionshouldberaisedandthen
        afullsyncshouldbedone.
        """
        mock_do_request.side_effect=[
            requests.HTTPError(response=MagicMock(status_code=410,content="fullSyncRequired")),
            self._do_request_result({"value":[]}),
        ]

        events,next_token=self.service._get_events_delta(
            token=self.fake_token,sync_token=self.fake_sync_token,timeout=DEFAULT_TIMEOUT
        )

        self.assertEqual(next_token,None)
        self.assertFalse(events)
        mock_do_request.assert_has_calls([self.call_with_sync_token,self.call_without_sync_token])

    @patch.object(MicrosoftService,"_do_request")
    deftest_get_events_delta_without_sync_token(self,mock_do_request):
        """
        whennosynctokenisprovided,afullsyncshouldbedone
        """
        #returnsemptydatawithoutanynextsynctoken
        mock_do_request.return_value=self._do_request_result({"value":[]})

        events,next_token=self.service._get_events_delta(token=self.fake_token,timeout=DEFAULT_TIMEOUT)

        self.assertEqual(next_token,None)
        self.assertFalse(events)
        mock_do_request.assert_has_calls([self.call_without_sync_token])

    @patch.object(MicrosoftService,"_do_request")
    deftest_get_events_delta_with_sync_token(self,mock_do_request):
        """
        whenasynctokenisprovided,weshouldretrievethesynctokentouseforthenextsync.
        """
        #returnsemptydatawithanextsynctoken
        mock_do_request.return_value=self._do_request_result({
            "value":[],
            "@odata.deltaLink":self.fake_next_sync_token_url
        })

        events,next_token=self.service._get_events_delta(
            token=self.fake_token,sync_token=self.fake_sync_token,timeout=DEFAULT_TIMEOUT
        )

        self.assertEqual(next_token,"MY_NEXT_SYNC_TOKEN")
        self.assertFalse(events)
        mock_do_request.assert_has_calls([self.call_with_sync_token])

    @patch.object(MicrosoftService,"_do_request")
    deftest_get_events_one_page(self,mock_do_request):
        """
        Whenalleventsareononepage,justgetthem.
        """
        mock_do_request.return_value=self._do_request_result({
            "value":[
                {"id":1,"type":"singleInstance","subject":"ev1"},
                {"id":2,"type":"singleInstance","subject":"ev2"},
                {"id":3,"type":"singleInstance","subject":"ev3"},
            ],
        })
        events,_=self.service._get_events_delta(token=self.fake_token,timeout=DEFAULT_TIMEOUT)

        self.assertEqual(events,MicrosoftEvent([
            {"id":1,"type":"singleInstance","subject":"ev1"},
            {"id":2,"type":"singleInstance","subject":"ev2"},
            {"id":3,"type":"singleInstance","subject":"ev3"},
        ]))
        mock_do_request.assert_has_calls([self.call_without_sync_token])

    @patch.object(MicrosoftService,"_do_request")
    deftest_get_events_loop_over_pages(self,mock_do_request):
        """
        Loopoverpagestoretrievealltheevents.
        """
        mock_do_request.side_effect=[
            self._do_request_result({
                "value":[{"id":1,"type":"singleInstance","subject":"ev1"}],
                "@odata.nextLink":"link_1"
            }),
            self._do_request_result({
                "value":[{"id":2,"type":"singleInstance","subject":"ev2"}],
                "@odata.nextLink":"link_2"
            }),
            self._do_request_result({
                "value":[{"id":3,"type":"singleInstance","subject":"ev3"}],
            }),
        ]

        events,_=self.service._get_events_delta(token=self.fake_token,timeout=DEFAULT_TIMEOUT)

        self.assertEqual(events,MicrosoftEvent([
            {"id":1,"type":"singleInstance","subject":"ev1"},
            {"id":2,"type":"singleInstance","subject":"ev2"},
            {"id":3,"type":"singleInstance","subject":"ev3"},
        ]))
        mock_do_request.assert_has_calls([
            self.call_without_sync_token,
            call(
                "link_1",
                {},
                {**self.header,'Prefer':self.header_prefer},
                preuri='',method="GET",timeout=DEFAULT_TIMEOUT
            ),
            call(
                "link_2",
                {},
                {**self.header,'Prefer':self.header_prefer},
                preuri='',method="GET",timeout=DEFAULT_TIMEOUT
            ),
        ])

    @patch.object(MicrosoftService,"_do_request")
    deftest_get_events_filter_out_occurrences(self,mock_do_request):
        """
        Whenalleventsareononepage,justgetthem.
        """
        mock_do_request.return_value=self._do_request_result({
            "value":[
                {"id":1,"type":"singleInstance","subject":"ev1"},
                {"id":2,"type":"occurrence","subject":"ev2"},
                {"id":3,"type":"seriesMaster","subject":"ev3"},
            ],
        })
        events,_=self.service._get_events_delta(token=self.fake_token,timeout=DEFAULT_TIMEOUT)

        self.assertEqual(events,MicrosoftEvent([
            {"id":1,"type":"singleInstance","subject":"ev1"},
            {"id":3,"type":"seriesMaster","subject":"ev3"},
        ]))
        mock_do_request.assert_has_calls([self.call_without_sync_token])

    deftest_get_occurrence_details_token_error(self):
        """
        ifnotokenisprovided,anexceptionisraised
        """
        withself.assertRaises(AttributeError):
            self.service._get_occurrence_details(1)

    @patch.object(MicrosoftService,"_do_request")
    deftest_get_occurrence_details(self,mock_do_request):
        mock_do_request.return_value=self._do_request_result({
            "value":[
                {"id":1,"type":"singleInstance","subject":"ev1"},
                {"id":2,"type":"occurrence","subject":"ev2"},
                {"id":3,"type":"seriesMaster","subject":"ev3"},
            ],
        })
        events=self.service._get_occurrence_details(123,token=self.fake_token,timeout=DEFAULT_TIMEOUT)

        self.assertEqual(events,MicrosoftEvent([
            {"id":1,"type":"singleInstance","subject":"ev1"},
            {"id":2,"type":"occurrence","subject":"ev2"},
            {"id":3,"type":"seriesMaster","subject":"ev3"},
        ]))

        mock_do_request.assert_called_with(
            "/v1.0/me/events/123/instances",
            {
                'startDateTime':fields.Datetime.subtract(fields.Datetime.now(),years=2).strftime("%Y-%m-%dT00:00:00Z"),
                'endDateTime':fields.Datetime.add(fields.Datetime.now(),years=2).strftime("%Y-%m-%dT00:00:00Z"),
            },
            {**self.header,'Prefer':self.header_prefer},
            method='GET',timeout=DEFAULT_TIMEOUT,
        )

    deftest_get_events_token_error(self):
        """
        ifnotokenisprovided,anexceptionisraised
        """
        withself.assertRaises(AttributeError):
            self.service.get_events()

    @patch.object(MicrosoftService,"_do_request")
    deftest_get_events_no_serie_master(self,mock_do_request):
        """
        Whenthereisnoseriemaster,justretrievethelistofevents.
        """
        mock_do_request.return_value=self._do_request_result({
            "value":[
                {"id":1,"type":"singleInstance","subject":"ev1"},
                {"id":2,"type":"singleInstance","subject":"ev2"},
                {"id":3,"type":"singleInstance","subject":"ev3"},
            ],
        })

        events,_=self.service.get_events(token=self.fake_token,timeout=DEFAULT_TIMEOUT)

        self.assertEqual(events,MicrosoftEvent([
            {"id":1,"type":"singleInstance","subject":"ev1"},
            {"id":2,"type":"singleInstance","subject":"ev2"},
            {"id":3,"type":"singleInstance","subject":"ev3"},
        ]))

    @patch.object(MicrosoftService,"_do_request")
    deftest_get_events_with_one_serie_master(self,mock_do_request):
        """
        Whenthereisaseriemaster,retrievethelistofeventsandeventoccurrenceslinkedtotheseriemaster
        """
        mock_do_request.side_effect=[
            self._do_request_result({
                "value":[
                    {"id":1,"type":"singleInstance","subject":"ev1"},
                    {"id":2,"type":"seriesMaster","subject":"ev2"},
                ],
            }),
            self._do_request_result({
                "value":[
                    {"id":3,"type":"occurrence","subject":"ev3"},
                ],
            }),
        ]

        events,_=self.service.get_events(token=self.fake_token,timeout=DEFAULT_TIMEOUT)

        self.assertEqual(events,MicrosoftEvent([
            {"id":1,"type":"singleInstance","subject":"ev1"},
            {"id":2,"type":"seriesMaster","subject":"ev2"},
            {"id":3,"type":"occurrence","subject":"ev3"},
        ]))

    deftest_insert_token_error(self):
        """
        ifnotokenisprovided,anexceptionisraised
        """
        withself.assertRaises(AttributeError):
            self.service.insert({})


    @patch.object(MicrosoftService,"_do_request")
    deftest_insert(self,mock_do_request):

        mock_do_request.return_value=self._do_request_result({'id':1,'iCalUId':2})

        instance_id,event_id=self.service.insert({"subject":"ev1"},token=self.fake_token,timeout=DEFAULT_TIMEOUT)

        self.assertEqual(instance_id,1)
        self.assertEqual(event_id,2)
        mock_do_request.assert_called_with(
            "/v1.0/me/calendar/events",
            json.dumps({"subject":"ev1"}),
            self.header,method="POST",timeout=DEFAULT_TIMEOUT
        )

    deftest_patch_token_error(self):
        """
        ifnotokenisprovided,anexceptionisraised
        """
        withself.assertRaises(AttributeError):
            self.service.patch(123,{})

    @patch.object(MicrosoftService,"_do_request")
    deftest_patch_returns_false_if_event_does_not_exist(self,mock_do_request):
        event_id=123
        values={"subject":"ev2"}
        mock_do_request.return_value=(404,"",None)

        res=self.service.patch(event_id,values,token=self.fake_token,timeout=DEFAULT_TIMEOUT)

        self.assertFalse(res)
        mock_do_request.assert_called_with(
            f"/v1.0/me/calendar/events/{event_id}",
            json.dumps(values),
            self.header,method="PATCH",timeout=DEFAULT_TIMEOUT
        )

    @patch.object(MicrosoftService,"_do_request")
    deftest_patch_an_existing_event(self,mock_do_request):
        event_id=123
        values={"subject":"ev2"}
        mock_do_request.return_value=(200,"",None)

        res=self.service.patch(event_id,values,token=self.fake_token,timeout=DEFAULT_TIMEOUT)

        self.assertTrue(res)
        mock_do_request.assert_called_with(
            f"/v1.0/me/calendar/events/{event_id}",
            json.dumps(values),
            self.header,method="PATCH",timeout=DEFAULT_TIMEOUT
        )

    deftest_delete_token_error(self):
        """
        ifnotokenisprovided,anexceptionisraised
        """
        withself.assertRaises(AttributeError):
            self.service.delete(123)

    @patch.object(MicrosoftService,"_do_request")
    deftest_delete_returns_false_if_event_does_not_exist(self,mock_do_request):
        event_id=123
        mock_do_request.return_value=(404,"",None)

        res=self.service.delete(event_id,token=self.fake_token,timeout=DEFAULT_TIMEOUT)

        self.assertFalse(res)
        mock_do_request.assert_called_with(
            f"/v1.0/me/calendar/events/{event_id}",
            {},headers={'Authorization':'Bearer%s'%self.fake_token},method="DELETE",timeout=DEFAULT_TIMEOUT
        )

    @patch.object(MicrosoftService,"_do_request")
    deftest_delete_an_already_cancelled_event(self,mock_do_request):
        """
        Whenaneventhasalreadybeencancelled,Outlookmayreturnastatuscodeequalsto403or410.
        Inthiscase,thedeletemethodshouldreturnTrue.
        """
        event_id=123

        forstatusin(403,410):
            mock_do_request.return_value=(status,"",None)

            res=self.service.delete(event_id,token=self.fake_token,timeout=DEFAULT_TIMEOUT)

            self.assertTrue(res)
            mock_do_request.assert_called_with(
                f"/v1.0/me/calendar/events/{event_id}",
                {},headers={'Authorization':'Bearer%s'%self.fake_token},method="DELETE",timeout=DEFAULT_TIMEOUT
            )


    @patch.object(MicrosoftService,"_do_request")
    deftest_delete_an_existing_event(self,mock_do_request):
        event_id=123
        mock_do_request.return_value=(200,"",None)

        res=self.service.delete(event_id,token=self.fake_token,timeout=DEFAULT_TIMEOUT)

        self.assertTrue(res)
        mock_do_request.assert_called_with(
            f"/v1.0/me/calendar/events/{event_id}",
            {},headers={'Authorization':'Bearer%s'%self.fake_token},method="DELETE",timeout=DEFAULT_TIMEOUT
        )

    deftest_answer_token_error(self):
        """
        ifnotokenisprovided,anexceptionisraised
        """
        withself.assertRaises(AttributeError):
            self.service.answer(123,'ok',{})

    @patch.object(MicrosoftService,"_do_request")
    deftest_answer_returns_false_if_event_does_not_exist(self,mock_do_request):
        event_id=123
        answer="accept"
        values={"a":1,"b":2}
        mock_do_request.return_value=(404,"",None)

        res=self.service.answer(event_id,answer,values,token=self.fake_token,timeout=DEFAULT_TIMEOUT)

        self.assertFalse(res)
        mock_do_request.assert_called_with(
            f"/v1.0/me/calendar/events/{event_id}/{answer}",
            json.dumps(values),
            self.header,method="POST",timeout=DEFAULT_TIMEOUT
        )

    @patch.object(MicrosoftService,"_do_request")
    deftest_answer_to_an_existing_event(self,mock_do_request):
        event_id=123
        answer="decline"
        values={"a":1,"b":2}
        mock_do_request.return_value=(200,"",None)

        res=self.service.answer(event_id,answer,values,token=self.fake_token,timeout=DEFAULT_TIMEOUT)

        self.assertTrue(res)
        mock_do_request.assert_called_with(
            f"/v1.0/me/calendar/events/{event_id}/{answer}",
            json.dumps(values),
            self.header,method="POST",timeout=DEFAULT_TIMEOUT
        )
