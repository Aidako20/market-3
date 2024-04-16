#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.addons.website_slides.testsimportcommon


classTestAttendee(common.SlidesCase):

    deftest_course_attendee_copy(self):
        """Tocheckmembersofthechannelafterduplicationofcontact"""
        #Addingattendee
        self.channel._action_add_members(self.customer)
        self.channel.invalidate_cache()

        #Attendeecountbeforecopyofcontact
        attendee_before=self.env['slide.channel.partner'].search_count([])

        #Duplicatingthecontact
        self.customer.copy()

        #Attendeecountaftercopyofcontact
        attendee_after=self.env['slide.channel.partner'].search_count([])
        self.assertEqual(attendee_before,attendee_after,"Duplicatingthecontactshouldnotcreateanewattendee")
