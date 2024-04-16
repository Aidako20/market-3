#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromastimportliteral_eval

fromflectra.addons.mass_mailing_sms.tests.commonimportMassSMSCommon
fromflectra.tests.commonimportusers


classTestMassMailValues(MassSMSCommon):

    @classmethod
    defsetUpClass(cls):
        super(TestMassMailValues,cls).setUpClass()

        cls._create_mailing_list()
        cls.sms_template_partner=cls.env['sms.template'].create({
            'name':'TestTemplate',
            'model_id':cls.env['ir.model']._get('res.partner').id,
            'body':'Dear${object.display_name}thisisanSMS.'
        })

    @users('user_marketing')
    deftest_mailing_computed_fields(self):
        #Createonres.partner,withdefaultvaluesforcomputedfields
        mailing=self.env['mailing.mailing'].create({
            'name':'TestMailing',
            'subject':'Test',
            'mailing_type':'sms',
            'body_plaintext':'Coucouhibou',
            'mailing_model_id':self.env['ir.model']._get('res.partner').id,
        })
        self.assertEqual(mailing.user_id,self.user_marketing)
        self.assertEqual(mailing.body_plaintext,'Coucouhibou')
        self.assertEqual(mailing.medium_id,self.env.ref('mass_mailing_sms.utm_medium_sms'))
        self.assertEqual(mailing.mailing_model_name,'res.partner')
        self.assertEqual(mailing.mailing_model_real,'res.partner')
        #defaultforpartner:removeblacklisted
        self.assertEqual(literal_eval(mailing.mailing_domain),[('phone_sanitized_blacklisted','=',False)])
        #updatetemplate->updatebody
        mailing.write({'sms_template_id':self.sms_template_partner.id})
        self.assertEqual(mailing.body_plaintext,self.sms_template_partner.body)
        #updatedomain
        mailing.write({
            'mailing_domain':[('email','ilike','test.example.com')]
        })
        self.assertEqual(literal_eval(mailing.mailing_domain),[('email','ilike','test.example.com')])

        #resetmailingmodel->resetdomain;setreply_to->keepit
        mailing.write({
            'mailing_model_id':self.env['ir.model']._get('mailing.list').id,
            'reply_to':self.email_reply_to,
        })
        self.assertEqual(mailing.mailing_model_name,'mailing.list')
        self.assertEqual(mailing.mailing_model_real,'mailing.contact')
        #defaultformailinglist:dependsuponcontact_list_ids
        self.assertEqual(literal_eval(mailing.mailing_domain),[])
        mailing.write({
            'contact_list_ids':[(4,self.mailing_list_1.id),(4,self.mailing_list_2.id)]
        })
        self.assertEqual(literal_eval(mailing.mailing_domain),[('list_ids','in',(self.mailing_list_1|self.mailing_list_2).ids)])
