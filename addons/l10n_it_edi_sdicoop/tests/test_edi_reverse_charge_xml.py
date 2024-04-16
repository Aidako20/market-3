#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromcollectionsimportnamedtuple
fromlxmlimportetree

fromflectraimportfields
fromflectra.testsimporttagged
fromflectra.addons.l10n_it_edi_sdicoop.tests.test_edi_xmlimportTestItEdi


@tagged('post_install_l10n','post_install','-at_install')
classTestItEdiReverseCharge(TestItEdi):

    @classmethod
    defsetUpClass(cls):
        super().setUpClass()

        #Helperfunctions-----------
        defget_tag_ids(tag_codes):
            """Helperfunctiontodefinetagidsfortaxes"""
            returncls.env['account.account.tag'].search([
                ('applicability','=','taxes'),
                ('country_id.code','=','IT'),
                ('name','in',tag_codes)]).ids

        RepartitionLine=namedtuple('Line','factor_percentrepartition_typetag_ids')
        defrepartition_lines(*lines):
            """Helperfunctiontodefinerepartitionlinesintaxes"""
            return[(5,0,0)]+[(0,0,{**line._asdict(),'tag_ids':get_tag_ids(line[2])})forlineinlines]

        ProductLine=namedtuple('Line','datanameproduct_id')
        defproduct_lines(*lines):
            """Helperfunctiontodefinemovelinesbasedonaproduct"""
            return[(0,0,{**line[0],'name':line[1],'product_id':line[2]})forlineinlines]

        #Company-----------
        cls.company.partner_id.l10n_it_pa_index="0803HR0"

        #Partner-----------
        cls.french_partner=cls.env['res.partner'].create({
            'name':'Alessi',
            'vat':'FR15437982937',
            'country_id':cls.env.ref('base.fr').id,
            'street':'AvenueTestrue',
            'zip':'84000',
            'city':'Avignon',
            'is_company':True
        })

        #Taxes-----------
        tax_data={
            'name':'Tax4%(Goods)ReverseCharge',
            'amount':4.0,
            'amount_type':'percent',
            'type_tax_use':'purchase',
            'invoice_repartition_line_ids':repartition_lines(
                RepartitionLine(100,'base',('+03','+vj9')),
                RepartitionLine(100,'tax',('+5v',)),
                RepartitionLine(-100,'tax',('-4v',))),
            'refund_repartition_line_ids':repartition_lines(
                RepartitionLine(100,'base',('-03','-vj9')),
                RepartitionLine(100,'tax',False),
                RepartitionLine(-100,'tax',False)),
        }
        #Purchasetax4%withReverseCharge
        cls.purchase_tax_4p=cls.env['account.tax'].with_company(cls.company).create(tax_data)
        cls.line_tax_4p=cls.standard_line.copy()
        cls.line_tax_4p['tax_ids']=[(6,0,cls.purchase_tax_4p.ids)]

        #Purchasetax4%withReverseCharge,targetingthetaxgridforimportofgoods
        #alreadyinItalyinaVATdeposit
        tax_data_4p_already_in_italy={
            **tax_data,
            'name':'Tax4%purchaseReverseCharge,inItaly',
            'invoice_repartition_line_ids':repartition_lines(
                RepartitionLine(100,'base',('+03','+vj3')),
                RepartitionLine(100,'tax',('+5v',)),
                RepartitionLine(-100,'tax',('-4v',))),
            'refund_repartition_line_ids':repartition_lines(
                RepartitionLine(100,'base',('-03','-vj3')),
                RepartitionLine(100,'tax',False),
                RepartitionLine(-100,'tax',False)),
        }

        cls.purchase_tax_4p_already_in_italy=cls.env['account.tax'].with_company(cls.company).create(tax_data_4p_already_in_italy)
        cls.line_tax_4p_already_in_italy=cls.standard_line.copy()
        cls.line_tax_4p_already_in_italy['tax_ids']=[(6,0,cls.purchase_tax_4p_already_in_italy.ids)]

        #Purchasetax22%withReverseCharge
        tax_data_22p={**tax_data,'name':'Tax22%purchaseReverseCharge','amount':22.0}
        cls.purchase_tax_22p=cls.env['account.tax'].with_company(cls.company).create(tax_data_22p)
        cls.line_tax_22p=cls.standard_line.copy()
        cls.line_tax_22p['tax_ids']=[(6,0,cls.purchase_tax_22p.ids)]

        #Exporttax0%
        tax_data_0v={**tax_data,"type_tax_use":"sale","amount":0}
        cls.sale_tax_0v=cls.env['account.tax'].with_company(cls.company).create(tax_data_0v)
        cls.line_tax_sale=cls.standard_line.copy()
        cls.line_tax_sale['tax_ids']=[(6,0,cls.sale_tax_0v.ids)]

        #Products-----------
        #ProductAwith0%saleexportandtax4%reversecargepurchasetax
        product_a=cls.env['product.product'].with_company(cls.company).create({
            'name':'product_a',
            'lst_price':1000.0,
            'standard_price':800.0,
            'type':'consu',
            'taxes_id':[(6,0,cls.sale_tax_0v.ids)],
            'supplier_taxes_id':[(6,0,cls.purchase_tax_4p.ids)],
        })
        #ProductBwith0%saleexportandtax4%reversechargepurchasetax
        product_b=cls.env['product.product'].with_company(cls.company).create({
            'name':'product_b',
            'lst_price':1000.0,
            'standard_price':800.0,
            'type':'consu',
            'taxes_id':[(6,0,cls.sale_tax_0v.ids)],
            'supplier_taxes_id':[(6,0,cls.purchase_tax_4p.ids)],
        })

        #Moves-----------
        #Exportinvoice
        cls.reverse_charge_invoice=cls.env['account.move'].with_company(cls.company).create({
            'company_id':cls.company.id,
            'move_type':'out_invoice',
            'invoice_date':fields.Date.from_string('2022-03-24'),
            'partner_id':cls.french_partner.id,
            'partner_bank_id':cls.test_bank.id,
            'invoice_line_ids':product_lines(
                ProductLine(cls.line_tax_sale,'ProductA',product_a.id),
                ProductLine(cls.line_tax_sale,'ProductB',product_b.id)
            ),
        })

        #Importbill#1
        bill_data={
            'company_id':cls.company.id,
            'move_type':'in_invoice',
            'invoice_date':fields.Date.from_string('2022-03-24'),
            'partner_id':cls.french_partner.id,
            'partner_bank_id':cls.test_bank.id,
            'invoice_line_ids':product_lines(
                ProductLine(cls.line_tax_22p,'ProductA',product_a.id),
                ProductLine(cls.line_tax_4p,'ProductB,taxed4%',product_b.id)
            )
        }
        cls.reverse_charge_bill=cls.env['account.move'].with_company(cls.company).create(bill_data)

        #Importbill#2
        bill_data_2={
            **bill_data,
            'invoice_line_ids':product_lines(
                ProductLine(cls.line_tax_22p,'ProductA',product_a.id),
                ProductLine(cls.line_tax_4p_already_in_italy,'ProductB,taxed4%AlreadyinItaly',product_b.id),
            ),
        }
        cls.reverse_charge_bill_2=cls.env['account.move'].with_company(cls.company).create(bill_data_2)
        cls.reverse_charge_refund=cls.reverse_charge_bill.with_company(cls.company)._reverse_moves([{
            'invoice_date':fields.Date.from_string('2022-03-24'),
        }])

        #Postingmoves-----------
        cls.reverse_charge_invoice._post()
        cls.reverse_charge_bill._post()
        cls.reverse_charge_bill_2._post()
        cls.reverse_charge_refund._post()

    def_cleanup_etree(self,content,xpaths=None):
        xpaths={
            **(xpathsor{}),
            '//FatturaElettronicaBody/Allegati':'Allegati',
            '//DatiTrasmissione/ProgressivoInvio':'ProgressivoInvio',
        }
        returnself.with_applied_xpath(
            etree.fromstring(content),
            "".join([f"<xpathexpr='{x}'position='replace'>{y}</xpath>"forx,yinxpaths.items()])
        )

    def_test_invoice_with_sample_file(self,invoice,filename,xpaths_file=None,xpaths_result=None):
        result=self._cleanup_etree(invoice._export_as_xml(),xpaths_result)
        expected=self._cleanup_etree(self._get_test_file_content(filename),xpaths_file)
        self.assertXmlTreeEqual(result,expected)

    deftest_reverse_charge_invoice(self):
        self._test_invoice_with_sample_file(self.reverse_charge_invoice,"reverse_charge_invoice.xml")

    deftest_reverse_charge_bill(self):
        self._test_invoice_with_sample_file(self.reverse_charge_bill,"reverse_charge_bill.xml")

    deftest_reverse_charge_bill_2(self):
        self._test_invoice_with_sample_file(
            self.reverse_charge_bill_2,
            "reverse_charge_bill.xml",
            xpaths_result={
                "//DatiGeneraliDocumento/Numero":"<Numero/>",
                "(//DettaglioLinee/Descrizione)[2]":"<Descrizione/>",
            },
            xpaths_file={
                "//DatiGeneraliDocumento/TipoDocumento":"<TipoDocumento>TD19</TipoDocumento>",
                "//DatiGeneraliDocumento/Numero":"<Numero/>",
                "(//DettaglioLinee/Descrizione)[2]":"<Descrizione/>",
            }
        )

    deftest_reverse_charge_refund(self):
        self._test_invoice_with_sample_file(
            self.reverse_charge_refund,
            "reverse_charge_bill.xml",
            xpaths_result={
                "//DatiGeneraliDocumento/Numero":"<Numero/>",
                "//DatiPagamento/DettaglioPagamento/DataScadenzaPagamento":"<DataScadenzaPagamento/>",
            },
            xpaths_file={
                "//DatiGeneraliDocumento/Numero":"<Numero/>",
                "//DatiGeneraliDocumento/ImportoTotaleDocumento":"<ImportoTotaleDocumento>-1808.91</ImportoTotaleDocumento>",
                "//DatiPagamento/DettaglioPagamento/DataScadenzaPagamento":"<DataScadenzaPagamento/>",
                "(//DettaglioLinee/PrezzoUnitario)[1]":"<PrezzoUnitario>-800.400000</PrezzoUnitario>",
                "(//DettaglioLinee/PrezzoUnitario)[2]":"<PrezzoUnitario>-800.400000</PrezzoUnitario>",
                "(//DettaglioLinee/PrezzoTotale)[1]":"<PrezzoTotale>-800.40</PrezzoTotale>",
                "(//DettaglioLinee/PrezzoTotale)[2]":"<PrezzoTotale>-800.40</PrezzoTotale>",
                "(//DatiRiepilogo/ImponibileImporto)[1]":"<ImponibileImporto>-800.40</ImponibileImporto>",
                "(//DatiRiepilogo/ImponibileImporto)[2]":"<ImponibileImporto>-800.40</ImponibileImporto>",
                "(//DatiRiepilogo/Imposta)[1]":"<Imposta>-176.09</Imposta>",
                "(//DatiRiepilogo/Imposta)[2]":"<Imposta>-32.02</Imposta>",
            }
        )
