#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimporttools
fromflectra.addons.crm.tests.commonimportTestCrmCommon
fromflectra.addons.event.tests.commonimportTestEventCommon


classTestEventCrmCommon(TestCrmCommon,TestEventCommon):

    @classmethod
    defsetUpClass(cls):
        super(TestEventCrmCommon,cls).setUpClass()

        #avoidclashwithexistingrules
        cls.env['event.lead.rule'].search([]).write({'active':False})

        cls.test_lead_tag=cls.env['crm.tag'].create({'name':'TagTest'})

        cls.test_rule_attendee=cls.env['event.lead.rule'].create({
            'name':'RuleAttendee',
            'lead_creation_basis':'attendee',
            'lead_creation_trigger':'create',
            'event_id':cls.event_0.id,
            'event_registration_filter':[['email','ilike','@test.example.com']],
            'lead_type':'lead',
            'lead_user_id':cls.user_sales_salesman.id,
            'lead_tag_ids':cls.test_lead_tag,
        })

        cls.test_rule_order=cls.env['event.lead.rule'].create({
            'name':'RuleOrder',
            'lead_creation_basis':'order',
            'lead_creation_trigger':'create',
            'event_id':cls.event_0.id,
            'event_registration_filter':[['email','ilike','@test.example.com']],
            'lead_type':'opportunity',
            'lead_user_id':cls.user_sales_leads.id,
            'lead_sales_team_id':cls.sales_team_1.id,
        })
        cls.test_rule_order_done=cls.env['event.lead.rule'].create({
            'name':'RuleOrder:confirmedpartneronly',
            'lead_creation_basis':'order',
            'lead_creation_trigger':'done',
            'event_registration_filter':[['partner_id','!=',False]],
            'lead_type':'opportunity',
        })

        cls.batch_customer_data=[{
            'partner_id':cls.event_customer.id,
        }]+[{
            'name':'MyCustomer00',
            'partner_id':cls.event_customer2.id,
            'email':'email.00@test.example.com',
            'phone':'0456000000',
        }]+[{
            'name':'MyCustomer%02d'%x,
            'partner_id':cls.env.ref('base.public_partner').idifx==0elseFalse,
            'email':'email.%02d@test.example.com'%x,
            'phone':'04560000%02d'%x,
        } forxinrange(1,4)]

    defassertLeadConvertion(self,rule,registrations,partner=None,**expected):
        """Toolmethodhidingdetailsofleadvaluegenerationandcheck

        :paramlead:leadcreatedthroughautomatedrule;
        :paramrule:event.lead.rulethatcreatedthelead;
        :paramevent:originalevent;
        :paramregistrations:sourceregistrations(singletonorrecordsetifdoneinbatch);
        :parampartner:partneronlead;
        """
        registrations=registrations.sorted('id') #currentlyorderisforcedtoidASC
        lead=self.env['crm.lead'].sudo().search([
            ('registration_ids','in',registrations.ids),
            ('event_lead_rule_id','=',rule.id)
        ])
        self.assertEqual(len(lead),1,'Invalidregistrations->leadcreation,found%sleadswhereonly1isexpected.'%len(lead))
        self.assertEqual(lead.registration_ids,registrations,'Invalidregistrations->leadcreation,toomuchregistrationsonit.')
        event=registrations.event_id
        self.assertEqual(len(event),1,'Invalidregistrations->eventassertion,allregistrationsshouldbelongtosameevent')

        ifpartnerisNone:
            partner=self.env['res.partner']
        expected_reg_name=partner.nameorregistrations._find_first_notnull('name')orregistrations._find_first_notnull('email')
        ifpartner:
            expected_contact_name=partner.nameifnotpartner.is_companyelseFalse
            expected_partner_name=partner.nameifpartner.is_companyelseFalse
        else:
            expected_contact_name=registrations._find_first_notnull('name')
            expected_partner_name=False

        #eventinformation
        self.assertEqual(lead.event_id,event)
        self.assertEqual(lead.referred,event.name)

        #registrationinformation
        self.assertEqual(lead.partner_id,partner)
        self.assertEqual(lead.name,'%s-%s'%(event.name,expected_reg_name))
        self.assertNotIn('False',lead.name) #avoida"DearFalse"likeconstruct^^(thisassertisseriousandintended)

        self.assertEqual(lead.contact_name,expected_contact_name)
        self.assertEqual(lead.partner_name,expected_partner_name)
        self.assertEqual(lead.email_from,partner.emailifpartnerandpartner.emailelseregistrations._find_first_notnull('email'))
        self.assertEqual(lead.phone,partner.phoneifpartnerandpartner.phoneelseregistrations._find_first_notnull('phone'))
        self.assertEqual(lead.mobile,partner.mobileifpartnerandpartner.mobileelseregistrations._find_first_notnull('mobile'))

        #description:toimprove
        self.assertNotIn('False',lead.description) #avoida"DearFalse"likeconstruct^^(thisassertisseriousandintended)
        forregistrationinregistrations:
            ifregistration.name:
                self.assertIn(registration.name,lead.description)
            elifregistration.partner_id.name:
                self.assertIn(registration.partner_id.name,lead.description)
            ifregistration.email:
                iftools.email_normalize(registration.email)==registration.partner_id.email_normalized:
                    self.assertIn(registration.partner_id.email,lead.description)
                else:
                    self.assertIn(registration.email,lead.description)
            ifregistration.phone:
                self.assertIn(registration.phone,lead.description)

        #leadconfiguration
        self.assertEqual(lead.type,rule.lead_type)
        self.assertEqual(lead.user_id,rule.lead_user_id)
        self.assertEqual(lead.team_id,rule.lead_sales_team_id)
        self.assertEqual(lead.tag_ids,rule.lead_tag_ids)
