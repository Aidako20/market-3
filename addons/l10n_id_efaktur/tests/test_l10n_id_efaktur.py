fromflectra.testsimporttagged,common
fromflectra.addons.l10n_id_efaktur.models.account_moveimportFK_HEAD_LIST,LT_HEAD_LIST,OF_HEAD_LIST,_csv_row

@tagged('post_install','-at_install')
classTestIndonesianEfaktur(common.TransactionCase):
    defsetUp(self):
        """
        1)contactwithl10n_id_pkp=True,l10n_id_kode_transaksi="01"
        2)tax:amount=10,type_tax_use=sale,price_include=True
        3)invoicewithpartner_id=contact,journal=customerinvoices,
        """
        super().setUp()

        self.maxDiff=1500
        #changecompanyinfoforcsvdetailater
        self.env.company.country_id=self.env.ref('base.id')
        self.env.company.street="test"
        self.env.company.phone="12345"

        self.partner_id=self.env['res.partner'].create({"name":"l10ntest","l10n_id_pkp":True,"l10n_id_kode_transaksi":"01","l10n_id_nik":"12345"})
        self.tax_id=self.env['account.tax'].create({"name":"testtax","type_tax_use":"sale","amount":10.0,"price_include":True})

        self.efaktur=self.env['l10n_id_efaktur.efaktur.range'].create({'min':'0000000000001','max':'0000000000010'})
        self.out_invoice_1=self.env['account.move'].create({
            'type':'out_invoice',
            'partner_id':self.partner_id.id,
            'invoice_date':'2019-05-01',
            'date':'2019-05-01',
            'invoice_line_ids':[
                (0,0,{'name':'line1','price_unit':110.0,'tax_ids':self.tax_id.ids}),
            ],
            'l10n_id_kode_transaksi':"01",
        })
        self.out_invoice_1.post()

        self.out_invoice_2=self.env['account.move'].create({
            'type':'out_invoice',
            'partner_id':self.partner_id.id,
            'invoice_date':'2019-05-01',
            'date':'2019-05-01',
            'invoice_line_ids':[
                (0,0,{'name':'line1','price_unit':110.11,'quantity':400,'tax_ids':self.tax_id.ids})
            ],
            'l10n_id_kode_transaksi':'01'
        })
        self.out_invoice_2.post()

    deftest_efaktur_csv_output_1(self):
        """
        Testtoensurethattheoutputcsvdatacontainstax-excludedpricesregardlessofwhetherthetaxconfigurationistax-includedortax-excluded.
        Currenttestisusingpriceof110whichistax-includedwithtaxofamount10%.Sotheunitpricelistedhastobe100whereastheoriginalresultwouldhave110instead.
        """
        #tocheckthediffwhentestfails

        efaktur_csv_output=self.out_invoice_1._generate_efaktur_invoice(',')
        output_head='%s%s%s'%(
            _csv_row(FK_HEAD_LIST,','),
            _csv_row(LT_HEAD_LIST,','),
            _csv_row(OF_HEAD_LIST,','),
        )
        #remaininglines
        line_4='"FK","01","0","0000000000001","5","2019","1/5/2019","12345","l10ntest","","100","10","0","","0","110","0","0","INV/2019/000112345","0"\n'
        line_5='"FAPR","000000000000000","YourCompany","test","","","","","","","","","","12345"\n'
        line_6='"OF","","","100","1.0","100","0","100","10","0","0"\n'

        efaktur_csv_expected=output_head+line_4+line_5+line_6

        self.assertEqual(efaktur_csv_expected,efaktur_csv_output)

    deftest_efaktur_csv_output_decimal_place(self):
        """
        Testtoensurethatdecimalplaceconversionisonlydonewheninputtingtocsv
        Thisistotestoriginalcalculationofinvoice_line_total_price:invoice_line_total_price=invoice_line_unit_price*line.quantity
        asinvoice_line_unit_priceisalreadyconvertedtobetax-excludedandsettothedecimalplaceasconfiguredonthecurrency,thecalculationoftotalcouldbeflawed.

        Inthistestcase,thetax-includedpriceunitis110.11,hencetax-excludedis100.1,
        invoice_line_unit_pricewillbe100,ifwecontinuewiththecalculationoftotalprice,itwillbe100*400=40000
        eventhoughthetotalissupposedtobe100.1*400=40040,thereisa40discrepancy
        """
        efaktur_csv_output=self.out_invoice_2._generate_efaktur_invoice(',')
        output_head='%s%s%s'%(
            _csv_row(FK_HEAD_LIST,','),
            _csv_row(LT_HEAD_LIST,','),
            _csv_row(OF_HEAD_LIST,','),
        )
        line_4='"FK","01","0","0000000000002","5","2019","1/5/2019","12345","l10ntest","","40040","4004","0","","0","44044","0","0","INV/2019/000212345","0"\n'
        line_5='"FAPR","000000000000000","YourCompany","test","","","","","","","","","","12345"\n'
        line_6='"OF","","","100","400.0","40040","0","40040","4004","0","0"\n'

        efaktur_csv_expected=output_head+line_4+line_5+line_6
        self.assertEqual(efaktur_csv_expected,efaktur_csv_output)
