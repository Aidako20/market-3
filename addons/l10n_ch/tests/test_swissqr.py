#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
importtime

fromflectra.addons.account.tests.commonimportAccountTestInvoicingCommon
fromflectra.testsimporttagged

CH_IBAN='CH1538815158384538437'
QR_IBAN='CH2130808001234567827'


@tagged('post_install','-at_install')
classTestSwissQR(AccountTestInvoicingCommon):

    @classmethod
    defsetUpClass(cls,chart_template_ref='l10n_ch.l10nch_chart_template'):
        super().setUpClass(chart_template_ref=chart_template_ref)

    defsetUp(self):
        super(TestSwissQR,self).setUp()
        #ActivateSwissQRinSwissinvoices
        self.env['ir.config_parameter'].create(
            {'key':'l10n_ch.print_qrcode','value':'1'}
        )
        self.customer=self.env['res.partner'].create(
            {
                "name":"Partner",
                "street":"RoutedeBerne41",
                "street2":"",
                "zip":"1000",
                "city":"Lausanne",
                "country_id":self.env.ref("base.ch").id,
            }
        )
        self.env.user.company_id.partner_id.write(
            {
                "street":"RoutedeBerne88",
                "street2":"",
                "zip":"2000",
                "city":"Neuchâtel",
                "country_id":self.env.ref('base.ch').id,
            }
        )
        self.invoice1=self.create_invoice('base.CHF')
        sale_journal=self.env['account.journal'].search([("type","=","sale")])
        sale_journal.invoice_reference_model="ch"

    defcreate_invoice(self,currency_to_use='base.CHF'):
        """Generatesatestinvoice"""

        product=self.env.ref("product.product_product_4")
        acc_type=self.env.ref('account.data_account_type_current_assets')
        account=self.env['account.account'].search(
            [('user_type_id','=',acc_type.id)],limit=1
        )
        invoice=(
            self.env['account.move']
            .create(
                {
                    'move_type':'out_invoice',
                    'partner_id':self.customer.id,
                    'currency_id':self.env.ref(currency_to_use).id,
                    'date':time.strftime('%Y')+'-12-22',
                    'invoice_line_ids':[
                        (
                            0,
                            0,
                            {
                                'name':product.name,
                                'product_id':product.id,
                                'account_id':account.id,
                                'quantity':1,
                                'price_unit':42.0,
                            },
                        )
                    ],
                }
            )
        )

        returninvoice

    defcreate_account(self,number):
        """Generatesatestres.partner.bank."""
        returnself.env['res.partner.bank'].create(
            {
                'acc_number':number,
                'partner_id':self.env.user.company_id.partner_id.id,
            }
        )

    defswissqr_not_generated(self,invoice):
        """PrintsthegiveninvoiceandteststhatnoSwissQRgenerationistriggered."""
        self.assertFalse(
            invoice.partner_bank_id._eligible_for_qr_code('ch_qr',invoice.partner_id,invoice.currency_id),
            'NoSwissQRshouldbegeneratedforthisinvoice',
        )

    defswissqr_generated(self,invoice,ref_type='NON'):
        """PrintsthegiveninvoiceandteststhataSwissQRgenerationistriggered."""
        self.assertTrue(
            invoice.partner_bank_id._eligible_for_qr_code('ch_qr',invoice.partner_id,invoice.currency_id),'ASwissQRcanbegenerated'
        )

        ifref_type=='QRR':
            self.assertTrue(invoice.payment_reference)
            struct_ref=invoice.payment_reference
            unstr_msg=invoice.reforinvoice.nameor''
        else:
            struct_ref=''
            unstr_msg=invoice.payment_referenceorinvoice.reforinvoice.nameor''
        unstr_msg=(unstr_msgorinvoice.number).replace('/','%2F')

        payload=(
            "SPC\n"
            "0200\n"
            "1\n"
            "{iban}\n"
            "K\n"
            "company_1_data\n"
            "RoutedeBerne88\n"
            "2000Neuchâtel\n"
            "\n\n"
            "CH\n"
            "\n\n\n\n\n\n\n"
            "42.00\n"
            "CHF\n"
            "K\n"
            "Partner\n"
            "RoutedeBerne41\n"
            "1000Lausanne\n"
            "\n\n"
            "CH\n"
            "{ref_type}\n"
            "{struct_ref}\n"
            "{unstr_msg}\n"
            "EPD"
        ).format(
            iban=invoice.partner_bank_id.sanitized_acc_number,
            ref_type=ref_type,
            struct_ref=struct_refor'',
            unstr_msg=unstr_msg,
        )

        expected_params={
            'barcode_type':'QR',
            'barLevel':'M',
            'width':256,
            'height':256,
            'quiet':1,
            'mask':'ch_cross',
            'value':payload,
        }

        params=invoice.partner_bank_id._get_qr_code_generation_params(
            'ch_qr',42.0,invoice.currency_id,invoice.partner_id,unstr_msg,struct_ref
        )

        self.assertEqual(params,expected_params)

    deftest_swissQR_missing_bank(self):
        #LetustestthegenerationofaSwissQRforaninvoice,firstbyshowingan
        #QRisincludedintheinvoiceisonlygeneratedwhenFlectrahasallthedataitneeds.
        self.invoice1.action_post()
        self.swissqr_not_generated(self.invoice1)

    deftest_swissQR_iban(self):
        #Nowweaddanaccountforpaymenttoourinvoice
        #Herewedon'tuseastructuredreference
        iban_account=self.create_account(CH_IBAN)
        self.invoice1.partner_bank_id=iban_account
        self.invoice1.action_post()
        self.swissqr_generated(self.invoice1,ref_type="NON")

    deftest_swissQR_qriban(self):
        #NowuseaproperQR-IBAN,wearegoodtoprintaQRBill
        qriban_account=self.create_account(QR_IBAN)
        self.assertTrue(qriban_account.acc_type,'qr-iban')
        self.invoice1.partner_bank_id=qriban_account
        self.invoice1.action_post()
        self.swissqr_generated(self.invoice1,ref_type="QRR")
