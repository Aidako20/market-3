#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromdatetimeimportdatetime,timedelta

fromflectraimportfields
fromflectra.addons.website_event.tests.commonimportTestWebsiteEventCommon
fromflectra.tests.commonimportusers


classTestEventWebsiteTrack(TestWebsiteEventCommon):

    def_get_menus(self):
        returnsuper(TestEventWebsiteTrack,self)._get_menus()|set(['Community','Talks','Agenda','TalkProposals'])

    @users('user_eventmanager')
    deftest_create_menu(self):
        event=self.env['event.event'].create({
            'name':'TestEvent',
            'date_begin':fields.Datetime.to_string(datetime.today()+timedelta(days=1)),
            'date_end':fields.Datetime.to_string(datetime.today()+timedelta(days=15)),
            'registration_ids':[(0,0,{
                'partner_id':self.user_eventuser.partner_id.id,
                'name':'test_reg',
            })],
            'website_menu':True,
            'community_menu':True,
            'website_track':True,
            'website_track_proposal':True,
        })

        self._assert_website_menus(event)

    @users('user_event_web_manager')
    deftest_menu_management_frontend(self):
        event=self.env['event.event'].create({
            'name':'TestEvent',
            'date_begin':fields.Datetime.to_string(datetime.today()+timedelta(days=1)),
            'date_end':fields.Datetime.to_string(datetime.today()+timedelta(days=15)),
            'website_menu':True,
            'community_menu':True,
            'website_track':True,
            'website_track_proposal':True,
        })
        self.assertTrue(event.website_track)
        self.assertTrue(event.website_track_proposal)
        self._assert_website_menus(event)

        introduction_menu=event.menu_id.child_id.filtered(lambdamenu:menu.name=='Introduction')
        introduction_menu.unlink()
        self._assert_website_menus(event,set(['Location','Register','Community','Talks','Agenda','TalkProposals']))

        menus=event.menu_id.child_id.filtered(lambdamenu:menu.namein['Agenda','TalkProposals'])
        menus.unlink()
        self.assertTrue(event.website_track)
        self.assertFalse(event.website_track_proposal)

        menus=event.menu_id.child_id.filtered(lambdamenu:menu.namein['Talks'])
        menus.unlink()
        self.assertFalse(event.website_track)
        self.assertFalse(event.website_track_proposal)

        self._assert_website_menus(event,set(['Location','Register','Community']))

        event.write({'website_track_proposal':True})
        self.assertFalse(event.website_track)
        self.assertTrue(event.website_track_proposal)
        self._assert_website_menus(event,set(['Location','Register','Community','TalkProposals']))

        event.write({'website_track':True})
        self.assertTrue(event.website_track)
        self.assertTrue(event.website_track_proposal)
        self._assert_website_menus(event,set(['Location','Register','Community','Talks','Agenda','TalkProposals']))

    @users('user_eventmanager')
    deftest_write_menu(self):
        event=self.env['event.event'].create({
            'name':'TestEvent',
            'date_begin':fields.Datetime.to_string(datetime.today()+timedelta(days=1)),
            'date_end':fields.Datetime.to_string(datetime.today()+timedelta(days=15)),
            'website_menu':False,
        })
        self.assertFalse(event.menu_id)
        event.write({
            'website_menu':True,
            'community_menu':True,
            'website_track':True,
            'website_track_proposal':True,
        })
        self._assert_website_menus(event)
