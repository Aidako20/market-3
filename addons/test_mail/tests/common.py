#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.addons.mail.tests.commonimportMailCommon
fromflectra.tests.commonimportSavepointCase


classTestMailCommon(MailCommon):
    """Mainentrypointforfunctionaltests."""

    @classmethod
    def_create_channel_listener(cls):
        cls.channel_listen=cls.env['mail.channel'].with_context(cls._test_context).create({'name':'Listener'})

    @classmethod
    def_create_records_for_batch(cls,model,count):
        #TDEnote:tobecleanedinmaster
        records=cls.env[model]
        partners=cls.env['res.partner']
        country_id=cls.env.ref('base.be').id

        partners=cls.env['res.partner'].with_context(**cls._test_context).create([{
            'name':'Partner_%s'%(x),
            'email':'_test_partner_%s@example.com'%(x),
            'country_id':country_id,
            'mobile':'047500%02d%02d'%(x,x)
        }forxinrange(count)])

        records=cls.env[model].with_context(**cls._test_context).create([{
            'name':'Test_%s'%(x),
            'customer_id':partners[x].id,
        }forxinrange(count)])

        cls.records=cls._reset_mail_context(records)
        cls.partners=partners
        returncls.records,cls.partners


classTestMailMultiCompanyCommon(MailCommon):

    @classmethod
    defsetUpClass(cls):
        super(TestMailMultiCompanyCommon,cls).setUpClass()
        cls.company_2=cls.env['res.company'].create({
            'name':'SecondTestCompany',
        })


classTestRecipients(SavepointCase):

    @classmethod
    defsetUpClass(cls):
        super(TestRecipients,cls).setUpClass()
        Partner=cls.env['res.partner'].with_context({
            'mail_create_nolog':True,
            'mail_create_nosubscribe':True,
            'mail_notrack':True,
            'no_reset_password':True,
        })
        cls.partner_1=Partner.create({
            'name':'ValidLelitre',
            'email':'valid.lelitre@agrolait.com',
            'country_id':cls.env.ref('base.be').id,
            'mobile':'0456001122',
        })
        cls.partner_2=Partner.create({
            'name':'ValidPoilvache',
            'email':'valid.other@gmail.com',
            'country_id':cls.env.ref('base.be').id,
            'mobile':'+32456221100',
        })
