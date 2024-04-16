#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectra.tests.commonimportBaseCase
fromflectra.addons.google_calendar.utils.google_calendarimportGoogleEvent


classTestGoogleEvent(BaseCase):
    deftest_google_event_readonly(self):
        event=GoogleEvent()
        withself.assertRaises(TypeError):
            event._events['foo']='bar'
        withself.assertRaises(AttributeError):
            event._events.update({'foo':'bar'})
        withself.assertRaises(TypeError):
            dict.update(event._events,{'foo':'bar'})
