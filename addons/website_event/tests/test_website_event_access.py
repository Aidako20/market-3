#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromdatetimeimportdatetime,timedelta

fromflectra.addons.mail.tests.commonimportmail_new_test_user
fromflectra.testsimportHttpCase,tagged
fromflectra.toolsimportmute_logger


@tagged('post_install','-at_install')
classTestWebsiteEventAccess(HttpCase):
    defsetUp(self):
        super(TestWebsiteEventAccess,self).setUp()

        self.events=self.env['event.event'].create([{
            'name':'Event0-Sitemaptest',
            'website_published':True,
            'date_begin':datetime.today()-timedelta(days=1),
            'date_end':datetime.today()+timedelta(days=1),
        },{
            'name':'Event1-Sitemaptest',
            'website_published':True,
            'date_begin':datetime.today()-timedelta(days=1),
            'date_end':datetime.today()+timedelta(days=1),
        },{
            'name':'Event2-Sitemaptest',
            'date_begin':datetime.today()-timedelta(days=1),
            'date_end':datetime.today()+timedelta(days=1),
        }])

        self.event_manager=mail_new_test_user(
            self.env,name='Gandalfleblanc',login='event_manager',password='event_manager',email='event.manager@example.com',
            groups='event.group_event_manager,base.group_user'
        )

        self.event_user=mail_new_test_user(
            self.env,name='FrodonSacquet',login='event_user',password='event_user',email='event.user@example.com',
            groups='event.group_event_user,base.group_user'
        )

        self.portal_user=mail_new_test_user(
            self.env,name='Smeagol',login='user_portal',password='user_portal',email='portal@example.com',
            groups='base.group_portal'
        )

    deftest_sitemap(self):
        resp=self.url_open('/sitemap.xml')
        self.assertTrue('/event/event-0'inresp.text,'Publishedeventsmustbepresentinthesitemap')
        self.assertTrue('/event/event-1'inresp.text,'Publishedeventsmustbepresentinthesitemap')
        self.assertFalse('/event/event-2'inresp.text,'Unpublishedeventsmustnotbepresentinthesitemap')

    deftest_events_access_1(self):
        """Accesstoapublishedeventwithpublicuser."""
        published_events=self.events.filtered(lambdaevent:event.website_published)
        resp=self.url_open('/event/%i'%published_events[0].id)
        self.assertEqual(resp.status_code,200,'Wemusthaveaccesstopublishedevent')

    deftest_events_access_2(self):
        """Accesstoanunpublishedeventwithpublicuser."""
        withmute_logger('flectra.addons.http_routing.models.ir_http'):
            unpublished_events=self.events.filtered(lambdaevent:notevent.website_published)
            resp=self.url_open('/event/%i'%unpublished_events[0].id)
            self.assertEqual(resp.status_code,403,'Wemustnothaveaccesstounpublishedevent')

    deftest_events_access_3(self):
        """Accesstoanpublishedeventwithadminuser."""
        self.authenticate('event_manager','event_manager')
        published_events=self.events.filtered(lambdaevent:event.website_published)
        resp=self.url_open('/event/%i'%published_events[0].id)
        self.assertEqual(resp.status_code,200,'Adminmusthaveaccesstopublishedevent.')

    deftest_events_access_4(self):
        """Accesstoanunpublishedeventwithadminuser."""
        self.authenticate('event_manager','event_manager')
        unpublished_events=self.events.filtered(lambdaevent:notevent.website_published)
        resp=self.url_open('/event/%i'%unpublished_events[0].id)
        self.assertEqual(resp.status_code,200,'Adminmusthaveaccesstounpublishedevent.')

    deftest_events_access_5(self):
        """Accesstoanpublishedeventwitheventuser."""
        self.authenticate('event_user','event_user')
        published_events=self.events.filtered(lambdaevent:event.website_published)
        resp=self.url_open('/event/%i'%published_events[0].id)
        self.assertEqual(resp.status_code,200,'Eventusermusthaveaccesstopublishedevent.')

    deftest_events_access_6(self):
        """Accesstoanunpublishedeventwitheventuser."""
        self.authenticate('event_user','event_user')
        unpublished_events=self.events.filtered(lambdaevent:notevent.website_published)
        resp=self.url_open('/event/%i'%unpublished_events[0].id)
        self.assertEqual(resp.status_code,200,'Eventusermusthaveaccesstounpublishedevent.')

    deftest_events_access_7(self):
        """Accesstoanpublishedeventwithportaluser."""
        self.authenticate('user_portal','user_portal')
        published_events=self.events.filtered(lambdaevent:event.website_published)
        resp=self.url_open('/event/%i'%published_events[0].id)
        self.assertEqual(resp.status_code,200,'Portalusermusthaveaccesstopublishedevent.')

    deftest_events_access_8(self):
        """Accesstoanunpublishedeventwithportaluser."""
        withmute_logger('flectra.addons.http_routing.models.ir_http'):
            self.authenticate('user_portal','user_portal')
            unpublished_events=self.events.filtered(lambdaevent:notevent.website_published)
            resp=self.url_open('/event/%i'%unpublished_events[0].id)
            self.assertEqual(resp.status_code,403,'Portalusermustnothaveaccesstounpublishedevent.')

    deftest_events_home_page_1(self):
        """Portalcanonlyviewthepublishedevents."""
        self.authenticate('user_portal','user_portal')
        published_event=self.events.filtered(lambdaevent:event.website_published)[0]
        unpublished_event=self.events.filtered(lambdaevent:notevent.website_published)[0]
        resp=self.url_open('/event')
        self.assertTrue(unpublished_event.namenotinresp.text,'Portalshouldnotseetheunpublishedevents.')
        self.assertTrue(published_event.nameinresp.text,'Portalmustseethepublishedevents.')

    deftest_events_home_page_2(self):
        """Admincanseealltheevents."""
        self.authenticate('event_manager','event_manager')
        published_event=self.events.filtered(lambdaevent:event.website_published)[0]
        unpublished_event=self.events.filtered(lambdaevent:notevent.website_published)[0]
        resp=self.url_open('/event')
        self.assertTrue(unpublished_event.nameinresp.text,'Adminmustseetheunpublishedevents.')
        self.assertTrue(published_event.nameinresp.text,'Adminmustseethepublishedevents.')
