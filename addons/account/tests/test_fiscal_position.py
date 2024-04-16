#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.testsimportcommon


classTestFiscalPosition(common.SavepointCase):
    """Testsforfiscalpositionsinautoapply(account.fiscal.position).
    Ifapartnerhasavatnumber,thefiscalpositionswith"vat_required=True"
    arepreferred.
    """

    @classmethod
    defsetUpClass(cls):
        super(TestFiscalPosition,cls).setUpClass()
        cls.fp=cls.env['account.fiscal.position']

        #resetanyexistingFP
        cls.fp.search([]).write({'auto_apply':False})

        cls.res_partner=cls.env['res.partner']
        cls.be=be=cls.env.ref('base.be')
        cls.fr=fr=cls.env.ref('base.fr')
        cls.mx=mx=cls.env.ref('base.mx')
        cls.eu=cls.env.ref('base.europe')
        cls.nl=cls.env.ref('base.nl')
        cls.us=cls.env.ref('base.us')
        cls.state_fr=cls.env['res.country.state'].create(dict(
                                           name="State",
                                           code="ST",
                                           country_id=fr.id))
        cls.jc=cls.res_partner.create(dict(
                                           name="JCVD",
                                           vat="BE0477472701",
                                           country_id=be.id))
        cls.ben=cls.res_partner.create(dict(
                                           name="BP",
                                           country_id=be.id))
        cls.george=cls.res_partner.create(dict(
                                           name="George",
                                           vat="BE0477472701",
                                           country_id=fr.id))
        cls.alberto=cls.res_partner.create(dict(
                                           name="Alberto",
                                           vat="BE0477472701",
                                           country_id=mx.id))
        cls.be_nat=cls.fp.create(dict(
                                         name="BE-NAT",
                                         auto_apply=True,
                                         country_id=be.id,
                                         vat_required=False,
                                         sequence=10))
        cls.fr_b2c=cls.fp.create(dict(
                                         name="EU-VAT-FR-B2C",
                                         auto_apply=True,
                                         country_id=fr.id,
                                         vat_required=False,
                                         sequence=40))
        cls.fr_b2b=cls.fp.create(dict(
                                         name="EU-VAT-FR-B2B",
                                         auto_apply=True,
                                         country_id=fr.id,
                                         vat_required=True,
                                         sequence=50))

    deftest_10_fp_country(self):
        defassert_fp(partner,expected_pos,message):
            self.assertEqual(
                self.fp.get_fiscal_position(partner.id).id,
                expected_pos.id,
                message)

        george,jc,ben,alberto=self.george,self.jc,self.ben,self.alberto

        #B2BhasprecedenceoverB2Cforsamecountryevenwhensequencegiveslowerprecedence
        self.assertGreater(self.fr_b2b.sequence,self.fr_b2c.sequence)
        assert_fp(george,self.fr_b2b,"FR-B2BshouldhaveprecedenceoverFR-B2C")
        self.fr_b2b.auto_apply=False
        assert_fp(george,self.fr_b2c,"FR-B2Cshouldmatchnow")
        self.fr_b2b.auto_apply=True

        #CreatepositionsmatchingonCountryGroupandonNOcountryatall
        self.eu_intra_b2b=self.fp.create(dict(
                                         name="EU-INTRAB2B",
                                         auto_apply=True,
                                         country_group_id=self.eu.id,
                                         vat_required=True,
                                         sequence=20))
        self.world=self.fp.create(dict(
                                         name="WORLD-EXTRA",
                                         auto_apply=True,
                                         vat_required=False,
                                         sequence=30))

        #Countrymatchhashigherprecedencethangroupmatchorsequence
        self.assertGreater(self.fr_b2b.sequence,self.eu_intra_b2b.sequence)
        assert_fp(george,self.fr_b2b,"FR-B2BshouldhaveprecedenceoverEU-INTRAB2B")

        #B2Bhasprecedenceregardlessofcountryorgroupmatch
        self.assertGreater(self.eu_intra_b2b.sequence,self.be_nat.sequence)
        assert_fp(jc,self.eu_intra_b2b,"EU-INTRAB2BshouldmatchbeforeBE-NAT")

        #Lowersequence=higherprecedenceifcountry/groupandVATmatches
        self.assertFalse(ben.vat)#NoVATset
        assert_fp(ben,self.be_nat,"BE-NATshouldmatchbeforeEU-INTRAduetolowersequence")

        #RemoveBEfromEUgroup,nowBE-NATshouldbethefallbackmatchbeforethewildcardWORLD
        self.be.write({'country_group_ids':[(3,self.eu.id)]})
        self.assertTrue(jc.vat)#VATset
        assert_fp(jc,self.be_nat,"BE-NATshouldmatchasfallbackevenw/oVATmatch")

        #Nocountry=wildcardmatchonlyifnothingelsematches
        self.assertTrue(alberto.vat)#withVAT
        assert_fp(alberto,self.world,"WORLD-EXTRAshouldmatchanythingelse(1)")
        alberto.vat=False         #orwithout
        assert_fp(alberto,self.world,"WORLD-EXTRAshouldmatchanythingelse(2)")

        #Ziprange
        self.fr_b2b_zip100=self.fr_b2b.copy(dict(zip_from=0,zip_to=5000,sequence=60))
        george.zip=6000
        assert_fp(george,self.fr_b2b,"FR-B2Bwithwrongziprangeshouldnotmatch")
        george.zip=3000
        assert_fp(george,self.fr_b2b_zip100,"FR-B2Bwithziprangeshouldhaveprecedence")

        #States
        self.fr_b2b_state=self.fr_b2b.copy(dict(state_ids=[(4,self.state_fr.id)],sequence=70))
        george.state_id=self.state_fr
        assert_fp(george,self.fr_b2b_zip100,"FR-B2Bwithzipshouldhaveprecedenceoverstates")
        george.zip=False
        assert_fp(george,self.fr_b2b_state,"FR-B2Bwithstatesshouldhaveprecedence")

        #Dedicatedpositionhasmaxprecedence
        george.property_account_position_id=self.be_nat
        assert_fp(george,self.be_nat,"Forcedpositionhasmaxprecedence")


    deftest_20_fp_one_tax_2m(self):

        self.src_tax=self.env['account.tax'].create({'name':"SRC",'amount':0.0})
        self.dst1_tax=self.env['account.tax'].create({'name':"DST1",'amount':0.0})
        self.dst2_tax=self.env['account.tax'].create({'name':"DST2",'amount':0.0})

        self.fp2m=self.fp.create({
            'name':"FP-TAX2TAXES",
            'tax_ids':[
                (0,0,{
                    'tax_src_id':self.src_tax.id,
                    'tax_dest_id':self.dst1_tax.id
                }),
                (0,0,{
                    'tax_src_id':self.src_tax.id,
                    'tax_dest_id':self.dst2_tax.id
                })
            ]
        })
        mapped_taxes=self.fp2m.map_tax(self.src_tax)

        self.assertEqual(mapped_taxes,self.dst1_tax|self.dst2_tax)

    deftest_20_fp_one_tax_2none(self):
        src_tax=self.env['account.tax'].create({'name':"SRC",'amount':0.0})

        fp2m=self.fp.create({
            'name':"FP-TAX2NONE",
            'tax_ids':[
                (0,0,{
                    'tax_src_id':src_tax.id,
                }),
            ]
        })
        mapped_taxes=fp2m.map_tax(src_tax)

        self.assertEqual(mapped_taxes,self.env['account.tax'])

    deftest_30_fp_delivery_address(self):
        #MakesurethebillingcompanyisfromBelgium(withintheEU)
        self.env.company.vat='BE0477472701'
        self.env.company.country_id=self.be

        #ResetanyexistingFP
        self.env['account.fiscal.position'].search([]).auto_apply=False

        #Createthefiscalpositions
        fp_be_nat=self.env['account.fiscal.position'].create({
            'name':'RégimeNational',
            'auto_apply':True,
            'country_id':self.be.id,
            'vat_required':True,
            'sequence':10,
        })
        fp_eu_priv=self.env['account.fiscal.position'].create({
            'name':'EUprivé',
            'auto_apply':True,
            'country_group_id':self.eu.id,
            'vat_required':False,
            'sequence':20,
        })
        fp_eu_intra=self.env['account.fiscal.position'].create({
            'name':'RégimeIntra-Communautaire',
            'auto_apply':True,
            'country_group_id':self.eu.id,
            'vat_required':True,
            'sequence':30,
        })
        fp_eu_extra=self.env['account.fiscal.position'].create({
            'name':'RégimeExtra-Communautaire',
            'auto_apply':True,
            'vat_required':False,
            'sequence':40,
        })

        #Createthepartners
        partner_be_vat=self.env['res.partner'].create({
            'name':'BEVAT',
            'vat':'BE0477472701',
            'country_id':self.be.id,
        })
        partner_nl_vat=self.env['res.partner'].create({
            'name':'NLVAT',
            'vat':'NL123456782B90',
            'country_id':self.nl.id,
        })
        partner_nl_no_vat=self.env['res.partner'].create({
            'name':'NLNOVAT',
            'country_id':self.nl.id,
        })
        partner_us_no_vat=self.env['res.partner'].create({
            'name':'USNOVAT',
            'country_id':self.us.id,
        })

        #Case:1
        #Billing(VAT/country):BE/BE
        #Delivery(VAT/country):NL/NL
        #ExpectedFP:RégimeNational
        self.assertEqual(
            self.env['account.fiscal.position'].get_fiscal_position(partner_be_vat.id,partner_nl_vat.id),
            fp_be_nat
        )

        #Case:2
        #Billing(VAT/country):NL/NL
        #Delivery(VAT/country):BE/BE
        #ExpectedFP:RégimeNational
        self.assertEqual(
            self.env['account.fiscal.position'].get_fiscal_position(partner_nl_vat.id,partner_be_vat.id),
            fp_be_nat
        )

        #Case:3
        #Billing(VAT/country):BE/BE
        #Delivery(VAT/country):None/NL
        #ExpectedFP:RégimeNational
        self.assertEqual(
            self.env['account.fiscal.position'].get_fiscal_position(partner_be_vat.id,partner_nl_no_vat.id),
            fp_be_nat
        )

        #Case:4
        #Billing(VAT/country):NL/NL
        #Delivery(VAT/country):NL/NL
        #ExpectedFP:RégimeIntra-Communautaire
        self.assertEqual(
            self.env['account.fiscal.position'].get_fiscal_position(partner_nl_vat.id,partner_nl_vat.id),
            fp_eu_intra
        )

        #Case:5
        #Billing(VAT/country):None/NL
        #Delivery(VAT/country):None/NL
        #ExpectedFP:EUprivé
        self.assertEqual(
            self.env['account.fiscal.position'].get_fiscal_position(partner_nl_no_vat.id,partner_nl_no_vat.id),
            fp_eu_priv
        )

        #Case:6
        #Billing(VAT/country):None/US
        #Delivery(VAT/country):None/US
        #ExpectedFP:RégimeExtra-Communautaire
        self.assertEqual(
            self.env['account.fiscal.position'].get_fiscal_position(partner_us_no_vat.id,partner_us_no_vat.id),
            fp_eu_extra
        )
