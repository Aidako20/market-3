fromflectra.addons.microsoft_calendar.utils.microsoft_eventimportMicrosoftEvent
fromflectra.addons.microsoft_calendar.tests.commonimportTestCommon,patch_api

classTestMicrosoftEvent(TestCommon):

    @patch_api
    defsetUp(self):
        super().setUp()
        self.create_events_for_tests()

    deftest_already_mapped_events(self):

        #arrange
        event_id=self.simple_event.ms_organizer_event_id
        event_uid=self.simple_event.ms_universal_event_id
        events=MicrosoftEvent([{
            "type":"singleInstance",
            "_flectra_id":self.simple_event.id,
            "iCalUId":event_uid,
            "id":event_id,
        }])

        #act
        mapped=events._load_flectra_ids_from_db(self.env)

        #assert
        self.assertEqual(len(mapped._events),1)
        self.assertEqual(mapped._events[event_id]["_flectra_id"],self.simple_event.id)

    deftest_map_an_event_using_global_id(self):

        #arrange
        event_id=self.simple_event.ms_organizer_event_id
        event_uid=self.simple_event.ms_universal_event_id
        events=MicrosoftEvent([{
            "type":"singleInstance",
            "_flectra_id":False,
            "iCalUId":event_uid,
            "id":event_id,
        }])

        #act
        mapped=events._load_flectra_ids_from_db(self.env)

        #assert
        self.assertEqual(len(mapped._events),1)
        self.assertEqual(mapped._events[event_id]["_flectra_id"],self.simple_event.id)

    deftest_map_an_event_using_instance_id(self):
        """
        Here,theFlectraeventhasanuidbuttheOutlookeventhasnot.
        """
        #arrange
        event_id=self.simple_event.ms_organizer_event_id
        events=MicrosoftEvent([{
            "type":"singleInstance",
            "_flectra_id":False,
            "iCalUId":False,
            "id":event_id,
        }])

        #act
        mapped=events._load_flectra_ids_from_db(self.env)

        #assert
        self.assertEqual(len(mapped._events),1)
        self.assertEqual(mapped._events[event_id]["_flectra_id"],self.simple_event.id)

    deftest_map_an_event_without_uid_using_instance_id(self):
        """
        Here,theFlectraeventhasnouidbuttheOutlookeventhasone.
        """

        #arrange
        event_id=self.simple_event.ms_organizer_event_id
        event_uid=self.simple_event.ms_universal_event_id
        self.simple_event.ms_universal_event_id=False
        events=MicrosoftEvent([{
            "type":"singleInstance",
            "_flectra_id":False,
            "iCalUId":event_uid,
            "id":event_id,
        }])

        #act
        mapped=events._load_flectra_ids_from_db(self.env)

        #assert
        self.assertEqual(len(mapped._events),1)
        self.assertEqual(mapped._events[event_id]["_flectra_id"],self.simple_event.id)
        self.assertEqual(self.simple_event.ms_universal_event_id,event_uid)

    deftest_map_an_event_without_uid_using_instance_id_2(self):
        """
        Here,bothFlectraeventandOutlookeventhavenouid.
        """

        #arrange
        event_id=self.simple_event.ms_organizer_event_id
        self.simple_event.ms_universal_event_id=False
        events=MicrosoftEvent([{
            "type":"singleInstance",
            "_flectra_id":False,
            "iCalUId":False,
            "id":event_id,
        }])

        #act
        mapped=events._load_flectra_ids_from_db(self.env)

        #assert
        self.assertEqual(len(mapped._events),1)
        self.assertEqual(mapped._events[event_id]["_flectra_id"],self.simple_event.id)
        self.assertEqual(self.simple_event.ms_universal_event_id,False)

    deftest_map_a_recurrence_using_global_id(self):

        #arrange
        rec_id=self.recurrence.ms_organizer_event_id
        rec_uid=self.recurrence.ms_universal_event_id
        events=MicrosoftEvent([{
            "type":"seriesMaster",
            "_flectra_id":False,
            "iCalUId":rec_uid,
            "id":rec_id,
        }])

        #act
        mapped=events._load_flectra_ids_from_db(self.env)

        #assert
        self.assertEqual(len(mapped._events),1)
        self.assertEqual(mapped._events[rec_id]["_flectra_id"],self.recurrence.id)

    deftest_map_a_recurrence_using_instance_id(self):

        #arrange
        rec_id=self.recurrence.ms_organizer_event_id
        events=MicrosoftEvent([{
            "type":"seriesMaster",
            "_flectra_id":False,
            "iCalUId":False,
            "id":rec_id,
        }])

        #act
        mapped=events._load_flectra_ids_from_db(self.env)

        #assert
        self.assertEqual(len(mapped._events),1)
        self.assertEqual(mapped._events[rec_id]["_flectra_id"],self.recurrence.id)

    deftest_try_to_map_mixed_of_single_events_and_recurrences(self):

        #arrange
        event_id=self.simple_event.ms_organizer_event_id
        event_uid=self.simple_event.ms_universal_event_id
        rec_id=self.recurrence.ms_organizer_event_id
        rec_uid=self.recurrence.ms_universal_event_id

        events=MicrosoftEvent([
            {
                "type":"seriesMaster",
                "_flectra_id":False,
                "iCalUId":rec_uid,
                "id":rec_id,
            },
            {
                "type":"singleInstance",
                "_flectra_id":False,
                "iCalUId":event_uid,
                "id":event_id,
            },
        ])

        #act&assert
        withself.assertRaises(TypeError):
            events._load_flectra_ids_from_db(self.env)

    deftest_match_event_only(self):

        #arrange
        event_id=self.simple_event.ms_organizer_event_id
        event_uid=self.simple_event.ms_universal_event_id
        events=MicrosoftEvent([{
            "type":"singleInstance",
            "_flectra_id":False,
            "iCalUId":event_uid,
            "id":event_id,
        }])

        #act
        matched=events.match_with_flectra_events(self.env)

        #assert
        self.assertEqual(len(matched._events),1)
        self.assertEqual(matched._events[event_id]["_flectra_id"],self.simple_event.id)

    deftest_match_recurrence_only(self):

        #arrange
        rec_id=self.recurrence.ms_organizer_event_id
        rec_uid=self.recurrence.ms_universal_event_id
        events=MicrosoftEvent([{
            "type":"seriesMaster",
            "_flectra_id":False,
            "iCalUId":rec_uid,
            "id":rec_id,
        }])

        #act
        matched=events.match_with_flectra_events(self.env)

        #assert
        self.assertEqual(len(matched._events),1)
        self.assertEqual(matched._events[rec_id]["_flectra_id"],self.recurrence.id)

    deftest_match_not_typed_recurrence(self):
        """
        Whenarecurrenceisdeleted,Outlookreturnstheidofthedeletedrecurrence
        withoutthetypeofevent,soit'snotdirectlypossibletoknowthatit'sa
        recurrence.
        """
        #arrange
        rec_id=self.recurrence.ms_organizer_event_id
        rec_uid=self.recurrence.ms_universal_event_id
        events=MicrosoftEvent([{
            "@removed":{
                "reason":"deleted",
            },
            "_flectra_id":False,
            "iCalUId":rec_uid,
            "id":rec_id,
        }])

        #act
        matched=events.match_with_flectra_events(self.env)

        #assert
        self.assertEqual(len(matched._events),1)
        self.assertEqual(matched._events[rec_id]["_flectra_id"],self.recurrence.id)

    deftest_match_mix_of_events_and_recurrences(self):

        #arrange
        event_id=self.simple_event.ms_organizer_event_id
        event_uid=self.simple_event.ms_universal_event_id
        rec_id=self.recurrence.ms_organizer_event_id
        rec_uid=self.recurrence.ms_universal_event_id

        events=MicrosoftEvent([
            {
                "type":"singleInstance",
                "_flectra_id":False,
                "iCalUId":event_uid,
                "id":event_id,
            },
            {
                "@removed":{
                    "reason":"deleted",
                },
                "_flectra_id":False,
                "iCalUId":rec_uid,
                "id":rec_id,
            }
        ])

        #act
        matched=events.match_with_flectra_events(self.env)

        #assert
        self.assertEqual(len(matched._events),2)
        self.assertEqual(matched._events[event_id]["_flectra_id"],self.simple_event.id)
        self.assertEqual(matched._events[rec_id]["_flectra_id"],self.recurrence.id)

    deftest_ignore_not_found_items(self):

        #arrange
        events=MicrosoftEvent([{
            "type":"singleInstance",
            "_flectra_id":False,
            "iCalUId":"UNKNOWN_EVENT",
            "id":"UNKNOWN_EVENT",
        }])

        #act
        matched=events.match_with_flectra_events(self.env)

        #assert
        self.assertEqual(len(matched._events),0)

    deftest_search_set_ms_universal_event_id(self):
        not_synced_events=self.env['calendar.event'].search([('ms_universal_event_id','=',False)])
        synced_events=self.env['calendar.event'].search([('ms_universal_event_id','!=',False)])

        self.assertIn(self.simple_event,synced_events)
        self.assertNotIn(self.simple_event,not_synced_events)

        self.simple_event.ms_universal_event_id=''
        not_synced_events=self.env['calendar.event'].search([('ms_universal_event_id','=',False)])
        synced_events=self.env['calendar.event'].search([('ms_universal_event_id','!=',False)])

        self.assertNotIn(self.simple_event,synced_events)
        self.assertIn(self.simple_event,not_synced_events)

    deftest_microsoft_event_readonly(self):
        event=MicrosoftEvent()
        withself.assertRaises(TypeError):
            event._events['foo']='bar'
        withself.assertRaises(AttributeError):
            event._events.update({'foo':'bar'})
        withself.assertRaises(TypeError):
            dict.update(event._events,{'foo':'bar'})
