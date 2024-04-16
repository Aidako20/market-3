#-*-coding:utf-8-*-
fromflectra.addons.account.tests.commonimportAccountTestInvoicingCommon
fromflectra.testsimporttagged

importjson


@tagged('post_install','-at_install')
classTestAccountIncomingSupplierInvoice(AccountTestInvoicingCommon):

    @classmethod
    defsetUpClass(cls,chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

        cls.env['ir.config_parameter'].sudo().set_param('mail.catchall.domain','test-company.flectrahq.com')

        cls.internal_user=cls.env['res.users'].create({
            'name':'InternalUser',
            'login':'internal.user@test.flectrahq.com',
            'email':'internal.user@test.flectrahq.com',
        })

        cls.supplier_partner=cls.env['res.partner'].create({
            'name':'YourSupplier',
            'email':'supplier@other.company.com',
            'supplier_rank':10,
        })

        cls.journal=cls.company_data['default_journal_purchase']

        journal_alias=cls.env['mail.alias'].create({
            'alias_name':'test-bill',
            'alias_model_id':cls.env.ref('account.model_account_move').id,
            'alias_defaults':json.dumps({
                'move_type':'in_invoice',
                'company_id':cls.env.user.company_id.id,
                'journal_id':cls.journal.id,
            }),
        })
        cls.journal.write({'alias_id':journal_alias.id})

    deftest_supplier_invoice_mailed_from_supplier(self):
        message_parsed={
            'message_id':'message-id-dead-beef',
            'subject':'Incomingbill',
            'from':'%s<%s>'%(self.supplier_partner.name,self.supplier_partner.email),
            'to':'%s@%s'%(self.journal.alias_id.alias_name,self.journal.alias_id.alias_domain),
            'body':"Youknow,thatthingthatyoubought.",
            'attachments':[b'Hello,invoice'],
        }

        invoice=self.env['account.move'].message_new(message_parsed,{'move_type':'in_invoice','journal_id':self.journal.id})

        message_ids=invoice.message_ids
        self.assertEqual(len(message_ids),1,'Onlyonemessageshouldbepostedinthechatter')
        self.assertEqual(message_ids.body,'<p>VendorBillCreated</p>','Onlytheinvoicecreationshouldbeposted')

        following_partners=invoice.message_follower_ids.mapped('partner_id')
        self.assertEqual(following_partners,self.env.user.partner_id)
        self.assertRegex(invoice.name,'BILL/\d{4}/\d{2}/0001')

    deftest_supplier_invoice_forwarded_by_internal_user_without_supplier(self):
        """Inthistest,thebillwasforwardedbyanemployee,
            butnopartneremailaddressisfoundinthebody."""
        message_parsed={
            'message_id':'message-id-dead-beef',
            'subject':'Incomingbill',
            'from':'%s<%s>'%(self.internal_user.name,self.internal_user.email),
            'to':'%s@%s'%(self.journal.alias_id.alias_name,self.journal.alias_id.alias_domain),
            'body':"Youknow,thatthingthatyoubought.",
            'attachments':[b'Hello,invoice'],
        }

        invoice=self.env['account.move'].message_new(message_parsed,{'move_type':'in_invoice','journal_id':self.journal.id})

        message_ids=invoice.message_ids
        self.assertEqual(len(message_ids),1,'Onlyonemessageshouldbepostedinthechatter')
        self.assertEqual(message_ids.body,'<p>VendorBillCreated</p>','Onlytheinvoicecreationshouldbeposted')

        following_partners=invoice.message_follower_ids.mapped('partner_id')
        self.assertEqual(following_partners,self.env.user.partner_id|self.internal_user.partner_id)

    deftest_supplier_invoice_forwarded_by_internal_with_supplier_in_body(self):
        """Inthistest,thebillwasforwardedbyanemployee,
            andthepartneremailaddressisfoundinthebody."""
        message_parsed={
            'message_id':'message-id-dead-beef',
            'subject':'Incomingbill',
            'from':'%s<%s>'%(self.internal_user.name,self.internal_user.email),
            'to':'%s@%s'%(self.journal.alias_id.alias_name,self.journal.alias_id.alias_domain),
            'body':"Mailsentby%s<%s>:\nYouknow,thatthingthatyoubought."%(self.supplier_partner.name,self.supplier_partner.email),
            'attachments':[b'Hello,invoice'],
        }

        invoice=self.env['account.move'].message_new(message_parsed,{'move_type':'in_invoice','journal_id':self.journal.id})

        message_ids=invoice.message_ids
        self.assertEqual(len(message_ids),1,'Onlyonemessageshouldbepostedinthechatter')
        self.assertEqual(message_ids.body,'<p>VendorBillCreated</p>','Onlytheinvoicecreationshouldbeposted')

        following_partners=invoice.message_follower_ids.mapped('partner_id')
        self.assertEqual(following_partners,self.env.user.partner_id|self.internal_user.partner_id)

    deftest_supplier_invoice_forwarded_by_internal_with_internal_in_body(self):
        """Inthistest,thebillwasforwardedbyanemployee,
            andtheinternaluseremailaddressisfoundinthebody."""
        message_parsed={
            'message_id':'message-id-dead-beef',
            'subject':'Incomingbill',
            'from':'%s<%s>'%(self.internal_user.name,self.internal_user.email),
            'to':'%s@%s'%(self.journal.alias_id.alias_name,self.journal.alias_id.alias_domain),
            'body':"Mailsentby%s<%s>:\nYouknow,thatthingthatyoubought."%(self.internal_user.name,self.internal_user.email),
            'attachments':[b'Hello,invoice'],
        }

        invoice=self.env['account.move'].message_new(message_parsed,{'move_type':'in_invoice','journal_id':self.journal.id})

        message_ids=invoice.message_ids
        self.assertEqual(len(message_ids),1,'Onlyonemessageshouldbepostedinthechatter')
        self.assertEqual(message_ids.body,'<p>VendorBillCreated</p>','Onlytheinvoicecreationshouldbeposted')

        following_partners=invoice.message_follower_ids.mapped('partner_id')
        self.assertEqual(following_partners,self.env.user.partner_id|self.internal_user.partner_id)
