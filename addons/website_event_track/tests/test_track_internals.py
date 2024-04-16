#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromdatetimeimportdatetime,timedelta
fromunittest.mockimportpatch

fromflectraimportfields
fromflectra.addons.website.models.website_visitorimportWebsiteVisitor
fromflectra.addons.website_event_track.tests.commonimportTestEventTrackOnlineCommon
fromflectra.tests.commonimportusers


classTestTrackData(TestEventTrackOnlineCommon):

    @users('user_eventmanager')
    deftest_track_partner_sync(self):
        """Testregistrationcomputedfieldsaboutpartner"""
        test_email='"NibblerInSpace"<nibbler@futurama.example.com>'
        test_phone='0456001122'
        test_bio='<p>UserInput</p>'
        test_bio_void='<p><br/></p>'

        event=self.env['event.event'].browse(self.event_0.ids)
        customer=self.env['res.partner'].browse(self.event_customer.id)

        #takeallfrompartner
        new_track=self.env['event.track'].create({
            'event_id':event.id,
            'name':'MegaTrack',
            'partner_id':customer.id,
        })
        self.assertEqual(new_track.partner_id,customer)
        self.assertEqual(new_track.partner_name,customer.name)
        self.assertEqual(new_track.partner_email,customer.email)
        self.assertEqual(new_track.partner_phone,customer.phone)
        self.assertEqual(new_track.partner_biography,customer.website_description)
        self.assertIn(customer.name,new_track.partner_biography,'Low-leveltest:ensurecorrectlyupdated')

        #partialupdate
        new_track=self.env['event.track'].create({
            'event_id':event.id,
            'name':'MegaTrack',
            'partner_id':customer.id,
            'partner_name':'NibblerInSpace',
            'partner_email':test_email,
        })
        self.assertEqual(new_track.partner_id,customer)
        self.assertEqual(
            new_track.partner_name,'NibblerInSpace',
            'Trackshouldtakeuserinputovercomputedpartnervalue')
        self.assertEqual(
            new_track.partner_email,test_email,
            'Trackshouldtakeuserinputovercomputedpartnervalue')
        self.assertEqual(
            new_track.partner_phone,customer.phone,
            'Trackshouldtakepartnervalueifnotuserinput')

        #alreadyfilledinformationshouldnotbeupdated
        new_track=self.env['event.track'].create({
            'event_id':event.id,
            'name':'MegaTrack',
            'partner_name':'NibblerInSpace',
            'partner_phone':test_phone,
            'partner_biography':test_bio,
        })
        self.assertEqual(new_track.partner_name,'NibblerInSpace')
        self.assertEqual(new_track.partner_email,False)
        self.assertEqual(new_track.partner_phone,test_phone)
        self.assertEqual(new_track.partner_biography,test_bio)
        new_track.write({'partner_id':customer.id})
        self.assertEqual(new_track.partner_id,customer)
        self.assertEqual(
            new_track.partner_name,customer.name,
            'Trackcustomershouldtakeoverexistingvalue')
        self.assertEqual(
            new_track.partner_email,customer.email,
            'Trackcustomershouldtakeoverexistingvalue')
        self.assertEqual(
            new_track.partner_phone,customer.phone,
            'Trackcustomershouldtakeoverexistingvalue')


classTestTrackSuggestions(TestEventTrackOnlineCommon):

    deftest_track_suggestion(self):
        [location_1,location_2]=self.env['event.track.location'].create([
            {'name':'Location1'},
            {'name':'Location2'},
        ])

        [tag_1,tag_2,tag_3,tag_4]=self.env['event.track.tag'].create([
            {'name':'Tag1'},{'name':'Tag2'},{'name':'Tag3'},{'name':'Tag4'}
        ])

        date=fields.Datetime.from_string(datetime.now().strftime('%Y-%m-%d%H:00:00'))
        [track_1,track_2,track_3,track_4,track_5,track_6]=self.env['event.track'].create([{
            'name':'Track1',
            'location_id':location_1.id,
            'event_id':self.event_0.id,
            'tag_ids':[(4,tag_1.id),(4,tag_2.id)],
            'date':date+timedelta(hours=-1),
        },{
            'name':'Track2',
            'location_id':location_2.id,
            'event_id':self.event_0.id,
            'date':date,
        },{
            'name':'Track3',
            'location_id':location_2.id,
            'event_id':self.event_0.id,
            'tag_ids':[(4,tag_1.id),(4,tag_3.id),(4,tag_4.id)],
            'date':date,
        },{
            'name':'Track4',
            'event_id':self.event_0.id,
            'tag_ids':[(4,tag_1.id),(4,tag_2.id)],
            'date':date,
        },{
            'name':'Track5',
            'event_id':self.event_0.id,
            'tag_ids':[(4,tag_1.id),(4,tag_3.id)],
            'wishlisted_by_default':True,
            'date':date,
        },{
            'name':'Track6',
            'location_id':location_1.id,
            'event_id':self.event_0.id,
            'tag_ids':[(4,tag_1.id),(4,tag_3.id)],
            'date':date,
        }])

        emp_visitor=self.env['website.visitor'].create({
            'name':'Visitor',
            'partner_id':self.user_employee.partner_id.id
        })
        visitor_track=self.env['event.track.visitor'].create({
            'visitor_id':emp_visitor.id,
            'track_id':track_3.id,
            'is_wishlisted':True,
        })

        withpatch.object(WebsiteVisitor,'_get_visitor_from_request',lambda*args,**kwargs:emp_visitor),\
                self.with_user('user_employee'):
            current_track=self.env['event.track'].browse(track_1.id)
            all_suggestions=current_track._get_track_suggestions()
            self.assertEqual(
                all_suggestions.ids,
                (track_3+track_5+track_4+track_6+track_2).ids#whlst/wishlstdef/tagscount/location
            )

            track_suggestion=current_track._get_track_suggestions(limit=1)
            self.assertEqual(track_suggestion,track_3,
                'Returnedtrackshouldbethemanuallywishlistedone')

            #removewishlist,keynoteshouldbetop
            visitor_track.unlink()
            track_suggestion=current_track._get_track_suggestions(limit=1)
            self.assertEqual(
                track_suggestion,track_5,
                'Returnedtrackshouldbethedefaultwishlistedone')

            #togglewishlistedbydefaultoffthroughblacklist
            track_5_visitor=self.env['event.track.visitor'].sudo().create({
                'visitor_id':emp_visitor.id,
                'track_id':track_5.id,
                'is_blacklisted':True,
            })
            track_suggestion=current_track._get_track_suggestions(limit=1)
            self.assertEqual(
                track_suggestion,track_4,
                'Returnedtrackshouldtheonewiththemostcommontagsaskeynoteisblacklisted')
            track_5_visitor.unlink()

            #removekeynotedefault,nowbasedontags
            track_5.write({'wishlisted_by_default':False})
            #all_suggestions.invalidate_cache(fnames=['is_reminder_on'])
            track_suggestion=current_track._get_track_suggestions(limit=1)
            self.assertEqual(
                track_suggestion,track_4,
                'Returnedtrackshouldtheonewiththemostcommontags')

            #removetags,nowbasedonlocation
            all_suggestions.sudo().write({'tag_ids':[(5,)]})
            track_suggestion=current_track._get_track_suggestions(limit=1)
            self.assertEqual(
                track_suggestion,track_6,
                'Returnedtrackshouldtheonewithmatchinglocation')

            #removelocation,nowbasedorandom
            all_suggestions.sudo().write({'location_id':False})
            track_suggestion=current_track._get_track_suggestions(limit=1)
            self.assertTrue(
                track_suggestionin[track_2,track_3,track_4,track_5,track_6],
                "Returnedtrackshouldthearandomone(butnottheonewe'retryingtogetsuggestionfor)")
