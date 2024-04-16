#-*-coding:utf-8-*-
importbase64

fromfreezegunimportfreeze_time

fromflectra.addons.account_edi.tests.commonimportAccountEdiTestCommon
fromflectraimportfields
fromflectra.modules.moduleimportget_resource_path
fromflectra.testsimporttagged
fromflectra.toolsimportfloat_round

fromlxmlimportetree


@tagged('post_install_l10n','post_install','-at_install')
classTestUBLCommon(AccountEdiTestCommon):

    @classmethod
    defsetUpClass(cls,chart_template_ref=None,edi_format_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref,edi_format_ref=edi_format_ref)

        #EnsurethetestingcurrencyisusingavalidISOcode.
        real_usd=cls.env.ref('base.USD')
        real_usd.name='FUSD'
        real_usd.flush(['name'])
        cls.currency_data['currency'].name='USD'

        #removethistax,otherwise,atimport,thistaxwithchildrentaxescanbeselectedandthetotaliswrong
        cls.tax_armageddon.children_tax_ids.unlink()
        cls.tax_armageddon.unlink()

        #FixedTaxes
        cls.recupel=cls.env['account.tax'].create({
            'name':"RECUPEL",
            'amount_type':'fixed',
            'amount':1,
            'include_base_amount':True,
            'sequence':1,
        })
        cls.auvibel=cls.env['account.tax'].create({
            'name':"AUVIBEL",
            'amount_type':'fixed',
            'amount':1,
            'include_base_amount':True,
            'sequence':2,
        })

    @classmethod
    defsetup_company_data(cls,company_name,chart_template=None,**kwargs):
        #OVERRIDEtoforcethecompanywithEURcurrency.
        eur=cls.env.ref('base.EUR')
        ifnoteur.active:
            eur.active=True

        res=super().setup_company_data(company_name,chart_template=chart_template,**kwargs)
        res['company'].currency_id=eur
        returnres

    defassert_same_invoice(self,invoice1,invoice2,**invoice_kwargs):
        self.assertEqual(len(invoice1.invoice_line_ids),len(invoice2.invoice_line_ids))
        self.assertRecordValues(invoice2,[{
            'partner_id':invoice1.partner_id.id,
            'invoice_date':fields.Date.from_string(invoice1.date),
            'currency_id':invoice1.currency_id.id,
            'amount_untaxed':invoice1.amount_untaxed,
            'amount_tax':invoice1.amount_tax,
            'amount_total':invoice1.amount_total,
            **invoice_kwargs,
        }])

        default_invoice_line_kwargs_list=[{}]*len(invoice1.invoice_line_ids)
        invoice_line_kwargs_list=invoice_kwargs.get('invoice_line_ids',default_invoice_line_kwargs_list)
        self.assertRecordValues(invoice2.invoice_line_ids,[{
            'quantity':line.quantity,
            'price_unit':line.price_unit,
            'discount':line.discount,
            'product_id':line.product_id.id,
            'product_uom_id':line.product_uom_id.id,
            **invoice_line_kwargs,
        }forline,invoice_line_kwargsinzip(invoice1.invoice_line_ids,invoice_line_kwargs_list)])

    #-------------------------------------------------------------------------
    #IMPORTHELPERS
    #-------------------------------------------------------------------------

    @freeze_time('2017-01-01')
    def_assert_imported_invoice_from_etree(self,invoice,xml_etree,xml_filename):
        """
        Createanaccount.movedirectlyfromanxmlfile,assertstheinvoiceobtainedisthesameastheexpected
        invoice.
        """
        new_invoice=self.edi_format._create_invoice_from_xml_tree(
            xml_filename,
            xml_etree,
            #/!\usethesamejournalastheinvoice'sonetoimportthexml!
            invoice.journal_id,
        )

        self.assertTrue(new_invoice)
        self.assert_same_invoice(invoice,new_invoice)

    def_assert_imported_invoice_from_file(self,subfolder,filename,amount_total,amount_tax,list_line_subtotals,
                                           list_line_price_unit=None,list_line_discount=None,list_line_taxes=None,
                                           move_type='in_invoice',currency_id=None):
        """
        Createanemptyaccount.move,updatethefiletofillitsfields,assertsthecurrency,totalandtaxamounts
        areasexpected.
        """
        ifnotcurrency_id:
            currency_id=self.env.ref('base.EUR').id

        #Createemptyaccount.move,thenupdateafile
        ifmove_type=='in_invoice':
            invoice=self._create_empty_vendor_bill()
        elifmove_type=='out_invoice':
            invoice=self.env['account.move'].create({
                'move_type':move_type,
                'journal_id':self.company_data['default_journal_sale'].id,
            })
        else:
            invoice=self.env['account.move'].create({
                'move_type':move_type,
                'journal_id':self.company_data['default_journal_purchase'].id,
            })
        invoice_count=len(self.env['account.move'].search([]))

        #Importthefiletofilltheemptyinvoice
        self.update_invoice_from_file('l10n_account_edi_ubl_cii_tests',subfolder,filename,invoice)

        #Checks
        self.assertEqual(len(self.env['account.move'].search([])),invoice_count)
        self.assertRecordValues(invoice,[{
            'amount_total':amount_total,
            'amount_tax':amount_tax,
            'currency_id':currency_id,
        }])
        iflist_line_price_unit:
            self.assertEqual(invoice.invoice_line_ids.mapped('price_unit'),list_line_price_unit)
        iflist_line_discount:
            dp=self.env['decimal.precision'].precision_get("Discount")
            self.assertListEqual([float_round(line.discount,precision_digits=dp)forlineininvoice.invoice_line_ids],list_line_discount)
        iflist_line_taxes:
            forline,taxesinzip(invoice.invoice_line_ids,list_line_taxes):
                self.assertEqual(line.tax_ids,taxes)
        self.assertEqual(invoice.invoice_line_ids.mapped('price_subtotal'),list_line_subtotals)

    #-------------------------------------------------------------------------
    #EXPORTHELPERS
    #-------------------------------------------------------------------------

    @freeze_time('2017-01-01')
    def_generate_move(self,seller,buyer,**invoice_kwargs):
        """
        Createandpostanaccount.move.
        """
        #Setuptheseller.
        self.env.company.write({
            'partner_id':seller.id,
            'name':seller.name,
            'street':seller.street,
            'zip':seller.zip,
            'city':seller.city,
            'vat':seller.vat,
            'country_id':seller.country_id.id,
        })

        move_type=invoice_kwargs['move_type']
        account_move=self.env['account.move'].create({
            'partner_id':buyer.id,
            'partner_bank_id':(sellerifmove_type=='out_invoice'elsebuyer).bank_ids[:1].id,
            'invoice_payment_term_id':self.pay_terms_b.id,
            'invoice_date':'2017-01-01',
            'date':'2017-01-01',
            'currency_id':self.currency_data['currency'].id,
            'narration':'testnarration',
            'ref':'ref_move',
            **invoice_kwargs,
            'invoice_line_ids':[
                (0,0,{
                    'sequence':i,
                    **invoice_line_kwargs,
                })
                fori,invoice_line_kwargsinenumerate(invoice_kwargs.get('invoice_line_ids',[]))
            ],
        })
        #thisisneededforformatsnotenabledbydefaultonthejournal
        account_move.journal_id.edi_format_ids+=self.edi_format
        account_move.action_post()
        returnaccount_move

    def_assert_invoice_attachment(self,invoice,xpaths,expected_file):
        """
        Getattachmentfromapostedaccount.move,andassertsit'sthesameastheexpectedxmlfile.
        """
        attachment=invoice._get_edi_attachment(self.edi_format)
        self.assertTrue(attachment)
        xml_filename=attachment.name
        xml_content=base64.b64decode(attachment.with_context(bin_size=False).datas)
        xml_etree=self.get_xml_tree_from_string(xml_content)

        expected_file_path=get_resource_path('l10n_account_edi_ubl_cii_tests','tests/test_files',expected_file)
        expected_etree=etree.parse(expected_file_path).getroot()

        modified_etree=self.with_applied_xpath(
            expected_etree,
            xpaths
        )

        self.assertXmlTreeEqual(
            xml_etree,
            modified_etree,
        )

        returnxml_etree,xml_filename

    def_import_invoice_attachment(self,invoice,edi_code,journal):
        """Extracttheattachmentfromtheinvoiceandimportitonthegivenjournal.
        """
        #Gettheattachmentfromtheinvoice
        edi_attachment=invoice.edi_document_ids.filtered(
            lambdadoc:doc.edi_format_id.code==edi_code).attachment_id
        edi_etree=self.get_xml_tree_from_string(edi_attachment.raw)

        #importtheattachmentandreturntheresultinginvoice
        returnself.edi_format._create_invoice_from_xml_tree(
            filename='test_filename',
            tree=edi_etree,
            journal=journal,
        )

    def_test_encoding_in_attachment(self,edi_code,filename):
        """
        Generateaninvoice,assertthatthetag'<?xmlversion='1.0'encoding='UTF-8'?>'ispresentintheattachment
        """
        invoice=self._generate_move(
            seller=self.partner_1,
            buyer=self.partner_2,
            move_type='out_invoice',
            invoice_line_ids=[{'product_id':self.product_a.id}],
        )
        edi_attachment=invoice.edi_document_ids.filtered(
            lambdadoc:doc.edi_format_id.code==edi_code).attachment_id
        self.assertEqual(edi_attachment.name,filename)
        self.assertIn(b"<?xmlversion='1.0'encoding='UTF-8'?>",edi_attachment.raw)
