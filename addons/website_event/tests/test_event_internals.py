#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromdatetimeimportdatetime,timedelta

fromflectraimportfields
fromflectra.addons.website_event.tests.commonimportTestWebsiteEventCommon
fromflectra.tests.commonimportusers


classTestEventWebsite(TestWebsiteEventCommon):

    @users('user_eventmanager')
    deftest_menu_create(self):
        event=self.env['event.event'].create({
            'name':'TestEvent',
            'date_begin':fields.Datetime.to_string(datetime.today()+timedelta(days=1)),
            'date_end':fields.Datetime.to_string(datetime.today()+timedelta(days=15)),
            'website_menu':True,
            'community_menu':False,
        })
        self._assert_website_menus(event)

    @users('user_event_web_manager')
    deftest_menu_management_frontend(self):
        event=self.env['event.event'].create({
            'name':'TestEvent',
            'date_begin':fields.Datetime.to_string(datetime.today()+timedelta(days=1)),
            'date_end':fields.Datetime.to_string(datetime.today()+timedelta(days=15)),
            'website_menu':True,
            'community_menu':False,
        })
        self.assertTrue(event.website_menu)
        self._assert_website_menus(event)

        introduction_menu=event.menu_id.child_id.filtered(lambdamenu:menu.name=='Introduction')
        introduction_menu.unlink()

        self.assertTrue(event.website_menu)
        self._assert_website_menus(event,set(['Location','Register']))

    @users('user_eventmanager')
    deftest_menu_update(self):
        event=self.env['event.event'].browse(self.event_0.id)
        self.assertFalse(event.menu_id)
        event.website_menu=True
        self._assert_website_menus(event)
