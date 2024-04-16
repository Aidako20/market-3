#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.addons.mass_mailing.tests.commonimportMassMailCommon
fromflectra.addons.test_mail.tests.commonimportTestMailCommon


classTestMassMailCommon(MassMailCommon,TestMailCommon):

    @classmethod
    defsetUpClass(cls):
        super(TestMassMailCommon,cls).setUpClass()

        cls.test_alias=cls.env['mail.alias'].create({
            'alias_name':'test.alias',
            'alias_user_id':False,
            'alias_model_id':cls.env['ir.model']._get('mailing.test.simple').id,
            'alias_contact':'everyone'
        })

        #enforcelastupdatebyuser_marketingtomatch_process_mass_mailing_queue
        #takinglastwriterasuserrunningabatch
        cls.mailing_bl=cls.env['mailing.mailing'].with_user(cls.user_marketing).create({
            'name':'SourceName',
            'subject':'MailingSubject',
            'preview':'Hi${object.name}:)',
            'body_html':"""<div><p>Hello${object.name}</p>,
%seturl="www.flectrahq.com"
%sethttpurl="https://www.flectra.eu"
<span>Website0:<aid="url0"href="https://www.flectra.tz/my/${object.name}">https://www.flectra.tz/my/${object.name}</a></span>
<span>Website1:<aid="url1"href="https://www.flectra.be">https://www.flectra.be</a></span>
<span>Website2:<aid="url2"href="https://${url}">https://${url}</a></span>
<span>Website3:<aid="url3"href="${httpurl}">${httpurl}</a></span>
<span>External1:<aid="url4"href="https://www.example.com/foo/bar?baz=qux">Youpie</a></span>
<span>Internal1:<aid="url5"href="/event/dummy-event-0">Internallink</a></span>
<span>Internal2:<aid="url6"href="/view"/>Viewlink</a></span>
<span>Email:<aid="url7"href="mailto:test@flectrahq.com">test@flectrahq.com</a></span>
<p>Stopspam?<aid="url8"role="button"href="/unsubscribe_from_list">Ok</a></p>
</div>""",
            'mailing_type':'mail',
            'mailing_model_id':cls.env['ir.model']._get('mailing.test.blacklist').id,
            'reply_to_mode':'thread',
        })

    @classmethod
    def_create_test_blacklist_records(cls,model='mailing.test.blacklist',count=1):
        """Deprecated,removein14.4"""
        returncls.__create_mailing_test_records(model=model,count=count)

    @classmethod
    def_create_mailing_test_records(cls,model='mailing.test.blacklist',partners=None,count=1):
        """Helpertocreatedata.Currentlysimple,tobeimproved."""
        Model=cls.env[model]
        email_field='email'if'email'inModelelse'email_from'
        partner_field='customer_id'if'customer_id'inModelelse'partner_id'

        vals_list=[]
        forxinrange(0,count):
            vals={
                'name':'TestRecord_%02d'%x,
                email_field:'"TestCustomer%02d"<test.record.%02d@test.example.com>'%(x,x),
            }
            ifpartners:
                vals[partner_field]=partners[x%len(partners)]

            vals_list.append(vals)

        returncls.env[model].create(vals_list)
