#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromdatetimeimportdatetime
fromunittest.mockimportpatch

fromflectra.addons.website_event_track.tests.commonimportTestEventTrackOnlineCommon
fromflectra.fieldsimportDatetimeasFieldsDatetime
fromflectra.tests.commonimportusers


classTestSponsorData(TestEventTrackOnlineCommon):

    @classmethod
    defsetUpClass(cls):
        super(TestSponsorData,cls).setUpClass()

        cls.sponsor_0.write({
            'hour_from':8.0,
            'hour_to':18.0,
        })

        cls.wevent_exhib_dt=patch(
            'flectra.addons.website_event_track_exhibitor.models.event_sponsor.fields.Datetime',
            wraps=FieldsDatetime
        )
        cls.mock_wevent_exhib_dt=cls.wevent_exhib_dt.start()
        cls.mock_wevent_exhib_dt.now.return_value=cls.reference_now
        cls.addClassCleanup(cls.wevent_exhib_dt.stop)

    @users('user_eventmanager')
    deftest_event_date_computation(self):
        """Testdatecomputation.PayattentionthatmocksreturnsUTCvalues,meaning
        wehavetotakeintoaccountEurope/Brusselsoffset(+2inJuly)"""
        event=self.env['event.event'].browse(self.event_0.id)
        sponsor=self.env['event.sponsor'].browse(self.sponsor_0.id)
        event.invalidate_cache(fnames=['is_ongoing'])
        self.assertTrue(sponsor.is_in_opening_hours)
        self.assertTrue(event.is_ongoing)

        #Afterhour_from(9>8)
        self.mock_wevent_dt.now.return_value=datetime(2020,7,6,7,0,0)
        self.mock_wevent_exhib_dt.now.return_value=datetime(2020,7,6,7,0,0)
        event.invalidate_cache(fnames=['is_ongoing'])
        sponsor.invalidate_cache(fnames=['is_in_opening_hours'])
        self.assertTrue(sponsor.is_in_opening_hours)
        self.assertTrue(event.is_ongoing)

        #Athour_from(8=8)
        self.mock_wevent_dt.now.return_value=datetime(2020,7,6,6,0,0)
        self.mock_wevent_exhib_dt.now.return_value=datetime(2020,7,6,6,0,0)
        event.invalidate_cache(fnames=['is_ongoing'])
        sponsor.invalidate_cache(fnames=['is_in_opening_hours'])
        self.assertTrue(sponsor.is_in_opening_hours)
        self.assertTrue(event.is_ongoing)

        #Startedbutnotopened(7h59<8)
        self.mock_wevent_dt.now.return_value=datetime(2020,7,6,5,59,59)
        self.mock_wevent_exhib_dt.now.return_value=datetime(2020,7,6,5,59,59)
        event.invalidate_cache(fnames=['is_ongoing'])
        sponsor.invalidate_cache(fnames=['is_in_opening_hours'])
        self.assertFalse(sponsor.is_in_opening_hours)
        self.assertTrue(event.is_ongoing)

        #Eveningeventisnotinopeninghours(20>18)
        self.mock_wevent_dt.now.return_value=datetime(2020,7,6,18,0,0)
        self.mock_wevent_exhib_dt.now.return_value=datetime(2020,7,6,18,0,0)
        event.invalidate_cache(fnames=['is_ongoing'])
        sponsor.invalidate_cache(fnames=['is_in_opening_hours'])
        self.assertFalse(sponsor.is_in_opening_hours)
        self.assertTrue(event.is_ongoing)

        #Firstdaybeginslater
        self.mock_wevent_dt.now.return_value=datetime(2020,7,5,6,30,0)
        self.mock_wevent_exhib_dt.now.return_value=datetime(2020,7,5,6,30,0)
        event.invalidate_cache(fnames=['is_ongoing'])
        sponsor.invalidate_cache(fnames=['is_in_opening_hours'])
        self.assertFalse(sponsor.is_in_opening_hours)
        self.assertFalse(event.is_ongoing)

        #Enddayfinishedsooner
        self.mock_wevent_dt.now.return_value=datetime(2020,7,7,13,0,1)
        self.mock_wevent_exhib_dt.now.return_value=datetime(2020,7,7,13,0,1)
        event.invalidate_cache(fnames=['is_ongoing'])
        sponsor.invalidate_cache(fnames=['is_in_opening_hours'])
        self.assertFalse(sponsor.is_in_opening_hours)
        self.assertFalse(event.is_ongoing)

        #Use"00:00"asopeninghoursforsponsor->shouldstillwork
        event.invalidate_cache(fnames=['is_ongoing'])
        sponsor.hour_from=0.0 #0->18

        #Insideopeninghours(17<18)
        self.mock_wevent_dt.now.return_value=datetime(2020,7,6,15,0,1)
        self.mock_wevent_exhib_dt.now.return_value=datetime(2020,7,6,15,0,1)
        sponsor.invalidate_cache(fnames=['is_in_opening_hours'])
        self.assertTrue(sponsor.is_in_opening_hours)

        #Outsideopeninghours(21>18)
        self.mock_wevent_dt.now.return_value=datetime(2020,7,6,19,0,1)
        self.mock_wevent_exhib_dt.now.return_value=datetime(2020,7,6,19,0,1)
        sponsor.invalidate_cache(fnames=['is_in_opening_hours'])
        self.assertFalse(sponsor.is_in_opening_hours)

        #Use"00:00"asclosinghoursforsponsor->shouldstillwork
        #(considered'atmidnightthenextday')
        sponsor.hour_from=10.0
        sponsor.hour_to=0.0

        #Insideopeninghours(11>10)
        self.mock_wevent_dt.now.return_value=datetime(2020,7,6,9,0,1)
        self.mock_wevent_exhib_dt.now.return_value=datetime(2020,7,6,9,0,1)
        sponsor.invalidate_cache(fnames=['is_in_opening_hours'])
        self.assertTrue(sponsor.is_in_opening_hours)

        #Outsideopeninghours(7<10)
        self.mock_wevent_dt.now.return_value=datetime(2020,7,6,5,0,1)
        self.mock_wevent_exhib_dt.now.return_value=datetime(2020,7,6,5,0,1)
        sponsor.invalidate_cache(fnames=['is_in_opening_hours'])
        self.assertFalse(sponsor.is_in_opening_hours)
