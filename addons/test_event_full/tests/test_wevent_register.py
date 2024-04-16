#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimporttests
fromflectra.addons.test_event_full.tests.commonimportTestWEventCommon
fromflectra.tests.commonimportHOST


@tests.common.tagged('post_install','-at_install')
classTestWEventRegister(TestWEventCommon):

    deftest_register(self):
        self.browser_js(
            '/event',
            'flectra.__DEBUG__.services["web_tour.tour"].run("wevent_register")',
            'flectra.__DEBUG__.services["web_tour.tour"].tours.wevent_register.ready',
            login=None
        )
        new_registrations=self.event.registration_ids
        visitor=new_registrations.visitor_id

        #checkregistrationcontent
        self.assertEqual(len(new_registrations),2)
        self.assertEqual(
            set(new_registrations.mapped("name")),
            set(["RaoulettePoiluchette","MichelTractopelle"])
        )
        self.assertEqual(
            set(new_registrations.mapped("phone")),
            set(["0456112233","0456332211"])
        )
        self.assertEqual(
            set(new_registrations.mapped("email")),
            set(["raoulette@example.com","michel@example.com"])
        )

        #checkvisitorstoredinformation
        self.assertEqual(visitor.name,"RaoulettePoiluchette")
        self.assertEqual(visitor.event_registration_ids,new_registrations)
        self.assertEqual(visitor.partner_id,self.env['res.partner'])
        self.assertEqual(visitor.mobile,"0456112233")
        self.assertEqual(visitor.email,"raoulette@example.com")
        self.assertFalse(visitor.parent_id)
        self.assertTrue(visitor.active)
