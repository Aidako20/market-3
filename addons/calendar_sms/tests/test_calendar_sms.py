#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromdatetimeimportdatetime

fromflectra.tests.commonimportSingleTransactionCase


classTestCalendarSms(SingleTransactionCase):

    @classmethod
    defsetUpClass(cls):
        super(TestCalendarSms,cls).setUpClass()

        cls.partner_phone=cls.env['res.partner'].create({
            'name':'PartnerWithPhoneNumber',
            'phone':'0477777777',
            'country_id':cls.env.ref('base.be').id,
        })
        cls.partner_no_phone=cls.env['res.partner'].create({
            'name':'PartnerWithNoPhoneNumber',
            'country_id':cls.env.ref('base.be').id,
        })

    deftest_attendees_with_number(self):
        """Testifonlypartnerswithsanitizednumberarereturned."""
        attendees=self.env['calendar.event'].create({
            'name':"BoostrapvsFoundation",
            'start':datetime(2022,1,1,11,11),
            'stop':datetime(2022,2,2,22,22),
            'partner_ids':[(6,0,[self.partner_phone.id,self.partner_no_phone.id])],
        })._sms_get_default_partners()
        self.assertEqual(len(attendees),1,"Thereshouldbeonlyonepartnerretrieved")
