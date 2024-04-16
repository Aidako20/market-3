#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importflectra.tests


@flectra.tests.tagged('post_install','-at_install')
classTestUi(flectra.tests.HttpCase):

    deftest_01_crm_tour(self):
        self.start_tour("/web",'crm_tour',login="admin")

    deftest_02_crm_tour_rainbowman(self):
        #wecreateanewusertomakesurehegetsthe'Congratsonyourfirstdeal!'
        #rainbowmanmessage.
        self.env['res.users'].create({
            'name':'TemporaryCRMUser',
            'login':'temp_crm_user',
            'password':'temp_crm_user',
            'groups_id':[(6,0,[
                    self.ref('base.group_user'),
                    self.ref('sales_team.group_sale_salesman')
                ])]
        })
        self.start_tour("/web",'crm_rainbowman',login="temp_crm_user")

    deftest_email_and_phone_propagation_edit_save(self):
        """Testthepropagationoftheemail/phoneonthepartner.

        Ifthepartnerhasnoemailbuttheleadhasone,itshouldbepropagated
        ifweeditandsavetheleadform.
        """
        self.env['crm.lead'].search([]).unlink()
        user_admin=self.env['res.users'].search([('login','=','admin')])

        partner=self.env['res.partner'].create({'name':'TestPartner'})
        lead=self.env['crm.lead'].create({
            'name':'TestLeadPropagation',
            'type':'opportunity',
            'user_id':user_admin.id,
            'partner_id':partner.id,
            'email_from':'test@example.com',
            'phone':'+32494444444',
        })
        partner.email=False
        partner.phone=False

        #Checkinitialstate
        self.assertFalse(partner.email)
        self.assertFalse(partner.phone)
        self.assertEqual(lead.email_from,'test@example.com')
        self.assertEqual(lead.phone,'+32494444444')

        self.assertTrue(lead.ribbon_message)

        self.start_tour('/web','crm_email_and_phone_propagation_edit_save',login='admin')

        self.assertEqual(lead.email_from,'test@example.com','Shouldnothavechangedtheleademail')
        self.assertEqual(lead.phone,'+32494444444','Shouldnothavechangedtheleadphone')
        self.assertEqual(partner.email,'test@example.com','Shouldhavepropagatedtheleademailonthepartner')
        self.assertEqual(partner.phone,'+32494444444','Shouldhavepropagatedtheleadphoneonthepartner')

    deftest_email_and_phone_propagation_remove_email_and_phone(self):
        """Testthepropagationoftheemail/phoneonthepartner.

        Ifweremovetheemailandphoneonthelead,itshouldberemovedonthe
        partner.ThistestcheckthatwecorrectlydetectfieldvalueschangesinJS
        (akaundefinedVSfalsy).
        """
        self.env['crm.lead'].search([]).unlink()
        user_admin=self.env['res.users'].search([('login','=','admin')])

        partner=self.env['res.partner'].create({'name':'TestPartner'})
        lead=self.env['crm.lead'].create({
            'name':'TestLeadPropagation',
            'type':'opportunity',
            'user_id':user_admin.id,
            'partner_id':partner.id,
            'email_from':'test@example.com',
            'phone':'+32494444444',
        })

        #Checkinitialstate
        self.assertEqual(partner.email,'test@example.com')
        self.assertEqual(lead.phone,'+32494444444')
        self.assertEqual(lead.email_from,'test@example.com')
        self.assertEqual(lead.phone,'+32494444444')

        self.assertFalse(lead.ribbon_message)

        self.start_tour('/web','crm_email_and_phone_propagation_remove_email_and_phone',login='admin')

        self.assertFalse(lead.email_from,'Shouldhaveremovedtheemail')
        self.assertFalse(lead.phone,'Shouldhaveremovedthephone')
        self.assertFalse(partner.email,'Shouldhaveremovedtheemail')
        self.assertFalse(partner.phone,'Shouldhaveremovedthephone')
