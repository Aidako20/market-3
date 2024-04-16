#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromdatetimeimportdatetime

fromflectra.tests.commonimportSavepointCase,new_test_user


classTestEventNotifications(SavepointCase):

    @classmethod
    defsetUpClass(cls):
        super().setUpClass()
        cls.event=cls.env['calendar.event'].create({
            'name':"Doom'sday",
            'start':datetime(2019,10,25,8,0),
            'stop':datetime(2019,10,27,18,0),
        }).with_context(mail_notrack=True)
        cls.user=new_test_user(cls.env,'xav',email='em@il.com',notification_type='inbox')
        cls.partner=cls.user.partner_id

    deftest_attendee_added(self):
        self.event.partner_ids=self.partner
        self.assertTrue(self.event.attendee_ids,"Itshouldhavecreatedanattendee")
        self.assertEqual(self.event.attendee_ids.partner_id,self.partner,"Itshouldbelinkedtothepartner")
        self.assertIn(self.partner,self.event.message_follower_ids.partner_id,"Heshouldbefolloweroftheevent")

    deftest_attendee_added_create(self):
        event=self.env['calendar.event'].create({
            'name':"Doom'sday",
            'start':datetime(2019,10,25,8,0),
            'stop':datetime(2019,10,27,18,0),
            'partner_ids':[(4,self.partner.id)],
        })
        self.assertTrue(event.attendee_ids,"Itshouldhavecreatedanattendee")
        self.assertEqual(event.attendee_ids.partner_id,self.partner,"Itshouldbelinkedtothepartner")
        self.assertIn(self.partner,event.message_follower_ids.partner_id,"Heshouldbefolloweroftheevent")

    deftest_attendee_added_create_with_specific_states(self):
        """
        Whenaneventiscreatedfromanexternalcalendaraccount(suchasGoogle)whichisnotlinkedtoan
        Flectraaccount,attendeeinfosuchasemailandstatearegivenatsync.
        Inthiscase,attendee_idsshouldbecreatedaccordingly.
        """
        organizer_partner=self.env['res.partner'].create({'name':"orga","email":"orga@google.com"})
        event=self.env['calendar.event'].with_user(self.user).create({
            'name':"Doom'sday",
            'start':datetime(2019,10,25,8,0),
            'stop':datetime(2019,10,27,18,0),
            'attendee_ids':[
                (0,0,{'partner_id':self.partner.id,'state':'needsAction'}),
                (0,0,{'partner_id':organizer_partner.id,'state':'accepted'})
            ],
            'partner_ids':[(4,self.partner.id),(4,organizer_partner.id)],
        })
        attendees_info=[(a.email,a.state)forainevent.attendee_ids]
        self.assertEqual(len(event.attendee_ids),2)
        self.assertIn((self.partner.email,"needsAction"),attendees_info)
        self.assertIn((organizer_partner.email,"accepted"),attendees_info)

    deftest_attendee_added_multi(self):
        event=self.env['calendar.event'].create({
            'name':"Doom'sday",
            'start':datetime(2019,10,25,8,0),
            'stop':datetime(2019,10,27,18,0),
        })
        events=self.event|event
        events.partner_ids=self.partner
        self.assertEqual(len(events.attendee_ids),2,"Itshouldhavecreatedoneattendeeperevent")

    deftest_existing_attendee_added(self):
        self.event.partner_ids=self.partner
        attendee=self.event.attendee_ids
        self.event.write({'partner_ids':[(4,self.partner.id)]}) #Addexistingpartner
        self.assertEqual(self.event.attendee_ids,attendee,"Itshouldnothavecreatedannewattendeerecord")

    deftest_attendee_add_self(self):
        self.event.with_user(self.user).partner_ids=self.partner
        self.assertTrue(self.event.attendee_ids,"Itshouldhavecreatedanattendee")
        self.assertEqual(self.event.attendee_ids.partner_id,self.partner,"Itshouldbelinkedtothepartner")
        self.assertEqual(self.event.attendee_ids.state,'accepted',"Itshouldbeacceptedforthecurrentuser")

    deftest_attendee_removed(self):
        partner_bis=self.env['res.partner'].create({'name':"Xavier"})
        self.event.partner_ids=partner_bis
        attendee=self.event.attendee_ids
        self.event.partner_ids|=self.partner
        self.event.partner_ids-=self.partner
        self.assertEqual(attendee,self.event.attendee_ids,"Itshouldnothavere-createdanattendeerecord")
        self.assertNotIn(self.partner,self.event.attendee_ids.partner_id,"Itshouldhaveremovedtheattendee")
        self.assertNotIn(self.partner,self.event.message_follower_ids.partner_id,"Itshouldhaveunsubscribedthepartner")
        self.assertIn(partner_bis,self.event.attendee_ids.partner_id,"Itshouldhavelefttheattendee")

    deftest_default_attendee(self):
        """
        Checkifprioritylistidcorrectlyfollowed
        1)vals_list[0]['attendee_ids']
        2)vals_list[0]['partner_ids']
        3)context.get('default_attendee_ids')
        """
        partner_bis=self.env['res.partner'].create({'name':"Xavier"})
        event=self.env['calendar.event'].with_user(
            self.user
        ).with_context(
            default_attendee_ids=[(0,0,{'partner_id':partner_bis.id})]
        ).create({
            'name':"Doom'sday",
            'partner_ids':[(4,self.partner.id)],
            'start':datetime(2019,10,25,8,0),
            'stop':datetime(2019,10,27,18,0),
        })
        self.assertIn(self.partner,event.attendee_ids.partner_id,"Partnershouldbeinattendee")
        self.assertNotIn(partner_bis,event.attendee_ids.partner_id,"Partnerbisshouldnotbeinattendee")

    deftest_default_attendee_2(self):
        """
        Checkifprioritylistidcorrectlyfollowed
        1)vals_list[0]['attendee_ids']
        2)vals_list[0]['partner_ids']
        3)context.get('default_attendee_ids')
        """
        partner_bis=self.env['res.partner'].create({'name':"Xavier"})
        event=self.env['calendar.event'].with_user(
            self.user
        ).with_context(
            default_attendee_ids=[(0,0,{'partner_id':partner_bis.id})]
        ).create({
            'name':"Doom'sday",
            'start':datetime(2019,10,25,8,0),
            'stop':datetime(2019,10,27,18,0),
        })
        self.assertNotIn(self.partner,event.attendee_ids.partner_id,"Partnershouldnotbeinattendee")
        self.assertIn(partner_bis,event.attendee_ids.partner_id,"Partnerbisshouldbeinattendee")
