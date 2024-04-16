#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.addons.phone_validation.toolsimportphone_validation
fromflectra.addons.mass_mailing_sms.tests.commonimportMassSMSCommon
fromflectra.addons.test_mail.tests.commonimportTestRecipients
fromflectra.addons.test_mass_mailing.tests.commonimportTestMassMailCommon


classTestMailFullCommon(TestMassMailCommon,MassSMSCommon):

    @classmethod
    defsetUpClass(cls):
        super(TestMailFullCommon,cls).setUpClass()

        cls.mailing_sms=cls.env['mailing.mailing'].with_user(cls.user_marketing).create({
            'name':'XMasSMS',
            'subject':'XmasSMSfor{object.name}',
            'mailing_model_id':cls.env['ir.model']._get('mail.test.sms').id,
            'mailing_type':'sms',
            'mailing_domain':'%s'%repr([('name','ilike','SMSTest')]),
            'body_plaintext':'Dear${object.display_name}thisisamassSMSwithtwolinkshttp://www.flectrahq.com/smstestandhttp://www.flectrahq.com/smstest/${object.id}',
            'sms_force_send':True,
            'sms_allow_unsubscribe':True,
        })

    @classmethod
    def_create_mailing_sms_test_records(cls,model='mail.test.sms',partners=None,count=1):
        """Helpertocreatedata.Currentlysimple,tobeimproved."""
        Model=cls.env[model]
        phone_field='phone_nbr'if'phone_nbr'inModelelse'phone'
        partner_field='customer_id'if'customer_id'inModelelse'partner_id'

        vals_list=[]
        foridxinrange(count):
            vals={
                'name':'SMSTestRecord_%02d'%idx,
                phone_field:'045600%02d%02d'%(idx,idx)
            }
            ifpartners:
                vals[partner_field]=partners[idx%len(partners)]

            vals_list.append(vals)

        returncls.env[model].create(vals_list)


classTestRecipients(TestRecipients):

    @classmethod
    defsetUpClass(cls):
        super(TestRecipients,cls).setUpClass()
        cls.partner_numbers=[
            phone_validation.phone_format(partner.mobile,partner.country_id.code,partner.country_id.phone_code,force_format='E164')
            forpartnerin(cls.partner_1|cls.partner_2)
        ]
